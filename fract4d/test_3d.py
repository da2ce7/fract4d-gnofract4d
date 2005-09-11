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

        handle = fract4dc.pf_load(f.outputfile)
        pfunc = fract4dc.pf_create(handle)
        cmap = fract4dc.cmap_create_gradient(f.get_gradient().segments)
        (r,g,b,a) = f.solids[0]
        fract4dc.cmap_set_solid(cmap,0,r,g,b,a)
        (r,g,b,a) = f.solids[1]
        fract4dc.cmap_set_solid(cmap,1,r,g,b,a)
        
        initparams = f.all_params()
        fract4dc.pf_init(pfunc,1.0E-9,initparams)

        (iter,fate,dist,solid) = fract4dc.pf_calc(pfunc, [0.0, 0.0, 0.0, 0.0], 100)
        self.assertEqual(fate,1) # should be inside
        
        (iter,fate,dist,solid) = fract4dc.pf_calc(pfunc, [-2.5, 0.0, 0.0, 0.0], 100)
        self.assertEqual(fate,0) # should be outside
        
        #image = fract4dc.image_create(40,30)
        #f.draw(image)
        #fract4dc.image_save(image,"hs.tga")
        
    def testVector(self):
        pass
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

