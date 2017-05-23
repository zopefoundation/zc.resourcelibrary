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
from zope.publisher.interfaces import IRequest
import zope.security.management
import zope.security.interfaces

library_info = {}

class LibraryInfo(object):
    def __init__(self):
        self.included = []
        self.required = []


def getRequest():
    try:
        i = zope.security.management.getInteraction() # raises NoInteraction
    except zope.security.interfaces.NoInteraction:
        return

    for p in i.participations:
        if IRequest.providedBy(p):
            return p

def need(library_name):
    request = getRequest()
    # only take note of needed libraries if there is a request, and it is
    # capable of handling resource librarys
    if request is not None and hasattr(request, 'resource_libraries'):
        if not library_name in request.resource_libraries:
            request.resource_libraries.append(library_name)

def getRequired(name):
    return library_info[name].required

def getIncluded(name):
    return library_info[name].included

try:
    from zope.testing import cleanup
except ImportError: # pragma: no cover
    pass
else:
    cleanup.addCleanUp(library_info.clear)
