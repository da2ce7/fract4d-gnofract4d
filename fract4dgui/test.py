#!/usr/bin/env python

import unittest
import test_gtkfractal
import test_undo
import test_model
import test_preferences
import test_fourway
import test_angle
import test_hig

def suite():
    tests = (
        test_gtkfractal.suite(),
        test_undo.suite(),
        test_model.suite(),
        test_preferences.suite(),
        test_fourway.suite(),
        test_angle.suite(),
        test_hig.suite())
    return unittest.TestSuite(tests)

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

