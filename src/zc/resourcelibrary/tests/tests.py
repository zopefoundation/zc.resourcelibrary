##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""
$Id: ntests.py 3330 2005-09-09 23:05:34Z jim $
"""
from StringIO import StringIO
from zc.resourcelibrary import resourcelibrary
from zc.resourcelibrary import publication
from zc.resourcelibrary import tal
from zope.app.testing import functional
from zope.configuration import xmlconfig
import zope.interface
from zope.pagetemplate import pagetemplate
import zope.publisher.interfaces.browser
import doctest
import os
import unittest
import zope.component.hooks
import zope.security.management


class TestFactory:

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    def __init__(self, source, checker, name):
        self.name = name
        self.__Security_checker__ = checker

    def __call__(self, request):
        return self

    def __getitem__(self, name):
        return lambda: "http://localhost/@@/%s/%s" % (self.name, name)

    def publishTraverse(self, request, name):
        return getattr(self, name.replace('.', '_'))

    def foo_js(self):
        return 'foo = 1;\n'



#### testing framework ####

def zcml(s, execute=True, clear=(), site=None):
    zope.component.hooks.setSite(site)
    for i in clear:
        del resourcelibrary.library_info[i]
    from zope.app.appsetup.appsetup import __config_context as context
    try:
        xmlconfig.string(s, context, execute=execute)
    except:
        context.end()
        raise

class TestPageTemplate(pagetemplate.PageTemplate):
    def __init__(self, view):
        self.view = view
        super(TestPageTemplate, self).__init__()

    def pt_getContext(self, *args, **kws):
        context = super(TestPageTemplate, self).pt_getContext(*args, **kws)
        context['view'] = self.view
        return context


def zpt(s, view=None, content_type=None):
    request = publication.Request(body_instream=StringIO(''), environ={})
    zope.security.management.newInteraction(request)

    # if no set has been set, try setting it the view context
    if zope.component.hooks.getSite() is None and hasattr(view, 'context'):
        zope.component.hooks.setSite(view.context)

    pt = TestPageTemplate(view)

    # if the resource library expression hasn't been registered, do so
    engine = pt.pt_getEngine()
    type_name = 'resource_library'
    if type_name not in engine.types:
        engine.registerType(type_name, tal.ResourceLibraryExpression)

    pt.write(s)
    html = pt()
    zope.security.management.endInteraction()

    if content_type:
        request.response.setHeader("Content-Type", content_type)

    if html:
        request.response.setResult(html)
        return request.response.consumeBody()

#### tests ####

def test_empty_body():
    """
    If a response body is not html, guess that it is text/plain.  This
    follows the behavior of zope.publication's trunk as of this writing.

    >>> import zc.resourcelibrary.publication
    >>> response = zc.resourcelibrary.publication.Response()
    >>> response.setResult('')
    >>> response.getHeader('content-type')
    'text/plain'
    """

#### test setup ####

ResourceLibraryFunctionalLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ResourceLibraryFunctionalLayer')

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        '../README.txt',
        'duplicate_declarations.txt',
        'localsite.txt',
        globs={'zcml': zcml, 'zpt': zpt},
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        )
    suite.layer = ResourceLibraryFunctionalLayer
    return unittest.TestSuite((
        suite,
        doctest.DocTestSuite()
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
