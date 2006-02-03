================
Resource Library
================

The resource library is designed to make the inclusion of JavaScript, CSS, and
other resources easy, cache-friendly, and component-friendly.  For instance, if
two widgets on a page need the same JavaScript library, the library should be
only loaded once, but the widget designers should not have to concern
themselves with the presence of other widgets.

Imagine that one widget has a copy of a fictional Javascript library.  To
configure that library as available use ZCML like this:

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="some-library">
    ...     <directory source="example"/>
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """)

This is exactly equivalent to a resourceDirectory tag, with no additional
effect.

Loading Files
-------------

It is also possible to indicate that one or more Javascript or CSS files should
be included (by reference) into the HTML of a page that needs the library.
This is the current difference between resourceLibrary and resourceDirectory.

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="my-lib">
    ...     <directory
    ...         source="example/my-lib"
    ...         include="included.js included.css"
    ...     />
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """)

If a file is included that the resource library doesn't understand (i.e. it
isn't Javascript or CSS), an exception will occur.

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="bad-lib">
    ...     <directory
    ...         source="example/my-lib"
    ...         include="included.bad"
    ...     />
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """)
    Traceback (most recent call last):
    ...
    ZopeXMLConfigurationError:...
        ConfigurationError: Resource library doesn't know how to include this
        file: "included.bad".

Usage
-----

Components signal their need for a particular resource library (Javascript or
otherwise) by using a special TAL expression.  (The use of replace is not
mandated, the result may be assigned to a dummy variable, or otherwise
ignored.)

    >>> zpt('<tal:block replace="resource_library:my-lib"/>')

We'll be using a testbrowser.Browser to simulate a user viewing web pages.

    >>> from zope.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

When a page is requested that does not need any resource libraries, the HTML
will be untouched.

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_1')
    >>> browser.contents
    '...<head></head>...'

When a page is requested that uses a component that needs a resource library,
the library will be referenced in the rendered page.

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_2')

A reference to the JavaScript is inserted into the HTML.

    >>> '/@@/my-lib/included.js' in browser.contents
    True

And the JavaScript is available from the URL referenced.

    >>> browser.open('/@@/my-lib/included.js')
    >>> print browser.contents
        function be_annoying() {
        alert('Hi there!');
    }

A reference to the CSS is also inserted into the HTML.

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_2')
    >>> '/@@/my-lib/included.css' in browser.contents
    True

And the CSS is available from the URL referenced.

    >>> browser.open('/@@/my-lib/included.css')
    >>> print browser.contents
    div .border {
        border: 1px silid black;
    }

A reference to an unknown library causes an exception.

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_3')
    Traceback (most recent call last):
    ...
    RuntimeError: Unknown resource library: "does-not-exist"

Library usage may also be signaled programattically.  For example, if a page
would not otherwise include a resource library...

    >>> page = ('<html><head></head>'
    ...         '<body tal:define="unused view/doSomething">'
    ...         'This is the body.</body>')

    >>> class View(object):
    ...     def doSomething(self):
    ...         pass

    >>> zpt(page, view=View())
    '...<head></head>...'

...but we programmatically indicate that a resource library is needed, it will
be included.

    >>> import zc.resourcelibrary
    >>> class View(object):
    ...     def doSomething(self):
    ...         zc.resourcelibrary.need('my-lib')

    >>> '/@@/my-lib/included.js' in zpt(page, view=View())
    True

Dependencies
------------

If a resource library registers a dependency on another library, the dependency
must be satisfied or an error will be generated.

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="dependent-but-unsatisfied" require="not-here">
    ...     <directory source="example"/>
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """)
    Traceback (most recent call last):
    ...
    ConfigurationExecutionError:...Resource library "dependent-but-unsatisfied"
    has unsatisfied dependency on "not-here"...

When the dependencies are satisfied, the registrations will succeed.

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="dependent" require="dependency">
    ...     <directory source="example" include="1.js"/>
    ...   </resourceLibrary>
    ...
    ...   <resourceLibrary name="dependency">
    ...     <directory source="example" include="2.css"/>
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """)

If one library depends on another and the first library is referenced on a
page, the second library will also be included in the rendered HTML.

    >>> zpt('<tal:block replace="resource_library:dependent"/>')
    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_4')
    >>> '/@@/dependent/1.js' in browser.contents
    True
    >>> '/@@/dependency/2.css' in browser.contents
    True

Error Conditions
----------------

Errors are reported if you do something wrong.

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="some-library">
    ...     <directory source="does-not-exist"/>
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """)
    Traceback (most recent call last):
    ...
    ZopeXMLConfigurationError: ...
        ConfigurationError: Directory u'...does-not-exist' does not exist

Future Work
-----------

 * We want to be able to specify a single file to add to the resource.
 * We may want to be able to override a file in the resource with a different
   file.
 * Currently only one <directory> tag is allowed per-library.  If multiple tags
   are allowed, should they be merged or have distinct prefixes?
 * Add a test to ensure that files are only included once, and in the proper
   order
