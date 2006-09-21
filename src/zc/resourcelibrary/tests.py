import doctest
import unittest
from zope.testing.doctestunit import DocTestSuite
def test_suite():
    
    return unittest.TestSuite(
        (
        DocTestSuite('zc.resourcelibrary.publication',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
