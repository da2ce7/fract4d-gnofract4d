#!/usr/bin/env python

import unittest
import string
import commands
import re
import dl

import testbase

import fc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.load_formula_file("./gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")
        
class FCTest(testbase.TestBase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp
        
    def tearDown(self):
        pass

    def testLoad(self):
        
        ff = self.compiler.files["gf4d.frm"]
        self.assertNotEqual(string.index(ff.contents,"Modified for Gf4D"),-1)
        self.assertNotEqual(ff.get_formula("T03-01-G4"),None)
        self.assertEqual(len(ff.formulas) > 0,1)
        f = self.compiler.get_formula("gf4d.frm","T03-01-G4")
        self.assertEqual(f.errors, [])
        commands.getoutput("rm -f test-out.so")
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-out.so",None)
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

        f = self.compiler.get_formula("test.xxx","nonexistent")
        self.assertEqual(f,None)
        f = self.compiler.get_formula("test.frm","nonexistent")
        self.assertEqual(f,None)
        f = self.compiler.get_formula("test.frm","parse_error")
        self.assertEqual(len(f.errors),1)

    def disabled_testEvil(self):
        # this was too slow so turned it off
        f = self.compiler.get_formula("test.frm","frm:ny2004-4")
        self.assertEqual(len(f.errors),0)
        print f.pretty()
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-evil.so",None)
        
        f = self.compiler.get_formula("test.frm","Fractint-9-21")
        self.assertNoErrors(f)
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-evil.so",None)

    def testColorFunc(self):
        cf1 = self.compiler.get_colorfunc("gf4d.cfrm","default","cf0")
        self.assertEqual(len(cf1.errors),0)
        self.compiler.compile(cf1)
        
        cf2 = self.compiler.get_colorfunc("gf4d.cfrm","zero","cf1")
        self.assertEqual(len(cf2.errors),0)
        self.compiler.compile(cf2)
        
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg = self.compiler.compile(f)

        f.merge(cf1,"cf0")
        f.merge(cf2,"cf1")

        self.compiler.generate_code(f,cg,"test-cf.so",None)

    def testFractal(self):
        f = fc.Fractal(self.compiler)
        f.set_formula("gf4d.frm","Mandelbrot")
        f.set_inner("gf4d.cfrm","default")
        f.set_outer("gf4d.cfrm","zero")
        s = f.compile()

    def testFractalBadness(self):
        f = fc.Fractal(self.compiler)
        self.assertRaises(ValueError,f.set_formula,"gf4d.frm","xMandelbrot")
        self.assertRaises(ValueError,f.set_inner,"gf4d.cfrm","xdefault")
        self.assertRaises(ValueError,f.set_outer,"gf4d.cfrm","xzero")
        self.assertRaises(ValueError,f.compile)
        
        
def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

