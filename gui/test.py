#!/usr/bin/env python

import unittest
import test_gtkfractal
import test_undo

def suite():
    s1 = test_gtkfractal.suite()
    s2 = test_undo.suite()
    
    return unittest.TestSuite((s1,s2))

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

