#!/usr/bin/env python

import unittest

import test_makemap

def suite():
    tests = (
        test_makemap.suite(),
        )
    return unittest.TestSuite(tests)

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

