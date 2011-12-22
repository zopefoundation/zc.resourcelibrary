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
    ...     <directory source="tests/example"/>
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
    ...         source="tests/example/my-lib"
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
    ...         source="tests/example/my-lib"
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

    >>> from zope.testbrowser.testing import Browser
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

For inclusion of resources the full base url with namespaces is used.

    >>> browser.open('http://localhost/++skin++Basic/zc.resourcelibrary.test_template_2')
    >>> print browser.contents
    <html...
    src="http://localhost/++skin++Basic/@@/my-lib/included.js"...
    </html>

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
    ...     context = getRootFolder()
    ...     def doSomething(self):
    ...         pass

    >>> zpt(page, view=View())
    '...<head></head>...'

...but we programmatically indicate that a resource library is needed, it will
be included.

    >>> import zc.resourcelibrary
    >>> class View(object):
    ...     context = getRootFolder()
    ...     def doSomething(self):
    ...         zc.resourcelibrary.need('my-lib')

    >>> '/@@/my-lib/included.js' in zpt(page, view=View())
    True

Content-type checking
---------------------

Resources should be referenced only from HTML and XML content, other content
types should not be touched by the resource library:

    >>> page = ('<html><head>'
    ...         '<tal:block replace="resource_library:my-lib"/>'
    ...         '</head><body></body></html>')

    >>> '/@@/my-lib/included.js' in zpt(page, content_type='text/html')
    True

    >>> '/@@/my-lib/included.js' in zpt(page, content_type='text/xml')
    True

    >>> '/@@/my-lib/included.js' in zpt(page, content_type='text/none')
    False

This also works if the content type contains uppercase characters, as per RfC
2045 on the syntax of MIME type specifications (we can't test uppercase
characters in the major type yet since the publisher is not completely up to
the RfC on that detail yet):

    >>> '/@@/my-lib/included.js' in zpt(page, content_type='text/hTMl')
    True

    >>> '/@@/my-lib/included.js' in zpt(page, content_type='text/nOne')
    False

Parameters to the content type can't fool the check either:

    >>> '/@@/my-lib/included.js' in zpt(
    ...     page, content_type='text/xml; charset=utf-8')
    True

    >>> '/@@/my-lib/included.js' in zpt(
    ...     page, content_type='text/none; charset=utf-8')
    False

The content type is, however, assumed to be a strictly valid MIME type
specification, implying that it can't contain any whitespace up to the
semicolon signalling the start of parameters, if any (we can't test whitespace
around the major type as that would already upset the publisher):

    >>> '/@@/my-lib/included.js' in zpt(
    ...     page, content_type='text/ xml')
    False

    >>> '/@@/my-lib/included.js' in zpt(
    ...     page, content_type='text/xml ; charset=utf-8')
    False

The content type may also be None if it was never set, which of course doesn't
count as HTML or XML either:

    >>> from zc.resourcelibrary import publication
    >>> from StringIO import StringIO
    >>> request = publication.Request(body_instream=StringIO(''), environ={})
    >>> request.response.setResult("This is not HTML text.")
    >>> '/@@/my-lib/included.js' in request.response.consumeBody()
    False


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
    ...     <directory source="tests/example"/>
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
    ...     <directory source="tests/example" include="1.js"/>
    ...   </resourceLibrary>
    ...
    ...   <resourceLibrary name="dependency">
    ...     <directory source="tests/example" include="2.css"/>
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

Order matters, espacially for js files, so the dependency should
appear before the dependent library in the page

    >>> print browser.contents.strip()
    <html>...dependency/2.css...dependent/1.js...</html>

It is possible for a resource library to only register a list of dependencies
and not specify any resources.

When such a library is used in a resource_library statement in a template,
only its dependencies are referenced in the final rendered page.

    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="only_require" require="my-lib dependent"/>
    ...
    ... </configure>
    ... """)
    >>> zpt('<tal:block replace="resource_library:only_require"/>')
    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_7')
    >>> '/@@/my-lib/included.js' in browser.contents
    True
    >>> '/@@/my-lib/included.css' in browser.contents
    True
    >>> '/@@/dependent/1.js' in browser.contents
    True
    >>> '/@@/dependency/2.css' in browser.contents
    True
    >>> '/@@/only_require' in browser.contents
    False


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

Multiple Heads
--------------

On occasion the body of an HTML document may contain the text "<head>".  In
those cases, only the actual head tag should be manipulated.  The first
occurrence of "<head>" has the script tag inserted...

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_5')
    >>> print browser.contents
    <html>...<head> <script src="http://localhost/@@/my-lib/included.js"...

...but that is the only time it is inserted.

    >>> browser.contents.count('src="http://localhost/@@/my-lib/included.js"')
    1

Error during publishing
-----------------------

Note that in case an exception is raised during publishing, the
resource library is disabled.

    >>> browser.handleErrors = True
    >>> browser.post(
    ...    'http://localhost/zc.resourcelibrary.test_template_5',
    ...    'value:int=dummy', 'multipart/form-data')
    Traceback (most recent call last):
     ...
    HTTPError: ...
    >>> '/@@/my-lib/included.js' in browser.contents
    False

Custom "directory" factories
----------------------------

By default, a resource directory is created when a directory directive
is used.  You can add a factory option to specify a different
resource-directory factory.  This can be used, for example, to provide
dynamic resources.


    >>> zcml("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     package="zc.resourcelibrary">
    ...
    ...   <resourceLibrary name="my-lib">
    ...     <directory
    ...         source="tests/example/my-lib"
    ...         include="foo.js"
    ...         factory="zc.resourcelibrary.tests.tests.TestFactory"
    ...     />
    ...   </resourceLibrary>
    ...
    ... </configure>
    ... """, clear=['my-lib'])

The factory will be called with a source directory, a security checker
and a name.  We've created a class that implements a resource
directory dynamically.

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_2')
    >>> '/@@/my-lib/foo.js' in browser.contents
    True

    >>> browser.open('http://localhost/@@/my-lib/foo.js')
    >>> print browser.contents,
    foo = 1;

Library insertion place marker
------------------------------

You can explicitly mark where to insert HTML. Do do that, add the
special comment "<!-- zc.resourcelibrary -->" (exact string, w/o quotes)
to the template. It will be replaced by resource libraries HTML on
processing.

    >>> browser.open('http://localhost/zc.resourcelibrary.test_template_6')

A reference to the JavaScript is inserted into the HTML.

    >>> print browser.contents
    <html>
      <head>
        <title>Marker test</title>
    <BLANKLINE>
        <!-- Libraries will be included below -->
        <script src="http://localhost/@@/my-lib/foo.js"
            type="text/javascript">
        </script>
      </head>
    ...
    </html>

Future Work
-----------

 * We want to be able to specify a single file to add to the resource.
 * We may want to be able to override a file in the resource with a different
   file.
 * Currently only one <directory> tag is allowed per-library.  If multiple tags
   are allowed, should they be merged or have distinct prefixes?
 * Add a test to ensure that files are only included once, and in the proper
   order
