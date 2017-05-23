It used to be that this configuration would result in wierd errors later as the
global library_info dict would depend on the order declarations appeared in the
ZCML.

Now it just errors faster:

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...   <include package="." file="meta.zcml" />
    ...
    ...   <includeOverrides
    ...     package="zc.resourcelibrary.tests"
    ...     file="duplicate_declarations_overrides.zcml"/>
    ...   <include
    ...     package="zc.resourcelibrary.tests"
    ...     file="duplicate_declarations.zcml"/>
    ...
    ... </configure>
    ... """)
    Traceback (most recent call last):
    ...
    ZopeXMLConfigurationError:...
        NotImplementedError: Can't cope with 2 different registrations of the same library: some-library ([], []) ([], [u'1.js'])

This is what getIncluded would have returned if the above had not errored (it
is wrong as includeOverrides should have take precedence):

    >>> from zc.resourcelibrary import getIncluded
    >>> getIncluded("some-library") # doctest: +SKIP
    [u'included.js', u'included.css']

However we work if you load up the same ZCML file twice (as the information in
library_info is exactly the same):

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...   <include package="." file="meta.zcml" />
    ...
    ...   <include
    ...     package="zc.resourcelibrary.tests"
    ...     file="duplicate_declarations_overrides.zcml"/>
    ...
    ... </configure>
    ... """)
    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...   <include package="." file="meta.zcml" />
    ...
    ...   <include
    ...     package="zc.resourcelibrary.tests"
    ...     file="duplicate_declarations_overrides.zcml"/>
    ...
    ... </configure>
    ... """)

The correct result from getIncluded is:

    >>> getIncluded("some-library")
    [u'1.js']
