#!/usr/bin/env python

import unittest
import test_fractlexer
import test_fractparser

def suite():
    s1 = test_fractlexer.suite()
    s2 = test_fractparser.suite()
    return unittest.TestSuite((s1, s2))

alltests = suite()

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
