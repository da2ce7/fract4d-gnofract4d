#!/usr/bin/env python

import unittest
import test_fractlexer
import test_fractparser
import test_symbol
import test_translate

def suite():
    s1 = test_fractlexer.suite()
    s2 = test_fractparser.suite()
    s3 = test_symbol.suite()
    s4 = test_translate.suite()
    return unittest.TestSuite((s1, s2, s3, s4))

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

