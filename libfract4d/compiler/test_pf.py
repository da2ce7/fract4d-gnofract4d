#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path

sys.path.append("build/lib.linux-i686-2.2") # FIXME
import pf

class PfTest(unittest.TestCase):
    def setUp(self):
        compiler = fc.Compiler()
        compiler.load_formula_file("./gf4d.frm")
        f = compiler.get_formula("gf4d.frm","Mandelbrot")
        compiler.generate_code(f,"test-pf.so")
        self.compiler = compiler
        
    def tearDown(self):
        pass

    def testBasic(self):
        handle = pf.load("./test-pf.so")
        pfunc = pf.create(handle)

        # 1 param
        pf.init(pfunc,0.001,[0.5])
        # empty param array
        pf.init(pfunc,0.001,[])

        # a point which doesn't bail out
        result = pf.calc(pfunc,[0.15,0.0,0.0,0.0],100,100,0,0,0)
        self.assertEqual(result,(100,1,0.0)) 
        # one which does
        result = pf.calc(pfunc,[17.5,14.0,0.0,0.0],100,100,0,0,0)
        self.assertEqual(result,(1,0,0.0)) 

        # without optional args
        result = pf.calc(pfunc,[17.5,14.0,0.0,0.0],100,100)
        self.assertEqual(result,(1,0,0.0)) 
        
        pfunc = None
        handle = None

    def testWithColors(self):
        self.compiler.load_formula_file("./gf4d.cfrm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot",
                                      "gf4d.cfrm","default")
        self.compiler.generate_code(f,"test-pfc.so")
        handle = pf.load("./test-pfc.so")
        pfunc = pf.create(handle)
        pf.init(pfunc,0.001,[])
        result = pf.calc(pfunc,[1.5,0,0,0],100,100)
        self.assertEqual(result,(2,0,2.0/256.0))
                         
    def testMiniTextRender(self):
        handle = pf.load("./test-pf.so")
        pfunc = pf.create(handle)
        pf.init(pfunc,0.001,[])
        image = []
        for y in xrange(-20,20):
            line = []
            for x in xrange(-20,20):
                (iter,fate,dist) = pf.calc(pfunc,[x/10.0,y/10.0,0,0],100,100)
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
        self.assertRaises(TypeError,pf.load,1)
        self.assertRaises(TypeError,pf.load,"foo","bar")

        # nonexistent
        self.assertRaises(ValueError,pf.load,"garbage.xxx")

        # not a DLL
        self.assertRaises(ValueError,pf.load,"test_pf.py")

    def testBadInit(self):
        handle = pf.load("./test-pf.so")
        pfunc = pf.create(handle)
        self.assertRaises(TypeError,pf.init,pfunc,0.001,72)
        self.assertRaises(ValueError,pf.init,7,0.00,[0.4])
        self.assertRaises(ValueError,pf.init,pfunc,0.001,[0.0]*21)
        pfunc = None
        handle = None

    def testBadCalc(self):
        handle = pf.load("./test-pf.so")
        pfunc = pf.create(handle)
        pf.init(pfunc,0.001,[])
        self.assertRaises(ValueError,pf.calc,0,[1.0,2.0,3.0,4.0],100,100)
        self.assertRaises(TypeError,pf.calc,pfunc,[1.0,2.0,3.0],100,100)
        pfunc = None

    def testShutdownOrder(self):
        handle = pf.load("./test-pf.so")
        pfunc = pf.create(handle)
        pfunc2 = pf.create(handle)
        handle = None
        pfunc = None
        pfunc2 = None
def suite():
    return unittest.makeSuite(PfTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


