#!/usr/bin/env python

import unittest
import test_gtkfractal
import test_undo
import test_model
import test_preferences
import test_fourway
import test_angle

def suite():
    s1 = test_gtkfractal.suite()
    s2 = test_undo.suite()
    s3 = test_model.suite()
    s4 = test_preferences.suite()
    s5 = test_fourway.suite()
    s6 = test_angle.suite()
    
    return unittest.TestSuite((s1,s2,s3,s4,s5,s6))

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

