#!/usr/bin/env python

import unittest
import string
import commands
import re
import dl
import os
import time

import testbase

import fc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../formulas")
g_comp.load_formula_file("gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")
        
class FCTest(testbase.TestBase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp
        
    def tearDown(self):
        pass

    def testLists(self):
        fl = [x for (x,y) in self.compiler.formula_files()]
        fl.sort()
        self.assertEqual(fl,["gf4d.frm", "test.frm"])

        cfl = [x for (x,y) in self.compiler.colorfunc_files()]
        self.assertEqual(cfl,["gf4d.cfrm"])

        file = self.compiler.files["gf4d.cfrm"]
        names = file.get_formula_names()
        self.assertEqual(names,file.formulas.keys())

        inside_names = file.get_formula_names("OUTSIDE")
        for f in inside_names:
            self.assertNotEqual(file.formulas[f].symmetry, "OUTSIDE")

        outside_names = file.get_formula_names("INSIDE")
        for f in outside_names:            
            self.assertNotEqual(file.formulas[f].symmetry, "INSIDE")

    def testFileTimeChecking(self):
        try:
            f2 = fc.Compiler()
            
            formulas = '''
test_circle {
loop:
z = pixel
bailout:
|z| < @bailout
default:
float param bailout
	default = 4.0
endparam
}
test_square {
loop:
z = pixel
bailout: abs(real(z)) > 2.0 || abs(imag(z)) > 2.0
}
'''
            f = open("fttest.frm","w")
            f.write(formulas)
            f.close()
            
            f2.load_formula_file("fttest.frm")
            frm = f2.get_formula("fttest.frm","test_circle")
            self.assertEqual(frm.symbols.default_params(),[4.0])

            formulas = formulas.replace('4.0','6.0')
            time.sleep(1.0) # ensure filesystem will have a different time
            f = open("fttest.frm","w")
            f.write(formulas)
            f.close()

            frm2 = f2.get_formula("fttest.frm","test_circle")
            self.assertEqual(frm2.symbols.default_params(),[6.0])
            
        finally:
            os.remove("fttest.frm")
            
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
        self.assertEqual(string.count(output,"pf_calc"),2)
        self.assertEqual(string.count(output,"pf_init"),1)
        self.assertEqual(string.count(output,"pf_calc_period"),1)
        self.assertEqual(string.count(output,"pf_kill"),1)

        # load it and mess around
        so = dl.open('./test-out.so', dl.RTLD_NOW)
        self.assertNotEqual(so.sym('pf_new'),0)
        self.assertNotEqual(so.call('pf_new'),0)

    def testErrors(self):
        self.assertRaises(
            IOError, self.compiler.load_formula_file, "nonexistent.frm")

        self.assertRaises(
            IOError, self.compiler.get_formula, "test.xxx","nonexistent") 

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

        f.merge(cf1,"cf0_")
        f.merge(cf2,"cf1_")

        ofile = self.compiler.generate_code(f,cg)
        self.failUnless(os.path.exists(ofile))

    def testDoubleCompile(self):
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg = self.compiler.compile(f)
        of1 = self.compiler.generate_code(f,cg)

        cg2 = self.compiler.compile(f)
        of2 = self.compiler.generate_code(f,cg2)

        self.assertEqual(of1,of2)
        
def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

