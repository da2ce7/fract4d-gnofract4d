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
        ff = self.compiler.files["gf4d.frm"]
        self.assertNotEqual(string.index(ff.contents,"Modified for Gf4D"),-1)
        self.assertNotEqual(ff.get_formula("T03-01-G4"),None)
        self.assertEqual(len(ff.formulas),1)
        f = self.compiler.get_formula("gf4d.frm","T03-01-G4")
        self.assertEqual(f.leaf, "T03-01-G4")
            

def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

