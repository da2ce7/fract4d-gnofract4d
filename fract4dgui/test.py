#!/usr/bin/env python

import unittest
import test_gtkfractal
import test_undo
import test_model
import test_preferences

def suite():
    s1 = test_gtkfractal.suite()
    s2 = test_undo.suite()
    s3 = test_model.suite()
    s4 = test_preferences.suite()
    
    return unittest.TestSuite((s1,s2,s3, s4))

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

