#!/usr/bin/env python

import unittest
import string

import fc

class FCTest(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        
    def tearDown(self):
        pass

    def testLoad(self):
        self.compiler.load_formula_file("gf4d.frm")
        (formulas,contents) = self.compiler.files["gf4d.frm"]
        self.assertNotEqual(string.index(contents,"Modified for Gf4D"),-1)
        self.assertNotEqual(formulas.get("T03-01-G4"),None)
        
def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

