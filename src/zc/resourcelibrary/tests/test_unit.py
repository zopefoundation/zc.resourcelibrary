import doctest
import unittest

from zc.resourcelibrary import resourcelibrary
from zc.resourcelibrary.resourcelibrary import LibraryInfo


def setUp(test):
    test.old_library_info = resourcelibrary.library_info
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


def tearDown(test):
    resourcelibrary.library_info = test.old_library_info


def doctest_dependency_resolution():
    """Test Response._addDependencies

        >>> from zc.resourcelibrary.publication import Response
        >>> r = Response()

    The method gets a list of libraries and adds all their dependencies
    in the proper order

        >>> r._addDependencies(['libA'])
        ['libC', 'libB', 'libA']

    Here's a tricky corner case that the old algorithm used to get wrong:

        >>> r._addDependencies(['libA', 'libD'])
        ['libC', 'libB', 'libA', 'libD']

    No library is included more than once

        >>> r._addDependencies(['libC', 'libA', 'libD', 'libA'])
        ['libC', 'libB', 'libA', 'libD']

    If a library doesn't contain any included resources, only its
    required libraries will be included in its list of dependencies.

        >>> r._addDependencies(['libE'])
        ['libC', 'libD']

    Unknown library names cause errors

        >>> r._addDependencies(['libA', 'libZ'])
        Traceback (most recent call last):
          ...
        RuntimeError: Unknown resource library: "libZ"

    """


def test_suite():
    return unittest.TestSuite(
        (
        doctest.DocTestSuite(setUp=setUp, tearDown=tearDown),
        doctest.DocTestSuite('zc.resourcelibrary.publication',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
