#!/usr/bin/env python

import unittest
import string
import commands
import re

import fc

class FCTest(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        
    def tearDown(self):
        pass

    def testLoad(self):
        self.compiler.load_formula_file("./gf4d.frm")
        ff = self.compiler.files["gf4d.frm"]
        self.assertNotEqual(string.index(ff.contents,"Modified for Gf4D"),-1)
        self.assertNotEqual(ff.get_formula("T03-01-G4"),None)
        self.assertEqual(len(ff.formulas),1)
        f = self.compiler.get_formula("gf4d.frm","T03-01-G4")
        self.assertEqual(f.errors, [])
        self.compiler.generate_code(f,"test-out.so")
        (status,output) = commands.getstatusoutput('nm test-out.so')
        self.assertEqual(status,0)
        self.assertEqual(string.count(output,"pf_new"),1)
        self.assertEqual(string.count(output,"pf_calc"),1)
        self.assertEqual(string.count(output,"pf_init"),1)
        self.assertEqual(string.count(output,"pf_kill"),1)
        
    def testErrors(self):
        self.assertRaises(
            Exception, self.compiler.load_formula_file, "nonexistent.frm")
        self.compiler.load_formula_file("test.frm")
        f = self.compiler.get_formula("test.xxx","nonexistent")
        self.assertEqual(f,None)
        f = self.compiler.get_formula("test.frm","nonexistent")
        self.assertEqual(f,None)
        f = self.compiler.get_formula("test.frm","parse_error")
        self.assertEqual(len(f.errors),1)
        
def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
