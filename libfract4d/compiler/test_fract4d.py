#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path

sys.path.append("build/lib.linux-i686-2.2") # FIXME
import fract4d

class PfTest(unittest.TestCase):

    def compileMandel(self):
        self.compiler.load_formula_file("./gf4d.frm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        self.compiler.generate_code(f,"test-pf.so")
        
    def setUp(self):
        compiler = fc.Compiler()
        self.compiler = compiler
        
    def tearDown(self):
        pass

    def testBasic(self):
        self.compileMandel()
        handle = fract4d.pf_load("./test-pf.so")
        pfunc = fract4d.pf_create(handle)

        # 1 param
        fract4d.pf_init(pfunc,0.001,[0.5])
        # empty param array
        fract4d.pf_init(pfunc,0.001,[])

        # a point which doesn't bail out
        result = fract4d.pf_calc(pfunc,[0.15, 0.0, 0.0, 0.0],100,100,0,0,0)
        self.assertEqual(result,(100, 1, 0.0))
        # one which does
        result = fract4d.pf_calc(pfunc,[1.0, 1.0, 0.0, 0.0],100,100,0,0,0)
        self.assertEqual(result,(1,0, 0.0)) 

        # one which is already out
        result = fract4d.pf_calc(pfunc,[17.5, 14.0, 0.0, 0.0],100,100,0,0,0)
        self.assertEqual(result,(0, 0, 0.0)) 


        # without optional args
        result = fract4d.pf_calc(pfunc,[17.5, 14.0, 0.0, 0.0],100,100)
        self.assertEqual(result,(0, 0, 0.0)) 
        
        pfunc = None
        handle = None

    def disabled_testWithColors(self):
        self.compileMandel()
        self.compiler.load_formula_file("./gf4d.cfrm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot",
                                      "gf4d.cfrm","default")
        self.compiler.generate_code(f,"test-pfc.so")
        handle = fract4d.pf_load("./test-pfc.so")
        pfunc = fract4d.pf_create(handle)
        fract4d.pf_init(pfunc,0.001,[])
        result = fract4d.pf_calc(pfunc,[1.5,0,0,0],100,100)
        self.assertEqual(result,(2,0,2.0/256.0))
                         
    def testMiniTextRender(self):
        self.compileMandel()
        handle = fract4d.pf_load("./test-pf.so")
        pfunc = fract4d.pf_create(handle)
        fract4d.pf_init(pfunc,0.001,[])
        image = []
        for y in xrange(-20,20):
            line = []
            for x in xrange(-20,20):
                (iter,fate,dist) = fract4d.pf_calc(pfunc,[x/10.0,y/10.0,0,0],100,100)
                if(fate == 1):
                    line.append("#")
                else:
                    line.append(" ")
            image.append(string.join(line,""))
        printable_image = string.join(image,"\n")
        self.assertEqual(printable_image[0], " ")
        self.assertEqual(printable_image[20*41+20],"#") # in the middle
        #print printable_image # shows low-res mbrot in text mode 
        
    def testBadLoad(self):
        # wrong arg type/number
        self.assertRaises(TypeError,fract4d.pf_load,1)
        self.assertRaises(TypeError,fract4d.pf_load,"foo","bar")

        # nonexistent
        self.assertRaises(ValueError,fract4d.pf_load,"garbage.xxx")

        # not a DLL
        self.assertRaises(ValueError,fract4d.pf_load,"test_pf.py")

    def testBadInit(self):
        self.compileMandel()
        handle = fract4d.pf_load("./test-pf.so")
        pfunc = fract4d.pf_create(handle)
        self.assertRaises(TypeError,fract4d.pf_init,pfunc,0.001,72)
        self.assertRaises(ValueError,fract4d.pf_init,7,0.00,[0.4])
        self.assertRaises(ValueError,fract4d.pf_init,pfunc,0.001,[0.0]*21)
        pfunc = None
        handle = None

    def testBadCalc(self):
        self.compileMandel()
        handle = fract4d.pf_load("./test-pf.so")
        pfunc = fract4d.pf_create(handle)
        fract4d.pf_init(pfunc,0.001,[])
        self.assertRaises(ValueError,fract4d.pf_calc,0,[1.0,2.0,3.0,4.0],100,100)
        self.assertRaises(TypeError,fract4d.pf_calc,pfunc,[1.0,2.0,3.0],100,100)
        pfunc = None

    def testShutdownOrder(self):
        self.compileMandel()
        handle = fract4d.pf_load("./test-pf.so")
        pfunc = fract4d.pf_create(handle)
        pfunc2 = fract4d.pf_create(handle)
        handle = None
        pfunc = None
        pfunc2 = None

    def testCmap(self):
        cmap = fract4d.cmap_create(
            [(0.0,255,0,100,255), (1.0, 0, 255, 50, 255)])

        self.assertEqual(fract4d.cmap_lookup(cmap,0.0), (255,0,100,255))
        self.assertEqual(fract4d.cmap_lookup(cmap,1.0), (0,255,50,255))
        self.assertEqual(fract4d.cmap_lookup(cmap,0.5), (127,127,75,255))
        self.assertEqual(fract4d.cmap_lookup(cmap,-784.1), (255,0,100,255))
        self.assertEqual(fract4d.cmap_lookup(cmap,1.0E37), (0,255,50,255))
        
        cmap = fract4d.cmap_create(
            [(0.0,255,0,100,255)])
        expc1 = (255,0,100,255)
        self.assertEqual(fract4d.cmap_lookup(cmap,0.0),expc1)
        self.assertEqual(fract4d.cmap_lookup(cmap,1.0),expc1)
        self.assertEqual(fract4d.cmap_lookup(cmap,0.4),expc1)
        
        colors = []
        for i in xrange(256):
            colors.append((i/255.0,(i*17)%256,255-i,i/2,i/2+127))

        cmap = fract4d.cmap_create(colors)
        for i in xrange(256):
            self.assertEqual(fract4d.cmap_lookup(cmap,i/255.0),colors[i][1:])
        
def suite():
    return unittest.makeSuite(PfTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


