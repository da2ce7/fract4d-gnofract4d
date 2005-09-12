#!/usr/bin/env python

import unittest
import math

import testbase

import fc
import fractal
import fract4dc


from test_fractalsite import FractalSite

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

        self.f = fractal.T(self.compiler)
        self.f.set_formula("test.frm", "test_hypersphere")
        self.f.compile()

        handle = fract4dc.pf_load(self.f.outputfile)
        self.pfunc = fract4dc.pf_create(handle)
        self.cmap = fract4dc.cmap_create_gradient(self.f.get_gradient().segments)
        (r,g,b,a) = self.f.solids[0]
        fract4dc.cmap_set_solid(self.cmap,0,r,g,b,a)
        (r,g,b,a) = self.f.solids[1]
        fract4dc.cmap_set_solid(self.cmap,1,r,g,b,a)

        initparams = self.f.all_params()
        fract4dc.pf_init(self.pfunc,1.0E-9,initparams)

        self.image = fract4dc.image_create(40,30)
        siteobj = FractalSite()
        self.site = fract4dc.site_create(siteobj)
        
        self.fw = fract4dc.fw_create(1,self.pfunc,self.cmap,self.image,self.site)

        self.ff = fract4dc.ff_create(
            [0.0, 0.0, 0.0, 0.0,
             4.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            2,
            100,
            0,
            1,
            self.pfunc,
            self.cmap,
            0,
            1,
            0,
            self.image,
            self.site,
            self.fw)

    def tearDown(self):
        pass

    def testHyperSphereFormula(self):
        # check that a formula consisting of a simple 2.0-radius hypersphere
        # can be effectively ray-traced
        (iter,fate,dist,solid) = fract4dc.pf_calc(self.pfunc, [0.0, 0.0, 0.0, 0.0], 100)
        self.assertEqual(fate,1) # should be inside
        
        (iter,fate,dist,solid) = fract4dc.pf_calc(self.pfunc, [-2.5, 0.0, 0.0, 0.0], 100)
        self.assertEqual(fate,0) # should be outside

    def testLookVector(self):
        # check that looking at different points in screen works
        look = fract4dc.ff_look_vector(self.ff,0,0)
        big_look = [(-19.5/40) * 4.0, (14.5/30)*3.0, 40.0, 0.0]
        mag = math.sqrt(sum([x*x for x in big_look]))
        exp_look = tuple([x/mag for x in big_look])
        self.assertEqual(look, exp_look)

        look = fract4dc.ff_look_vector(self.ff,19.5,14.5)
        big_look = [0, 0, 40.0, 0.0]
        mag = math.sqrt(sum([x*x for x in big_look]))
        exp_look = tuple([x/mag for x in big_look])
        self.assertNearlyEqual(look, exp_look)
        
        #f.draw(image)
        #fract4dc.image_save(image,"hs.tga")

    def testVector(self):
        pass
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

