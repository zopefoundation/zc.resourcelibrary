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
$Id: publication.py 4528 2005-12-23 02:45:25Z gary $
"""
from zope import interface
from zope.app.publication.interfaces import IBrowserRequestFactory
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.publisher.browser import BrowserRequest, BrowserResponse
from zope.publisher.browser import isHTML
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.traversing.browser.interfaces import IAbsoluteURL

import zc.resourcelibrary
import zope.component.hooks


class Request(BrowserRequest):
    interface.classProvides(IBrowserRequestFactory)
    # __slots__ = ('resource_libraries',)

    def _createResponse(self):
        response = Response()
        self.resource_libraries = response.resource_libraries = []
        return response

    def retry(self):
        """Returns request object to be used in a retry attempt.

        In addition to BrowswerRequest's retry() the libraries are copied over
        to the new request. Otherwise it is not possible to add even new
        libraries to a retried request.

        >>> import StringIO
        >>> request = Request(StringIO.StringIO(), {})
        >>> request.resource_libraries = ['foo']
        >>> retry_request = request.retry()
        >>> retry_request is request
        False
        >>> request.resource_libraries is retry_request.resource_libraries
        True

        The assigned libraries are flushed because a new request will define
        its own set of required librarires.

        >>> request.resource_libraries
        []

        """
        request = super(Request, self).retry()
        if hasattr(self, 'resource_libraries'):
            request.resource_libraries = self.resource_libraries
            request.resource_libraries[:] = []
        return request


class Response(BrowserResponse):

    def retry(self):
        """
        Returns a response object to be used in a retry attempt.

        >>> response = Response()
        >>> response
        <zc.resourcelibrary.publication.Response object at ...>
        >>> response1 = response.retry()

        The returned object is not the same.
        >>> response1 is response
        False

        If resource_libraries are defined they are assigned to the new
        response.
        >>> rl = ['a','b','c']
        >>> response.resource_libraries = rl
        >>> response.retry().resource_libraries is rl
        True
        >>> response.retry().retry().resource_libraries is rl
        True
        """
        response = super(Response, self).retry()
        if hasattr(self, 'resource_libraries'):
            response.resource_libraries = self.resource_libraries
        return response

    def _implicitResult(self, body):
        #figure out the content type
        content_type = self.getHeader('content-type')
        if content_type is None:
            if isHTML(body):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            self.setHeader('x-content-type-warning', 'guessed from content')
            self.setHeader('content-type', content_type)

        # check the content type disregarding parameters and case
        if content_type and content_type.split(';', 1)[0].lower() in (
            'text/html', 'text/xml'):
            # act on HTML and XML content only!

            resource_libraries = self._addDependencies(self.resource_libraries)
            html = self._generateIncludes(resource_libraries)

            if html:
                # This is a pretty low-rent way of adding things to the head.
                # We should probably use a real HTML parser instead.
                marker = body.find('<!-- zc.resourcelibrary -->')
                if marker != -1:
                    body = body[:marker] + html + body[marker+27:]
                else:
                    body = body.replace('<head>', '<head>\n    %s\n' %
                                        html, 1)

        return super(Response, self)._implicitResult(body)

    def _generateIncludes(self, libraries):
        # generate the HTML that will be included in the response
        site = zope.component.hooks.getSite()
        if site is None:
            return

        resources = queryMultiAdapter(
            (site, self._request), interface.Interface, name='')

        if not IBrowserPublisher.providedBy(resources):
            # a setup with no resources factory is supported; in this
            # case, we manually craft a URL to the resource publisher
            # (see ``zope.browserresource.resource``).
            resources = None
            base = queryMultiAdapter(
                (site, self._request), IAbsoluteURL, name="resource")
            if base is None:
                baseURL = str(getMultiAdapter(
                    (site, self._request), IAbsoluteURL))
            else:
                baseURL = str(base)

        html = []
        for lib in libraries:
            if resources is not None:
                library_resources = resources[lib]

            included = zc.resourcelibrary.getIncluded(lib)
            for file_name in included:
                if resources is not None:
                    url = library_resources[file_name]()
                else:
                    url = "%s/@@/%s/%s" % (baseURL, lib, file_name)
                if file_name.endswith('.js'):
                    html.append('<script src="%s" ' % url)
                    html.append('    type="text/javascript">')
                    html.append('</script>')
                elif file_name.endswith('.css'):
                    html.append('<style type="text/css" media="all">')
                    html.append('  <!--')
                    html.append('    @import url("%s");' % url)
                    html.append('  -->')
                    html.append('</style>')
                elif file_name.endswith('.kss'):
                    html.append('<link type="text/kss" href="%s" rel="kinetic-stylesheet" />' % url)
                else:
                    # shouldn't get here; zcml.py is supposed to check includes
                    raise RuntimeError('Resource library doesn\'t know how to '
                                       'include this file: "%s"' % file_name)

        return '\n    '.join(html)

    def _addDependencies(self, resource_libraries):
        result = []
        def add_lib(lib):
            if lib in result:
                return # Nothing to do
            try:
                required = zc.resourcelibrary.getRequired(lib)
            except KeyError:
                raise RuntimeError('Unknown resource library: "%s"' % lib)
            for other in required:
                add_lib(other)
            if zc.resourcelibrary.getIncluded(lib):
                result.append(lib)
        for lib in resource_libraries:
            add_lib(lib)
        return result
