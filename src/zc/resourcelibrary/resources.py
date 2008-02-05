##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope import component
from zope import interface

import zope.app.appsetup.interfaces

import threading
import os
import sha

from interfaces import IResourceManager

library_info = {}

class LibraryInfo(object):
    def __init__(self):
        self.path = u""
        self.included = []
        self.required = []

class ResourceInfo(object):
    def __init__(self, path, _type, dependants=None):
        self.path = path
        self.type = _type

        if dependants is None:
            self.dependants = []
        else:
            self.dependants = dependants

        f = open(path, 'rb')

        h = sha.sha()
        
        for line in f:
            h.update(line)
            
        f.close()

        self.digest = h.digest()

    def __repr__(self):
        return '<ResourceInfo path="%s" type="%s" dependants="%s">' % \
               (self.path, self.type, self.dependants)

    def addDependant(self, name):
        self.dependants.append(name)

class ResourceBundle(object):
    def __init__(self, *resources):
        self.paths = [resource.path for resource in resources]

        assert len(resources) > 0

        self.type = resources[0].type
        self.dependants = resources[0].dependants

        h = sha.sha()
        map(h.update, (resource.digest for resource in resources))

        self.digest = h.hexdigest()

class ResourceManager(threading.local):
    """The resource manager is a utility class to manage resource bundles."""

    interface.implements(IResourceManager)
    
    def __init__(self, libraries={}):
        resources = self._unique_resources(libraries)
        bundles = self._compute_bundles(resources)

        self.by_dependant = self._by_dependant(resources, bundles)
        self.by_digest = bundles
        
    def getBundlesForLibrary(self, library_name):
        return self.by_dependant[library_name]

    def _unique_resources(self, libraries):
        """Process resources for each library:

        * Determine file type
        * Extract SHA digest

        Returned is a dict of ``ResourceInfo`` objects
        indexed by digest.

        Note: If two resources share digest (~ are equal), only one
        will be used.

          >>> linfo = LibraryInfo()
          >>> import zc.resourcelibrary
          >>> prefix = os.path.dirname(zc.resourcelibrary.__file__)
          >>> path = "/tests/example/my-lib/".replace('/', os.path.sep)
          
          >>> linfo.included = [prefix+path+"included.css",
          ...                   prefix+path+"included.js"]

          >>> manager = ResourceManager()
          >>> resources = manager._unique_resources({'my-lib': linfo})
          >>> len(resources)
          2
          >>> rinfo = resources[0]
          >>> rinfo.path # doctest: +ELLIPSIS
          '.../example/my-lib/included.js'
          >>> rinfo.dependants
          ['my-lib']

        """
        resources = {}

        for name, info in libraries.items():
            included = info.included

            for filename in included:
                filetype = os.path.splitext(filename)[-1][1:]

                if info.path:
                    filename = info.path + os.path.sep + filename
                
                rinfo = ResourceInfo(filename, type)
                    
                digest = rinfo.digest

                if digest not in resources:
                    resources[digest] = rinfo

                resources[digest].addDependant(name)

        return resources.values()

    def _compute_bundles(self, resources):
        groups = {}
        
        # group resources based on type and dependants
        for resource in resources:
            digest = resource.digest
            
            signature = tuple(sorted(resource.dependants)) + ('.%s' % resource.type,)

            if signature not in groups:
                groups[signature] = [resource]
            else:
                groups[signature].append(resource)

        bundles = {}

        for resources in groups.values():
            bundle = ResourceBundle(*resources)
            bundles[bundle.digest] = bundle

        return bundles

    def _list_dependants(self, resources):
        dependants = set()

        # maintain list of dependants
        for resource in resources:
            map(dependants.add, resource.dependants)

        return dependants

    def _by_dependant(self, resources, bundles):
        """
        We'll patch the built-in ``open`` method to define mock resources
        that do not correspond to actual files.

          >>> save_open = __builtins__['open']
          >>> class MockFile(unicode):
          ...     def close(self): pass
          >>> def mock_open(path, mode):
          ...     return MockFile(path)
          >>> __builtins__['open'] = mock_open

        Now we can define a few resources.

          >>> resources = (ResourceInfo('/path/a', 1, ['a']),
          ...              ResourceInfo('/path/aa', 1, ['a']),
          ...              ResourceInfo('/path/b', 1, ['a', 'b']),
          ...              ResourceInfo('/path/bb', 1, ['a', 'b']),
          ...              ResourceInfo('/path/c', 1, ['a', 'b', 'c']))

        Restore the ``open`` method.

          >>> __builtins__['open'] = save_open

        Now we're ready to compute the bundles per dependant:

          >>> manager = ResourceManager({})
          >>> bundles = manager._compute_bundles(resources)
          >>> by_dependant = manager._by_dependant(resources, bundles)

        Let's examine the bundles required for library 'a'. We expect
        three bundles:

          >>> bundles = by_dependant['a']
          >>> len(bundles)
          3
          >>> [bundle.paths for bundle in bundles]
          [['/path/b', '/path/bb'], ['/path/c'], ['/path/a', '/path/aa']]
          >>> [bundle.type for bundle in bundles]
          [1, 1, 1]
          >>> [bundle.digest for bundle in bundles] # doctest: +NORMALIZE_WHITESPACE
          ['7309e08f51cab77e6855288001c30c2ab9e05400',
           '2d5021510fc774edb7b698a9cd31a9059b51858e',
           '11f36f3b56dd892d7af6757c925bcecf19549af1']
        """
        
        dependants = self._list_dependants(resources)
        
        # compute bundles per library
        by_dependant = {}

        for name in dependants:
            required_bundles = []

            for digest, bundle in bundles.items():
                if name in bundle.dependants:
                    required_bundles.append(bundle)

            by_dependant[name] = required_bundles

        return by_dependant

@component.adapter(zope.app.appsetup.interfaces.IProcessStartingEvent)
def initializeResourceManager(*args):
    manager = ResourceManager(library_info)
    component.provideUtility(manager, IResourceManager)
