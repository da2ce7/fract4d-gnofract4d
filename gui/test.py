#!/usr/bin/env python

import unittest
import test_gtkfractal

def suite():
    s1 = test_gtkfractal.suite()
    
    return unittest.TestSuite((s1,))

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

