#!/usr/bin/env python

import unittest
import string
import commands
import re
import dl

import testbase

import fc

class FCTest(testbase.TestBase):
    def setUp(self):
        self.compiler = fc.Compiler()
        self.assertFoo()
        
    def tearDown(self):
        pass

    def testLoad(self):
        self.compiler.load_formula_file("./gf4d.frm")
        ff = self.compiler.files["gf4d.frm"]
        self.assertNotEqual(string.index(ff.contents,"Modified for Gf4D"),-1)
        self.assertNotEqual(ff.get_formula("T03-01-G4"),None)
        self.assertEqual(len(ff.formulas) > 0,1)
        f = self.compiler.get_formula("gf4d.frm","T03-01-G4")
        self.assertEqual(f.errors, [])
        commands.getoutput("rm -f test-out.so")
        self.compiler.generate_code(f,"test-out.so",None)
        # check the output contains the right functions
        (status,output) = commands.getstatusoutput('nm test-out.so')
        self.assertEqual(status,0)
        self.assertEqual(string.count(output,"pf_new"),1)
        self.assertEqual(string.count(output,"pf_calc"),1)
        self.assertEqual(string.count(output,"pf_init"),1)
        self.assertEqual(string.count(output,"pf_kill"),1)

        # load it and mess around
        so = dl.open('./test-out.so', dl.RTLD_NOW)
        self.assertNotEqual(so.sym('pf_new'),0)
        self.assertNotEqual(so.call('pf_new'),0)

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

    def testEvil(self):
        self.compiler.load_formula_file("test.frm")
        f = self.compiler.get_formula("test.frm","frm:ny2004-4")
        self.assertEqual(len(f.errors),0)
        #print f.pretty()
        self.compiler.generate_code(f,"test-evil.so",None)
        
        f = self.compiler.get_formula("test.frm","Fractint-9-21")
        self.assertNoErrors(f)
        self.compiler.generate_code(f,"test-evil.so",None)
        
def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

