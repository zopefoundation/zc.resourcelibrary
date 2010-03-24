import doctest
import unittest

from zc.resourcelibrary import resourcelibrary
from zc.resourcelibrary.resourcelibrary import LibraryInfo


def setUp(test):
    test.old_library_info = resourcelibrary.library_info
    resourcelibrary.library_info = library_info = {}
    # Dependencies:
    #
    #  libA   libD
    #     \    /
    #    libB /
    #       \/
    #      libC
    #
    library_info['libA'] = LibraryInfo()
    library_info['libA'].required.append('libB')
    library_info['libB'] = LibraryInfo()
    library_info['libB'].required.append('libC')
    library_info['libC'] = LibraryInfo()
    library_info['libD'] = LibraryInfo()
    library_info['libD'].required.append('libC')


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
