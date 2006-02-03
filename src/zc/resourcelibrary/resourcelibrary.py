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
    if request and hasattr(request, 'resource_libraries'):
        request.resource_libraries.add(library_name)

def getRequired(name):
    return library_info[name].required

def getIncluded(name):
    return library_info[name].included
