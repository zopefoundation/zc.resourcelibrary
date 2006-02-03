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
import zc.resourcelibrary.zcml

class Request(BrowserRequest):
    interface.classProvides(IBrowserRequestFactory)
    # __slots__ = ('resource_libraries',)

    def _createResponse(self):
        response = Response()
        self.resource_libraries = response.resource_libraries = set()
        return response


class Response(BrowserResponse):

    def _implicitResult(self, body):

        # add any libraries that the explicitly referenced libraries require
        libs = list(self.resource_libraries)
        while libs:
            lib = libs.pop()
            try:
                required = zc.resourcelibrary.getRequired(lib)
            except KeyError:
                raise RuntimeError('Unknown resource library: "%s"' % lib)
            for lib in required:
                if lib not in self.resource_libraries:
                    self.resource_libraries.add(lib)
                    libs.append(lib)

        # generate the HTML that will be included in the response
        html = []
        for lib in self.resource_libraries:
            included = zc.resourcelibrary.getIncluded(lib)
            for file_name in included:
                if file_name.endswith('.js'):
                    html.append('<script src="/@@/%s/%s" '
                                'language="Javascript1.1"' % (lib, file_name))
                    html.append('    type="text/javascript">')
                    html.append('</script>')
                elif file_name.endswith('.css'):
                    html.append('<style type="text/css" media="all">')
                    html.append('  <!--')
                    html.append('    @import url("/@@/%s/%s");'
                                % (lib, file_name))
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
