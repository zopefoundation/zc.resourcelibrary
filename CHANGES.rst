=========
 CHANGES
=========

2.0.0 (2017-05-23)
==================


- Add support for Python 3.4, 3.5, 3.6 and PyPy.
- Drop test dependency on ``zope.app.testing`` and
  ``zope.app.zcmlfiles``, among others.
- Make zope.app.publication dependency optional.



1.3.4 (2012-01-20)
==================

- Register adapters with getSiteManager rather than getGlobalSiteManager. This
  allows registering resource libraries in non-global sites. For detais see:

   - https://mail.zope.org/pipermail/zope-dev/2010-March/039657.html
   - http://docs.pylonsproject.org/projects/pyramid_zcml/en/latest/narr.html#using-broken-zcml-directives

- Raise NotImplementedError if we find that a second ZCML declaration would
  change the global library_info dict in a way that may (depending on ZCML
  ordering) break applications at runtime. These errors were pretty hard to
  debug.

- Remove unneeded test dependencies on ``zope.app.authentication`` and
  ``zope.app.securitypolicy``.

- Remove dependency on ``zope.app.pagetemplate``.

1.3.2 (2010-08-16)
==================

- Response._addDependencies will only include a ResourceLibrary in the
  list of dependencies if the ResourceLibrary actually has included
  resources.

  This makes directives that simply declare dependencies on other
  libraries work again.

- Add missing depedency on ``zope.app.pagetemplate``, clean up unused
  imports and whitespace.

1.3.1 (2010-03-24)
==================

- Resource libraries that are required during a retried request are now
  correctly registered and injected to the HTML.

- Import hooks functionality from zope.component after it was moved there from
  zope.site. This lifts the dependency on zope.site.

- Removed an unused ISite import and thereby, the undeclared dependency on
  zope.location.


1.3.0 (2009-10-08)
==================

- Use ``zope.browserresource`` instead of ``zope.app.publisher``, removing
  a dependency on latter.

- Look up the "resources view" via queryMultiAdapter instead of looking into
  the adapter registry.

- Moved the dependency on zope.site to the test dependencies.

1.2.0 (2009-06-04)
==================

- Use ``zope.site`` instead of ``zope.app.component``.  Removes direct
  dependency on ``zope.app.component``.

1.1.0 (2009-05-05)
==================

New features:

- An attempt to generate resource URLs using the "resources view" (@@)
  is now made; if unsuccesful, we fall back to the previous method of
  crafting the URL by hand from the site url. This ensures that the
  resource library respects the existing plugging points for resource
  publishing (see ``zope.app.publisher.browser.resources``).

- You can now explicitly specify where resource links should be
  inserted using the special marker comment '<!-- zc.resourcelibrary -->'.

1.0.2 (2009-01-27)
==================

- Remove zope.app.zapi from dependencies, substituting
  its uses with direct imports.

- Use zope-dev at zope.org mailing list address instead of
  zope3-dev at zope.org as the latter one is retired.

- Change "cheeseshop" to "pypi" in the package homepage.

1.0.1 (2008-03-07)
==================

Bugs fixed:

- added the behavior from the standard Zope 3 response to guess that a body
  that is not HTML without an explicit mimetype should have a
  'text/plain' mimetype.  This means that, for instance, redirects with
  a body of '' and no explicit content type will no longer cause an
  exception in the resourcelibrary response code.

1.0.0 (2008-02-17)
==================

New features:

- You can now provide an alternative "directory-resource"
  factory. This facilitates implementation of dynamic resources.


Bugs fixed:

- Updated the functional-testing zcml file to get rid of a deprecation
  warning.


0.8.2 (2007-12-07)
==================

- bug fix: when checking content type, take into account that it may be None

0.8.1 (2007-12-05)
==================

- changed MIME type handling to be more restrictive about whitespace to
  conform to RfC 2045

0.8 (2007-12-04)
================

- fixed the check for HTML and XML content to allow content type parameters

0.6.1 (2007-11-03)
==================

- Update package meta-data.

- Fixed package dependencies.

- Merged functional and unit tests.

0.6.0 (2006-09-22)
==================

???

0.5.2 (2006-06-15)
==================

- Add more package meta-data.

0.5.1 (2006-06-06)
==================

- Update package code to work with newer versions of other packages.

0.5.0 (2006-04-24)
==================

- Initial release.
