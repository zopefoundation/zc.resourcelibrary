Like most zope.component declarations, resource libraries are registered
against the current, not global site manager:

    >>> class DummySiteManager:
    ...     def registerAdapter(self, *args, **kw):
    ...         print('registering our adapter')
    >>> class DummySite:
    ...     def getSiteManager(self):
    ...         return DummySiteManager()

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...   <include package="." file="meta.zcml" />
    ...
    ...   <resourceLibrary name="some-other-library">
    ...     <directory source="tests/example"/>
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """, site=DummySite())
    registering our adapter

Clean Up:

    >>> import zope.component.hooks
    >>> zope.component.hooks.setSite(None)
