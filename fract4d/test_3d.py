#!/usr/bin/env python

import unittest

import testbase

import fc
import fractal
import fract4dc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../formulas")
g_comp.load_formula_file("gf4d.frm")
g_comp.load_formula_file("gf4d.cfrm")
g_comp.load_formula_file("test.frm")

class Test(testbase.TestBase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp
        
    def tearDown(self):
        pass

    def testHyperSphereFormula(self):
        f = fractal.T(self.compiler)
        f.set_formula("test.frm", "test_hypersphere")
        f.compile()
        
        image = fract4dc.image_create(40,30)
        f.draw(image)

    def testVector(self):
        pass
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

