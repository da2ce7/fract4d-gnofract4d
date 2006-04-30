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
        'Check we correctly classify funcs by color/insideness'
        fl = [x for (x,y) in self.compiler.formula_files()]
        self.assertEqual(fl.count("gf4d.frm"), 1)
        self.assertEqual(fl.count("test.frm"), 1)
        self.assertEqual(fl.count("gf4d.cfrm"), 0)
        
        cfl = [x for (x,y) in self.compiler.colorfunc_files()]
        self.assertEqual(cfl.count("gf4d.cfrm"),1)
        self.assertEqual(cfl.count("gf4d.frm"), 0)
        
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
        'Check we notice when a file changes'
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
            self.assertEqual(frm.symbols.default_params(),[0, 4.0])

            formulas = formulas.replace('4.0','6.0')
            time.sleep(1.0) # ensure filesystem will have a different time
            f = open("fttest.frm","w")
            f.write(formulas)
            f.close()

            frm2 = f2.get_formula("fttest.frm","test_circle")
            self.assertEqual(frm2.symbols.default_params(),[0, 6.0])
            
        finally:
            os.remove("fttest.frm")
            
    def testCompile(self):
        'Check we can compile a fractal and the resulting .so looks ok'
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
        # DL module doesn't work on x86_64, so disabling this part
        #so = dl.open('./test-out.so', dl.RTLD_NOW)
        #self.assertNotEqual(so.sym('pf_new'),0)
        #self.assertNotEqual(so.call('pf_new'),0)

    def testErrors(self):
        'Check we raise appropriate exns when formulas are busted'
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
        f = self.compiler.get_formula("test.frm","ny2004-4")
        self.assertEqual(len(f.errors),0)
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-evil.so",None)
        
        f = self.compiler.get_formula("test.frm","Fractint-9-21")
        self.assertNoErrors(f)
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-evil.so",None)

    def testPreprocessor(self):
        f = self.compiler.get_formula("test.frm","test_preprocessor")
        self.assertNoErrors(f)
        cg = self.compiler.compile(f)
        of = self.compiler.generate_code(f,cg)

    def testPreprocessorError(self):
        ff = self.compiler.load_formula_file("test_bad_pp.frm")
        f = self.compiler.get_formula("test_bad_pp.frm","error")
        self.assertEqual(len(f.errors),1)        
        self.compiler.files["test_bad_pp.frm"] = None
        
    def testColorFunc(self):
        'Compile inner + outer colorfuncs and merge'
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
        'Compile the same thing twice, check results same'
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg = self.compiler.compile(f)
        of1 = self.compiler.generate_code(f,cg)

        f2 = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg2 = self.compiler.compile(f2)
        of2 = self.compiler.generate_code(f,cg2)

        self.assertEqual(of1,of2)

    def testFormulasNotConnected(self):
        'fetch the same thing twice, check symbols tables differ'
        f = self.compiler.get_formula("fractint-builtin.frm","julfn+exp")
        f2 = self.compiler.get_formula("fractint-builtin.frm","julfn+exp")
        self.assertNotEqual(f,f2)
        self.assertNotEqual(f.symbols, f2.symbols)
        ol = f.symbols["@fn1"]
        ol2 = f2.symbols["@fn1"]
        self.assertNotEqual(ol, ol2)
        func = ol[0]
        func2 = ol2[0]
        self.assertNotEqual(func,func2)
        
    def testAllFormulasCompile(self):
        'Go through every formula and check for errors'
        for filename in self.compiler.find_formula_files():
            ff = self.compiler.get_file(filename)
            for fname in ff.get_formula_names():
                f = self.compiler.get_formula(ff.filename, fname)
                self.assertNoErrors(f, "%s:%s" % (filename, fname))
                
def suite():
    return unittest.makeSuite(FCTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

