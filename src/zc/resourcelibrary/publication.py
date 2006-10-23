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
"""
$Id: publication.py 4528 2005-12-23 02:45:25Z gary $
"""
from zope import interface
from zope.app.publication.interfaces import IBrowserRequestFactory
from zope.publisher.browser import BrowserRequest, BrowserResponse
from zope.publisher.browser import isHTML
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.traversing.browser.interfaces import IAbsoluteURL

import zc.resourcelibrary


class Request(BrowserRequest):
    interface.classProvides(IBrowserRequestFactory)
    # __slots__ = ('resource_libraries',)

    def _createResponse(self):
        response = Response()
        self.resource_libraries = response.resource_libraries = []
        return response


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

        if content_type == 'text/html' or content_type == 'text/xml':
            #act on HTML and XML content only!

            self.resource_libraries = self._addDependencies(self.resource_libraries)

            # generate the HTML that will be included in the response
            html = []
            site = getSite()
            baseURL = str(getMultiAdapter((site, self._request),
                                          IAbsoluteURL))
            for lib in self.resource_libraries:
                included = zc.resourcelibrary.getIncluded(lib)
                for file_name in included:
                    if file_name.endswith('.js'):
                        html.append('<script src="%s/@@/%s/%s" '
                                    % (baseURL, lib, file_name))
                        html.append('    type="text/javascript">')
                        html.append('</script>')
                    elif file_name.endswith('.css'):
                        html.append('<style type="text/css" media="all">')
                        html.append('  <!--')
                        html.append('    @import url("%s/@@/%s/%s");'
                                    % (baseURL, lib, file_name))
                        html.append('  -->')
                        html.append('</style>')
                    else:
                        # shouldn't get here; zcml.py is supposed to check includes
                        raise RuntimeError('Resource library doesn\'t know how to '
                                           'include this file: "%s"' % file_name)
    
            if html:
                body = body.replace('<head>', '<head>\n    %s\n' %
                                    '\n    '.join(html))


        return super(Response, self)._implicitResult(body)

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
            result.append(lib)
        for lib in resource_libraries:
            add_lib(lib)
        return result
