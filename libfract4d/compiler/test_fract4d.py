#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path

sys.path.append("build/lib.linux-i686-2.2") # FIXME
import fract4d

class FractalSite:
    def __init__(self):
        self.status_list = []
        self.progress_list = []
        self.parameters_times = 0
        self.image_list = []
        
    def status_changed(self,val):
        #print "status: %d" % val
        self.status_list.append(val)
        
    def progress_changed(self,d):
        #print "progress:", d
        self.progress_list.append(d)

    def is_interrupted(self):
        return False

    def parameters_changed(self):
        #print "params changed"
        self.parameters_times += 1
        
    def image_changed(self,x1,y1,x2,y2):
        #print "image: %d %d %d %d" %  (x1, x2, y1, y2)
        self.image_list.append((x1,y1,x2,y2))
        
class PfTest(unittest.TestCase):

    def compileMandel(self):
        self.compiler.load_formula_file("./gf4d.frm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-pf.so")
        
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

    def testImage(self):
        image = fract4d.image_create(40,30)
        fract4d.image_resize(image,80,60)

    def testCalc(self):
        image = fract4d.image_create(40,30)
        siteobj = FractalSite()
        site = fract4d.site_create(siteobj)

        self.compileMandel()
        handle = fract4d.pf_load("./test-pf.so")
        pfunc = fract4d.pf_create(handle)
        fract4d.pf_init(pfunc,0.001,[0.5])
        cmap = fract4d.cmap_create(
            [(0.0,255,0,100,255), (1.0, 0, 255, 50, 255)])
        fract4d.calc(
            [0.0] * 12,
            0,
            100,
            1,
            pfunc,
            cmap,
            0,
            image,
            site)

        self.failUnless(siteobj.progress_list[-1]== 0.0 and \
                         siteobj.progress_list[-2]== 1.0)

        self.failUnless(siteobj.image_list[-1]==(0,0,40,30))

        self.failUnless(siteobj.status_list[0]== 1 and \
                         siteobj.status_list[-1]== 0)

    def disabled_testWithColors(self):
        self.compileMandel()
        self.compiler.load_formula_file("./gf4d.cfrm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot",
                                      "gf4d.cfrm","default")
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-pfc.so")
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


