#!/usr/bin/env python

import unittest
import test_fractlexer
import test_fractparser
import test_symbol

def suite():
    s1 = test_fractlexer.suite()
    s2 = test_fractparser.suite()
    s3 = test_symbol.suite()
    return unittest.TestSuite((s1, s2, s3))

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
