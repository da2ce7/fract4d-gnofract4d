#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path
import struct
import math

import fract4dc

class FractalSite:
    def __init__(self):
        self.status_list = []
        self.progress_list = []
        self.iters_list = []
        self.image_list = []
        
    def status_changed(self,val):
        #print "status: %d" % val
        self.status_list.append(val)
        
    def progress_changed(self,d):
        #print "progress:", d
        self.progress_list.append(d)

    def is_interrupted(self):
        return False

    def iters_changed(self,iters):
        #print "iters changed to %d" % iters
        self.iters_list.append(iters)
        
    def image_changed(self,x1,y1,x2,y2):
        #print "image: %d %d %d %d" %  (x1, x2, y1, y2)
        self.image_list.append((x1,y1,x2,y2))

class ImageWrapper:
    FATE_SIZE = 4
    COL_SIZE = 3
    OUT=0
    IN=1 | 128 # in pixels have solid bit set
    UNKNOWN=255
    BLACK=[0,0,0]
    WHITE=[255,255,255]
    def __init__(self,xsize,ysize,img):
        self.xsize = xsize
        self.ysize = ysize
        self.fate_buf = fract4dc.image_fate_buffer(img,0,0)
        self.image_buf = fract4dc.image_buffer(img,0,0)
        self.img = img

    def pos(self,x,y,size):
        return size * (y * self.xsize + x)
    
    def get_fate(self,x,y):
        return ord(self.fate_buf[self.pos(x,y,ImageWrapper.FATE_SIZE)])

    def get_all_fates(self,x,y):
        pos = self.pos(x,y,ImageWrapper.FATE_SIZE)
        return map(ord,list(self.fate_buf[pos:pos+ImageWrapper.FATE_SIZE]))

    def get_color(self,x,y):
        pos = self.pos(x,y,ImageWrapper.COL_SIZE)
        return map(ord,list(self.image_buf[pos:pos+ImageWrapper.COL_SIZE]))

    def get_color_index(self,x,y,sub=0):
        return fract4dc.image_get_color_index(self.img,x,y,sub)
    
class PfTest(unittest.TestCase):

    def compileMandel(self):
        self.compiler.file_path.append('../formulas')
        self.compiler.load_formula_file("gf4d.frm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-pf.so")

    def compileColorMandel(self):
        self.compiler.file_path.append('../formulas')
        self.compiler.load_formula_file("gf4d.frm")
        self.compiler.load_formula_file("gf4d.cfrm")
        cf1 = self.compiler.get_colorfunc("gf4d.cfrm","default","cf0")
        self.assertEqual(len(cf1.errors),0)
        self.compiler.compile(cf1)
        
        cf2 = self.compiler.get_colorfunc("gf4d.cfrm","zero","cf1")
        self.assertEqual(len(cf2.errors),0)
        self.compiler.compile(cf2)
        
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")

        self.color_mandel_params = f.symbols.default_params() + \
                                   cf1.symbols.default_params() + \
                                   cf2.symbols.default_params()

        return self.compiler.compile_all(f,cf1,cf2)

    def compileColorDiagonal(self):
        self.compiler.file_path.append('../formulas')
        self.compiler.load_formula_file("test.frm")
        self.compiler.load_formula_file("gf4d.cfrm")
        cf1 = self.compiler.get_colorfunc("gf4d.cfrm","default","cf0")
        self.assertEqual(len(cf1.errors),0)

        
        cf2 = self.compiler.get_colorfunc("gf4d.cfrm","zero","cf1")
        self.assertEqual(len(cf2.errors),0)
        self.compiler.compile(cf2)
        
        f = self.compiler.get_formula("test.frm","test_simpleshape")
        outputfile = self.compiler.compile_all(f,cf1,cf2)

        self.color_diagonal_params = f.symbols.default_params() + \
                                     cf1.symbols.default_params() + \
                                     cf2.symbols.default_params()

        return outputfile
    
    def setUp(self):
        compiler = fc.Compiler()
        self.compiler = compiler
        self.name_of_msg = [
            "PARAMS",
            "IMAGE",
            "PROGRESS",
            "STATUS",
            "PIXEL"
            ]
        
    def tearDown(self):
        pass

    def testBasic(self):
        self.compileMandel()
        handle = fract4dc.pf_load("./test-pf.so")
        pfunc = fract4dc.pf_create(handle)

        fract4dc.pf_init(pfunc,0.001,[4.0, 0.5])

        # a point which doesn't bail out
        result = fract4dc.pf_calc(pfunc,[0.15, 0.0, 0.0, 0.0],100,0,0,0)
        self.assertEqual(result,(100, 1, 0.0,0))
        # one which does
        result = fract4dc.pf_calc(pfunc,[1.0, 1.0, 0.0, 0.0],100,0,0,0)
        self.assertEqual(result,(1,0, 0.0,0)) 

        # one which is already out
        result = fract4dc.pf_calc(pfunc,[17.5, 14.0, 0.0, 0.0],100,0,0,0)
        self.assertEqual(result,(0, 0, 0.0,0)) 

        # without optional args
        result = fract4dc.pf_calc(pfunc,[17.5, 14.0, 0.0, 0.0],100)
        self.assertEqual(result,(0, 0, 0.0,0)) 
        
        pfunc = None
        handle = None

    def testImage(self):
        image = fract4dc.image_create(40,30)
        fract4dc.image_resize(image,80,60)
        buf = fract4dc.image_buffer(image)
        self.assertEqual(len(buf),80*60*3)

        fate_buf = fract4dc.image_fate_buffer(image)
        self.assertEqual(len(fate_buf),80*60*4)
        
        bytes = list(buf)
        self.assertEqual(ord(bytes[0]),200)
        self.assertEqual(ord(bytes[1]),178)
        self.assertEqual(ord(bytes[2]),98)

        fate_bytes = list(fate_buf)
        for fb in fate_bytes:
            self.assertEqual(ord(fb), 255)
            
        self.assertRaises(ValueError,fract4dc.image_buffer, image, -1, 0)
        self.assertRaises(ValueError,fract4dc.image_buffer, image, 80, 0)
        self.assertRaises(ValueError,fract4dc.image_buffer, image, 41, 67)

        self.assertRaises(ValueError,fract4dc.image_fate_buffer, image, -1, 0)
        self.assertRaises(ValueError,fract4dc.image_fate_buffer, image, 80, 0)
        self.assertRaises(ValueError,fract4dc.image_fate_buffer, image, 41, 67)

        buf = fract4dc.image_buffer(image,5,10)
        self.assertEqual(len(buf),80*60*3 - (10*80+5)*3)
        
        buf = fract4dc.image_fate_buffer(image,5,10)
        self.assertEqual(len(buf),80*60*4 - (10*80+5)*4)

    def makeWorkerAndFunc(self, image, cmap):
        siteobj = FractalSite()
        site = fract4dc.site_create(siteobj)

        file = self.compileColorDiagonal()
        handle = fract4dc.pf_load(file)
        pfunc = fract4dc.pf_create(handle)
        fract4dc.pf_init(pfunc,0.001,self.color_diagonal_params)

        fw = fract4dc.fw_create(1,pfunc,cmap,image,site)
        ff = fract4dc.ff_create(
            [0.0, 0.0, 0.0, 0.0,
             4.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            2,
            100,
            0,
            1,
            pfunc,
            cmap,
            0,
            1,
            image,
            site,
            fw)

        return (fw,ff,site,handle,pfunc)

    def assertPixelIs(self,img,x,y,fates,outcolor=None,incolor=None,efate=None):
        self.assertEqual(img.get_all_fates(x,y), fates)
        (r,g,b) = (0,0,0)
        nsubpixels = 0
        for i in xrange(img.FATE_SIZE):
            fate = fates[i]
            if fate==img.UNKNOWN and efate != None:
                fate = efate
            if fate == img.OUT:
                if outcolor == None:
                    color = img.WHITE
                else:
                    color = outcolor
            else:
                if incolor == None:
                    color = img.BLACK
                else:
                    color = incolor

            if fate == img.IN:
                index = 0.0
            elif fate == img.OUT:
                index = 0.0
            else:
                continue
            
            r += color[0]; g += color[1]; b += color[2]
            nsubpixels += 1
            if fate != img.UNKNOWN and efate==None:
                findex = img.get_color_index(x,y,i)
                self.assertEqual(
                    findex,index,
                    "unexpected index %.17f for subpixel %d with fate %d" % (findex,i,fate))

        color = [r//nsubpixels, g//nsubpixels, b//nsubpixels]
        
        self.assertEqual(img.get_color(x,y),color)
        
    def printStuff(self):
        print
        for y in xrange(xsize):
            lower = ""
            upper = ""
            for x in xrange(ysize):
                fract4dc.fw_pixel(fw,x,y,1,1)
                fract4dc.fw_pixel_aa(fw,x,y)
                fates = iw.get_all_fates(x,y)
                upper += "%2x%2x " % (fates[0],fates[1])
                lower += "%2x%2x " % (fates[2],fates[3])
            print upper
            print lower
        print

    def testFractWorker(self):
        xsize = 8
        ysize = 8
        image = fract4dc.image_create(xsize,ysize)
        iw = ImageWrapper(xsize,ysize,image)
        
        cmap = fract4dc.cmap_create([(1.0, 255, 255, 255, 255)])

        fract4dc.cmap_set_solid(cmap,0,0,0,0,255)
        fract4dc.cmap_set_solid(cmap,1,0,0,0,255)
        
        (fw,ff,site,handle,pfunc) = self.makeWorkerAndFunc(image,cmap)

        # check clear() works
        fract4dc.image_clear(image)
        fate_buf = fract4dc.image_fate_buffer(image)
        buf = fract4dc.image_buffer(image)
        self.assertEqual(list(fate_buf), [chr(255)] * 4 * xsize * ysize)
        
        # draw 1 pixel, check it's set properly
        fract4dc.fw_pixel(fw,0,0,1,1)
        self.assertPixelIs(iw,0,0,[iw.OUT]+[iw.UNKNOWN]*3)

        fract4dc.fw_pixel(fw,0,4,1,1)
        self.assertPixelIs(iw,0,4,[iw.IN]+[iw.UNKNOWN]*3)
        
        # draw it again, check no change.
        fract4dc.fw_pixel(fw,0,0,1,1)
        self.assertPixelIs(iw,0,0,[iw.OUT]+[iw.UNKNOWN]*3)

        # draw & antialias another pixel
        fract4dc.fw_pixel(fw,2,2,1,1)
        fract4dc.fw_pixel_aa(fw,2,2)
        self.assertPixelIs(iw,2,2,[iw.OUT, iw.OUT, iw.IN, iw.OUT])

        # change cmap, draw same pixel again, check color changes
        cmap = fract4dc.cmap_create(
            [(1.0, 79, 88, 41, 255)])
        fract4dc.cmap_set_solid(cmap,1,100,101,102,255)
        
        (fw,ff,site,handle,pfunc) = self.makeWorkerAndFunc(image,cmap)

        fract4dc.fw_pixel(fw,0,0,1,1)
        self.assertPixelIs(iw,0,0,[iw.OUT]+[iw.UNKNOWN]*3, [79,88,41])

        # redraw antialiased pixel
        fract4dc.fw_pixel_aa(fw,2,2)
        self.assertPixelIs(
            iw,2,2, [iw.OUT, iw.OUT, iw.IN, iw.OUT],
            [79,88,41], [100,101,102])

        # draw large block overlapping existing pixels
        fract4dc.fw_pixel(fw,0,0,4,4)
        self.assertPixelIs(
            iw,0,0, [iw.OUT, iw.UNKNOWN, iw.UNKNOWN, iw.UNKNOWN],
            [79,88,41], [100,101,102])

        self.assertPixelIs(
            iw,3,1, [iw.UNKNOWN]*4,
            [79,88,41], [100,101,102], iw.OUT)        
        
    def testCalc(self):
        xsize = 64
        ysize = int(xsize * 3.0/4.0)
        image = fract4dc.image_create(xsize,ysize)
        siteobj = FractalSite()
        site = fract4dc.site_create(siteobj)

        file = self.compileColorMandel()
        handle = fract4dc.pf_load(file)
        pfunc = fract4dc.pf_create(handle)
        fract4dc.pf_init(pfunc,0.001,self.color_mandel_params)
        cmap = fract4dc.cmap_create(
            [(0.0,0,0,0,255),
             (1/256.0,255,255,255,255),
             (1.0, 255, 255, 255, 255)])
        fract4dc.calc(
            [0.0, 0.0, 0.0, 0.0,
             4.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            0,
            100,
            0,
            1,
            pfunc,
            cmap,
            0,
            1,
            image,
            site)

        self.failUnless(siteobj.progress_list[-1]== 0.0 and \
                         siteobj.progress_list[-2]== 1.0)

        self.failUnless(siteobj.image_list[-1]==(0,0,xsize,ysize))

        self.failUnless(siteobj.status_list[0]== 1 and \
                         siteobj.status_list[-1]== 0)

        self.failUnless(not os.path.exists("test.tga"))
        fract4dc.image_save(image,"test.tga")
        self.failUnless(os.path.exists("test.tga"))
        os.remove('test.tga')

        # fate of all non-aa pixels should be known, aa-pixels unknown
        #self.print_fates(image,xsize,ysize)
        fate_buf = fract4dc.image_fate_buffer(image)
        i = 0
        for byte in fate_buf:
            d = fract4dc.image_get_color_index(
                    image,
                    (i % (4 * xsize)) / 4,
                    i / (4 * xsize),
                    i % 4)
            
            if i % 4 == 0:
                # no-aa
                self.assertNotEqual(ord(byte), 255,
                                    "pixel %d is %d" % (i,ord(byte)))
                self.assertNotEqual("%g" % d,"inf")
            else:
                self.assertEqual(ord(byte), 255)
                self.assertEqual("%g" % d,"inf")
            i+= 1

    def testAACalc(self):
        xsize = 64
        ysize = int(xsize * 3.0/4.0)
        image = fract4dc.image_create(xsize,ysize)
        siteobj = FractalSite()
        site = fract4dc.site_create(siteobj)

        file = self.compileColorMandel()
        handle = fract4dc.pf_load(file)
        pfunc = fract4dc.pf_create(handle)
        fract4dc.pf_init(pfunc,0.001,self.color_mandel_params)
        cmap = fract4dc.cmap_create(
            [(0.0,0,0,0,255),
             (1/256.0,255,255,255,255),
             (1.0, 255, 255, 255, 255)])
        fract4dc.calc(
            [0.0, 0.0, 0.0, 0.0,
             4.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            1,
            100,
            0,
            1,
            pfunc,
            cmap,
            0,
            1,
            image,
            site)

        # fate of all pixels should be known
        fate_buf = fract4dc.image_fate_buffer(image)
        i = 0
        for byte in fate_buf:
            d = fract4dc.image_get_color_index(
                    image,
                    (i % (4 * xsize)) / 4,
                    i / (4 * xsize),
                    i % 4)

            self.assertNotEqual("%g" % d,"inf", "index %d is %g" % (i,d))
            self.assertNotEqual(ord(byte), 255,
                                "pixel %d is %d" % (i,ord(byte)))
            i+= 1

    def print_fates(self,image,x,y):
        buf = fract4dc.image_fate_buffer(image)
        for i in xrange(len(buf)):
            v = ord(buf[i])
            if v == 255:
                print "U",
            else:
                print v,
                
            if i % (x*4) == 4*x-1:
                print ""
            
    def testRotMatrix(self):
        params = [0.0, 0.0, 0.0, 0.0,
                 1.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        mat = fract4dc.rot_matrix(params)
        self.assertEqual(mat, ((1.0, 0.0, 0.0, 0.0),
                               (0.0, 1.0, 0.0, 0.0),
                               (0.0, 0.0, 1.0, 0.0),
                               (0.0, 0.0, 0.0, 1.0)))

        params[6] = math.pi/2.0
        mat = fract4dc.rot_matrix(params)
        self.assertNearlyEqual(mat, ((0.0, 0.0, 1.0, 0.0),
                                     (0.0, 1.0, 0.0, 0.0),
                                     (-1.0, 0.0, 0.0, 0.0),
                                     (0.0, 0.0, 0.0, 1.0)))
        
    def assertNearlyEqual(self,a,b):
        # check that each element is within epsilon of expected value
        epsilon = 1.0e-12
        for (ra,rb) in zip(a,b):
            for (ca,cb) in zip(ra,rb):
                d = abs(ca-cb)
                self.failUnless(d < epsilon)
                
    def testFDSite(self):
        xsize = 64
        ysize = int(xsize * 3.0/4.0)
        image = fract4dc.image_create(xsize,ysize)
        (rfd,wfd) = os.pipe()
        site = fract4dc.fdsite_create(wfd)

        file = self.compileColorMandel()

        for x in xrange(10):
            handle = fract4dc.pf_load(file)
            pfunc = fract4dc.pf_create(handle)
            fract4dc.pf_init(pfunc,0.001,self.color_mandel_params)
            cmap = fract4dc.cmap_create(
                [(0.0,0,0,0,255),
                 (1/256.0,255,255,255,255),
                 (1.0, 255, 255, 255, 255)])

            #print x
            fract4dc.async_calc(
                [0.0, 0.0, 0.0, 0.0,
                 4.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                0,
                100,
                0,
                1,
                pfunc,
                cmap,
                0,
                1,
                image,
                site)

            nrecved = 0
            while True:
                nb = 5*4
                if nrecved == x:
                    #print "hit message count"
                    fract4dc.interrupt(site)
                
                bytes = os.read(rfd,nb)
                if len(bytes) < nb:
                    self.fail("bad message")
                    break
                (t,p1,p2,p3,p4) = struct.unpack("5i",bytes)
                m = self.name_of_msg[t] 
                #print "msg: %s %d %d %d %d" % (m,p1,p2,p3,p4)
                if m == "STATUS" and p1 == 0:
                    #done
                    #print "done"
                    break
                
                nrecved += 1
                    
    def testDirtyFlagFullRender(self):
        '''Render the same image 2x with different colormaps.

        First, with the dirty flag set for a full redraw.  Second,
        with the dirty flag clear. The end result should be the same
        in both cases'''

        buf1 = self.drawTwice(True)
        buf2 = self.drawTwice(False)

        i=0
        for (a,b) in zip(list(buf1), list(buf2)):
            if a != b:
                print "%s != %s at %d" % (a,b,i)
                #self.assertEqual(a,b)
            i += 1
                    
    def drawTwice(self,is_dirty):
        xsize = 64
        ysize = int(xsize * 3.0/4.0)
        image = fract4dc.image_create(xsize,ysize)
        siteobj = FractalSite()
        site = fract4dc.site_create(siteobj)

        file = self.compileColorMandel()
        handle = fract4dc.pf_load(file)
        pfunc = fract4dc.pf_create(handle)
        fract4dc.pf_init(pfunc,0.001,self.color_mandel_params)

        cmap = fract4dc.cmap_create(
            [(1.0, 255, 255, 255, 255)])
        
        fract4dc.calc(
            [0.0, 0.0, 0.0, 0.0,
             4.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            0,
            100,
            0,
            1,
            pfunc,
            cmap,
            0,
            1,
            image,
            site, is_dirty)

        #print "1st pass %s" % is_dirty
        fract4dc.image_save(image, "pass1%d.tga" % is_dirty)
        #self.print_fates(image,xsize,ysize)
        
        cmap = fract4dc.cmap_create(
            [(1.0, 76, 49, 189, 255)])

        fract4dc.calc(
            [0.0, 0.0, 0.0, 0.0,
             4.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            0,
            100,
            0,
            1,
            pfunc,
            cmap,
            0,
            1,
            image,
            site, is_dirty)

        #print "2nd pass %s" % is_dirty
        #self.print_fates(image,xsize,ysize)
        fract4dc.image_save(image, "pass2%d.tga" % is_dirty)
        
        return fract4dc.image_buffer(image)
        
    def testMiniTextRender(self):
        self.compileMandel()
        handle = fract4dc.pf_load("./test-pf.so")
        pfunc = fract4dc.pf_create(handle)
        fract4dc.pf_init(pfunc,0.001,[4.0])
        image = []
        for y in xrange(-20,20):
            line = []
            for x in xrange(-20,20):
                (iter,fate,dist,solid) = fract4dc.pf_calc(pfunc,[x/10.0,y/10.0,0,0],100)
                if(fate == 1):
                    line.append("#")
                else:
                    line.append(" ")
            image.append(string.join(line,""))
        printable_image = string.join(image,"\n")
        self.assertEqual(printable_image[0], " ", printable_image)
        self.assertEqual(printable_image[20*41+20],"#", printable_image) # in the middle
        #print printable_image # shows low-res mbrot in text mode 
        
    def testBadLoad(self):
        # wrong arg type/number
        self.assertRaises(TypeError,fract4dc.pf_load,1)
        self.assertRaises(TypeError,fract4dc.pf_load,"foo","bar")

        # nonexistent
        self.assertRaises(ValueError,fract4dc.pf_load,"garbage.xxx")

        # not a DLL
        self.assertRaises(ValueError,fract4dc.pf_load,"test_pf.py")

    def testBadInit(self):
        self.compileMandel()
        handle = fract4dc.pf_load("./test-pf.so")
        pfunc = fract4dc.pf_create(handle)
        self.assertRaises(TypeError,fract4dc.pf_init,pfunc,0.001,72)
        self.assertRaises(ValueError,fract4dc.pf_init,7,0.00,[0.4])
        self.assertRaises(ValueError,fract4dc.pf_init,pfunc,0.001,[0.0]*21)
        pfunc = None
        handle = None

    def testBadCalc(self):
        self.compileMandel()
        handle = fract4dc.pf_load("./test-pf.so")
        pfunc = fract4dc.pf_create(handle)
        fract4dc.pf_init(pfunc,0.001,[])
        self.assertRaises(ValueError,fract4dc.pf_calc,0,[1.0,2.0,3.0,4.0],100)
        self.assertRaises(TypeError,fract4dc.pf_calc,pfunc,[1.0,2.0,3.0],100)
        pfunc = None

    def testShutdownOrder(self):
        self.compileMandel()
        handle = fract4dc.pf_load("./test-pf.so")
        pfunc = fract4dc.pf_create(handle)
        pfunc2 = fract4dc.pf_create(handle)
        handle = None
        pfunc = None
        pfunc2 = None

    def testCmap(self):
        cmap = fract4dc.cmap_create(
            [(0.0,255,0,100,255), (1.0, 0, 255, 50, 255)])

        self.assertEqual(fract4dc.cmap_lookup(cmap,0.0), (255,0,100,255))
        self.assertEqual(fract4dc.cmap_lookup(cmap,1.0-1e-10), (0,254,50,255))
        self.assertEqual(fract4dc.cmap_lookup(cmap,1.0), (0,255,50,255))
        self.assertEqual(fract4dc.cmap_lookup(cmap,0.5), (127,127,75,255))
        self.assertEqual(fract4dc.cmap_lookup(cmap,0.00000001), (254,0,99,255))
        
        cmap = fract4dc.cmap_create(
            [(0.0,255,0,100,255)])
        expc1 = (255,0,100,255)
        self.assertEqual(fract4dc.cmap_lookup(cmap,0.0),expc1)
        self.assertEqual(fract4dc.cmap_lookup(cmap,1.0),expc1)
        self.assertEqual(fract4dc.cmap_lookup(cmap,0.4),expc1)
        
        colors = []
        for i in xrange(256):
            colors.append((i/255.0,(i*17)%256,255-i,i/2,i/2+127))

        cmap = fract4dc.cmap_create(colors)
        for i in xrange(256):
            self.assertEqual(fract4dc.cmap_lookup(cmap,i/255.0),colors[i][1:],i)

        #fract4dc.cmap_set_solid(cmap,1,240,37,191,255)

    def testTransfers(self):
        # test fates
        cmap = fract4dc.cmap_create(
            [(0.0,33,33,33,255)])

        # make inner transfer func none
        fract4dc.cmap_set_transfer(cmap,1,0)
        
        # inside should be all-black by default, outside should never be
        index = 0.0
        while index < 2.0: 
            color = fract4dc.cmap_fate_lookup(cmap,1,index,0)
            self.assertEqual(color,(0,0,0,255))
            color = fract4dc.cmap_fate_lookup(cmap,0,index,0)
            self.assertEqual(color,(33,33,33,255))            
            index += 0.1

        # test setting solid colors and transfers
        fract4dc.cmap_set_solid(cmap,0,166,166,166,255)
        fract4dc.cmap_set_solid(cmap,1,177,177,177,255)
        fract4dc.cmap_set_transfer(cmap,0,0)
        
        index = 0.0
        while index < 2.0: 
            color = fract4dc.cmap_fate_lookup(cmap,1,index,0)
            self.assertEqual(color,(177,177,177,255))
            color = fract4dc.cmap_fate_lookup(cmap,0,index,0)
            self.assertEqual(color,(166,166,166,255))            
            index += 0.1

        # make inner linear
        fract4dc.cmap_set_transfer(cmap,1,1)

        index = 0.0
        while index < 2.0: 
            color = fract4dc.cmap_fate_lookup(cmap,1,index,0)
            self.assertEqual(color,(33,33,33,255))
            color = fract4dc.cmap_fate_lookup(cmap,0,index,0)
            self.assertEqual(color,(166,166,166,255))            
            index += 0.1

        # test that solid overrides
        color = fract4dc.cmap_fate_lookup(cmap,1,0.1,1)
        self.assertEqual(color,(177,177,177,255))
        color = fract4dc.cmap_fate_lookup(cmap,0,0.1,1)
        self.assertEqual(color,(166,166,166,255))
        
        

def suite():
    return unittest.makeSuite(PfTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


