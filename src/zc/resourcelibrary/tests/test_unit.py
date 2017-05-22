
import re
import doctest
import unittest

from zope.testing import renormalizing

from zc.resourcelibrary import resourcelibrary
from zc.resourcelibrary.resourcelibrary import LibraryInfo

from zc.resourcelibrary.tests.tests import checker

class TestDependencyResolution(unittest.TestCase):

    def setUp(self):
        self.old_library_info = resourcelibrary.library_info
        resourcelibrary.library_info = library_info = {}
        # Dependencies:
        #
        #           libE
        #            /
        #  libA   libD
        #     \    /
        #    libB /
        #       \/
        #      libC
        def lib_info(included=None, required=None):
            res = LibraryInfo()
            if included:
                res.included.append(included)
            if required:
                res.required.append(required)
            return res
        library_info['libA'] = lib_info('foo.js', 'libB')
        library_info['libB'] = lib_info('bar.js', 'libC')
        library_info['libC'] = lib_info('baz.js')
        library_info['libD'] = lib_info('foo.css', 'libC')
        library_info['libE'] = lib_info(required='libD')


    def tearDown(self):
        resourcelibrary.library_info = self.old_library_info


    def test_dependency_resolution(self):
        # Test Response._addDependencies

        from zc.resourcelibrary.publication import Response
        r = Response()

        # The method gets a list of libraries and adds all their dependencies
        # in the proper order

        self.assertEqual(r._addDependencies(['libA']),
                         ['libC', 'libB', 'libA'])

        # Here's a tricky corner case that the old algorithm used to get wrong:

        self.assertEqual(r._addDependencies(['libA', 'libD']),
                         ['libC', 'libB', 'libA', 'libD'])

        # No library is included more than once

        self.assertEqual(r._addDependencies(['libC', 'libA', 'libD', 'libA']),
                         ['libC', 'libB', 'libA', 'libD'])

        # If a library doesn't contain any included resources, only its
        # required libraries will be included in its list of dependencies.

        self.assertEqual(r._addDependencies(['libE']),
                         ['libC', 'libD'])

        # Unknown library names cause errors

        with self.assertRaises(RuntimeError) as exc:
            r._addDependencies(['libA', 'libZ'])

        self.assertEqual('Unknown resource library: "libZ"',
                         exc.exception.args[0])

class TestResourceLibrary(unittest.TestCase):

    def test_need_no_request(self):
        # does nothing, but doesn't fail
        self.assertIsNone(resourcelibrary.need('foo'))

def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite(
            'zc.resourcelibrary.publication',
            optionflags=(doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2),
            checker=checker,
        ),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
