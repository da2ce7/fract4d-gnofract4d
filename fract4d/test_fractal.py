#!/usr/bin/env python

import string
import unittest
import StringIO
import sys
import math

import fc
import fractal
import fract4dc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.load_formula_file("./gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")
        

class FctTest(unittest.TestCase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp

    def tearDown(self):
        pass

    def testRead(self):
        file = '''gnofract4d parameter file
version=1.9
bailout=5.1
x=0.0891
y=-0.314159
z=0.14
w=0.21
size=4.1
xy=0.00000001
xz=0.1
xw=0.09
yz=-0.1
yw=0.4
zw=0.2
maxiter=259
antialias=1
bailfunc=0
inner=2
outer=1
[function]
function=Mandelbar
[endsection]
[colorizer]=0
colorizer=1
colordata=000000548878548878548878588c78588c7c588c7c58907c5890805c94805c94805c94805c98845c98845c9884609c88609c88609c8860a08860a08c60a08c64a48c64a49064a49064a89064a89464a89468ac9468ac9468b09868b09868b0986cb49c6cb49c6cb49c6cb89c6cb8a06cb8a070bca070bca470bca470c0a470c0a470c0a874c4a874c4a874c4ac74c8ac74c8ac78ccb0303c38303c38343c38343c383840383840383c40383c403840403840443c44443c44443c48443c48443c4c483c4c483c50483c50483c544840544c40584c40584c405c4c405c4c406050406050406450406450406850446854446c54446c54447054447054447058447458447458447858487858487c5c487c5c48805c48805c48845c4884604888604888604c8c604c8c604c90644c90644c94644c94644c98684c98684c9c684c9c6850a06850a06c50a46c50a46c50a86c50a86c50ac7050ac7050b07054b07054b47054b47454b47454b87454b87454bc7454bc7854c07858c07858c47858c47858c87c58c87c58cc7c58cc7c58d07c58d08058d4805cd4805cd8805cd8805cdc845cdc845ce0845ce0845ce4845ce48860e88860e88860ec8860ec8860f08c60f08c60f48c60f48c60f89064303c3830403c30403c304440344440344844344848344c48384c4c38504c3850503854503c54543c58583c58583c5c5c3c5c5c406060406064406464406468446868446c6c446c6c44707048707448747448747848787848787c4c7c7c4c7c804c80844c808450848850848850888c508890548c90548c9454909454909854949858949c5898a0589ca0589ca45ca0a45ca0a8303c385ca4a85ca4ac60a8b060a8b060acb460acb460b0b864b0bc64b4bc64b4c064b8c068b8c468bcc468bcc868c0cc6cc0cc6cc4d06cc4d06cc8d470ccd870c8d870c4d870c0d86cbcdc6cb8dc6cb4dc68b0dc68ace068a8e068a4e064a0e0649ce46498e46090e4608ce46088e86084e85c80e85c7ce85c78ec5874ec5870ec586cec5868f05464f05460f0545cf05054f45054f45054f05058ec5458ec5458e8
[endsection]
[colorizer]=1
colorizer=1
colordata=30303044fc0094949438f4149090902ce82c8c8c8c24d84488888818cc5c8484840cc07480808000b08c7c7c7c0088a8787878005cc07474740038d8707070000cf46c6c6c1800e46868683800c46464645800a46060607800845c5c5c9c0060585858bc0040545454dc0020505050fc00004c4c4cfc1800484848fc3800444444fc5800404040fc78003c3c3cfc9800383838fcb800343434fcd800303030fcf8002c2c2ce4fc00282828c4fc00242424a4fc0020202084fc001c1c1c64fc0018181844fc0014141438f4141010102ce82c0c0c0c24d84408080818cc5c0404040cc07400000000b08c009c9c0000000070b4040404004ccc0808080020e80c0c0c0800f41010102800d41414144800b41818186800941c1c1c8c0070202020ac0050242424cc0030282828ec00102c2c2cfc0800303030fc2800343434fc4800383838fc68003c3c3cfc8800404040fca800444444fcc800484848fce8004c4c4cf4fc00505050d4fc00545454b4fc0058585894fc005c5c5c74fc0060606054fc006464643cf80868686834ec206c6c6c28e0387070701cd45074747410c86878787808bc807c7c7c009c9c8080800070b4848484004ccc8888880020e88c8c8c0800f49090902800d49494944800b49898986800949c9c9c8c0070a0a0a0ac0050a4a4a4cc0030a8a8a8ec0010acacacfc0800b0b0b0fc2800b4b4b4fc4800b8b8b8fc6800bcbcbcfc8800c0c0c0fca800c4c4c4fcc800c8c8c8fce800ccccccf4fc00d0d0d0d4fc00d4d4d4b4fc00d8d8d894fc00dcdcdc74fc00e0e0e054fc00e4e4e43cf808e8e8e834ec20ececec28e038f0f0f01cd450f4f4f410c868fcfcfc08bc80fcfcfc009c9cf8f8f80070b4f4f4f40038d8f0f0f0000cf4ececec1800e4e8e8e83800c4e4e4e45800a4e0e0e0780084dcdcdc9c0060d8d8d8bc0040d4d4d4dc0020d0d0d0fc0000ccccccfc1800c8c8c8fc3800c4c4c4fc5800c0c0c0fc7800bcbcbcfc9800b8b8b8fcb800b4b4b4fcd800b0b0b0fcf800acacace4fc00a8a8a8c4fc00a4a4a4a4fc00a0a0a084fc009c9c9c64fc00989898
[endsection]
[colorizer]=2
colorizer=1
colordata=0000000000a80400ac0408ac040cac0410ac0814b00818b0081cb00c20b00c24b41028b8102cb81430b81434bc1838c0183cc01c40c01c44c42048c8204cc82450c82454cc2858d0285cd02c60d02c64d43068d8306cd83470d83474dc3878e03c7ce03c80e04084e44088e84484e84488e8448ce84490e84894ec4898f04c9cf04ca0f050a4f450a8f854acf854b0f8287c00287c002c7c002c7c002c7c042c7c042c80042c800430800430800430800830800830840830840834840834840838840c38840c3c840c3c840c3c880c3c880c3c88103c88103c8c103c8c10408c10408c10408c14408c1440901440901444901444901444901844901844941848941848941c48981c4898204c98204c9c20509c20509c2450a02450a02854a02854a42858a42858a42c58a82c58a8305ca8305cac3060ac3060ac3460b03464b03464b03864b43864b43868b43c68b83c68b8406cb8406cbc406cbc4470bc4470bc4870c04870c04c74c04c74c44c74c45078c45078c85078c8547cc8547ccc547ccc5880cc5880d05880d05c84d05c84d45c88d45c88d46088d86088d8648cd8648cdc648cdc6890dc6890e06890e06c94e06c94e46c98e46c98e46c9ce46c9ce46ca0e46ca4e46ca8e46ca8e46cace46cace46cb0e46cb0e46cb4e46cb4e46cb8e46cb8e46cbce46cbce46cc0e46cc4e46cc4e46cc8e46ccce46ccce46cd0e46cd0e46cd4e46cd4e46cd8e46cdce46cdce46ce0e46ce4e46ce4e46ce8e46ce8e46ce8e468e8e468e8e464e8e464e8e460e8e460e8e45ce8e05ce8e05ce8dc58e8d854e8d850e8d450e8d44ce8d04ce8cc48e8cc44e8c844e8c840e8c840e8c440e8c43ce8c03ce8c038e8bc38e8bc34e8b834e8b830e8b430e8b42ce8b42ce8b02ce8b02ce8b028e8b028e8ac28e8ac24e8a824e8a824e4a420e4a420e4a020e4a020e09c1ce09818e09818e09414dc9414dc8c10dc8c10dc8410d88410d87c08d87c08d87408808080808080fcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcc0c0c0c0c0c0fcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfc
[endsection]
[colorizer]=3
colorizer=1
colordata=0000000000a80400ac0408ac040cac0410ac0814b00818b0081cb00c20b00c24b41028b8102cb81430b81434bc1838c0183cc01c40c01c44c42048c8204cc82450c82454cc2858d0285cd02c60d02c64d43068d8306cd83470d83474dc3878e03c7ce03c80e04084e44088e84484e84488e8448ce84490e84894ec4898f04c9cf04ca0f050a4f450a8f854acf854b0f8287c00287c002c7c002c7c002c7c042c7c042c80042c800430800430800430800830800830840830840834840834840838840c38840c3c840c3c840c3c880c3c880c3c88103c88103c8c103c8c10408c10408c10408c14408c1440901440901444901444901444901844901844941848941848941c48981c4898204c98204c9c20509c20509c2450a02450a02854a02854a42858a42858a42c58a82c58a8305ca8305cac3060ac3060ac3460b03464b03464b03864b43864b43868b43c68b83c68b8406cb8406cbc406cbc4470bc4470bc4870c04870c04c74c04c74c44c74c45078c45078c85078c8547cc8547ccc547ccc5880cc5880d05880d05c84d05c84d45c88d45c88d46088d86088d8648cd8648cdc648cdc6890dc6890e06890e06c94e06c94e46c98e46c98e46c9ce46c9ce46ca0e46ca4e46ca8e46ca8e46cace46cace46cb0e46cb0e46cb4e46cb4e46cb8e46cb8e46cbce46cbce46cc0e46cc4e46cc4e46cc8e46ccce46ccce46cd0e46cd0e46cd4e46cd4e46cd8e46cdce46cdce46ce0e46ce4e46ce4e46ce8e46ce8e46ce8e468e8e468e8e464e8e464e8e460e8e460e8e45ce8e05ce8e05ce8dc58e8d854e8d850e8d450e8d44ce8d04ce8cc48e8cc44e8c844e8c840e8c840e8c440e8c43ce8c03ce8c038e8bc38e8bc34e8b834e8b830e8b430e8b42ce8b42ce8b02ce8b02ce8b028e8b028e8ac28e8ac24e8a824e8a824e4a420e4a420e4a020e4a020e09c1ce09818e09818e09414dc9414dc8c10dc8c10dc8410d88410d87c08d87c08d87408808080808080fcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcc0c0c0c0c0c0fcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfcfc
[endsection]
'''
        f = fractal.T(self.compiler);
        f.loadFctFile(StringIO.StringIO(file))

        self.assertEqual(f.params[f.XCENTER],0.0891)
        self.assertEqual(f.params[f.YCENTER],-0.314159)
        self.assertEqual(f.params[f.ZCENTER],0.14)
        self.assertEqual(f.params[f.WCENTER],0.21)
        self.assertEqual(f.params[f.MAGNITUDE],4.1)
        self.assertEqual(f.params[f.XYANGLE],0.00000001)
        self.assertEqual(f.params[f.XZANGLE],0.1)
        self.assertEqual(f.params[f.XWANGLE],0.09)
        self.assertEqual(f.params[f.YZANGLE],-0.1)
        self.assertEqual(f.params[f.YWANGLE],0.4)
        self.assertEqual(f.params[f.ZWANGLE],0.2)

        self.assertEqual(f.bailout,5.1)
        self.assertEqual(f.funcName,"Mandelbar")
        self.assertEqual(f.maxiter, 259)
        self.assertEqual(len(f.colorlist),255)
        self.assertEqual(f.colorlist[0][0],0.0)
        self.assertEqual(f.colorlist[-1][0],1.0)
        
        sofile = f.compile()
        image = fract4dc.image_create(40,30)
        f.draw(image)
        
    def assertNearlyEqual(self,a,b):
        # check that each element is within epsilon of expected value
        epsilon = 1.0e-12
        for (ra,rb) in zip(a,b):
            d = abs(ra-rb)
            self.failUnless(d < epsilon,"%f != %f (by %f)" % (ra,rb,d))

    def testRelocation(self):
        f = fractal.T(self.compiler)
        
        f.compile()
        (w,h) = (40,30)
        image = fract4dc.image_create(w,h)

        # zoom
        f.relocate(0.0,0.0,2.0)
        tparams = [0.0] * 11
        tparams[f.MAGNITUDE] = 8.0
        self.assertNearlyEqual(f.params,tparams)

        # relocate
        f.relocate(1.0,2.0,1.0)
        tparams[f.XCENTER] = 8.0
        tparams[f.YCENTER] = 16.0
        self.assertNearlyEqual(f.params,tparams)

        # rotated relocation
        f.relocate(-1.0,-2.0,1.0)
        f.params[f.XYANGLE]= -math.pi/2.0
        f.relocate(1.0,2.0,1.0)
        tparams[f.XCENTER] = -16.0
        tparams[f.YCENTER] = 8.0
        tparams[f.XYANGLE] = -math.pi/2.0
        
        self.assertNearlyEqual(f.params,tparams)

        # Julia relocation
        f.relocate(-1.0,-2.0,1.0)
        f.params[f.XYANGLE]= 0
        f.params[f.XZANGLE] = f.params[f.YWANGLE] = math.pi/2.0
        f.relocate(1.0,2.0,1.0)

        tparams = [0.0] * 11
        tparams[f.MAGNITUDE] = 8.0
        tparams[f.ZCENTER] = 8.0
        tparams[f.WCENTER] = 16.0
        tparams[f.XZANGLE] = tparams[f.YWANGLE] = math.pi/2.0
        
        self.assertNearlyEqual(f.params,tparams)
        
    def testDefaultFractal(self):
        f = fractal.T(self.compiler)
        
        # check defaults
        self.assertEqual(f.params[f.XCENTER],0.0)
        self.assertEqual(f.params[f.YCENTER],0.0)
        self.assertEqual(f.params[f.ZCENTER],0.0)
        self.assertEqual(f.params[f.WCENTER],0.0)
        self.assertEqual(f.params[f.MAGNITUDE],4.0)
        self.assertEqual(f.params[f.XYANGLE],0.0)
        self.assertEqual(f.params[f.XZANGLE],0.0)
        self.assertEqual(f.params[f.XWANGLE],0.0)
        self.assertEqual(f.params[f.YZANGLE],0.0)
        self.assertEqual(f.params[f.YWANGLE],0.0)
        self.assertEqual(f.params[f.ZWANGLE],0.0)
        self.assertEqual(f.bailout,4.0)

        f.compile()
        (w,h) = (40,30)
        image = fract4dc.image_create(w,h)
        f.draw(image)

        buf = fract4dc.image_buffer(image,0,0)

        # corners must be white
        self.assertWhite(buf,0,0,w)
        self.assertWhite(buf,w-1,0,w)
        self.assertWhite(buf,0,h-1,w)
        self.assertWhite(buf,w-1,h-1,w)

        # center is black
        self.assertBlack(buf,w/2,h/2,w)        

        # and vertically symmetrical
        for x in xrange(w):
            for y in xrange(h/2):
                apos = (y*w+x)*3
                bpos = ((h-y-1)*w+x)*3
                a = buf[apos:apos+3]
                b = buf[bpos:bpos+3]
                self.assertEqual(a,b)

    def testReset(self):
        # test that formula's defaults are applied
        f = fractal.T(self.compiler)

        f.params[f.XCENTER] = 777.0
        f.set_formula("test.frm","test_defaults")
        f.reset()
        self.assertEqual(f.maxiter,200)
        self.assertEqual(f.params[f.XCENTER],1.0)
        self.assertEqual(f.params[f.YCENTER],2.0)
        self.assertEqual(f.params[f.ZCENTER],7.1)
        self.assertEqual(f.params[f.WCENTER],2.9)
        self.assertEqual(f.params[f.MAGNITUDE], 8.0)
        
        self.assertEqual(f.params[f.XYANGLE],0.001)
        self.assertEqual(f.params[f.XZANGLE],0.789)
        self.assertEqual(f.title,"Hello World")
        self.assertEqual(f.initparams,[8.0,7.0,1.0])

    def testCircle(self):
        f = fractal.T(self.compiler)

        f.set_formula("test.frm","test_circle")
        f.set_outer("gf4d.cfrm","continuous_potential")
        f.compile()
        f.reset()
        self.assertEqual(f.initparams,[4.0])
        (w,h) = (40,30)
        im = fract4dc.image_create(w,h)
        f.draw(im)

        # check that result is horizontally symmetrical
        buf = fract4dc.image_buffer(im,0,0)
        for y in xrange(h):
            line = list(buf[y*w*3:(y*w+w)*3])
            line.reverse()
            revline = "".join(line)
            self.assertEqual(buf[y*w*3:(y*w+w)*3],revline)

        # and vertically symmetrical
        for x in xrange(w):
            for y in xrange(h/2):
                apos = (y*w+x)*3
                bpos = ((h-y-1)*w+x)*3
                a = buf[apos:apos+3]
                b = buf[bpos:bpos+3]
                self.assertEqual(a,b)

    def testDiagonal(self):
        f = fractal.T(self.compiler)
        #f.pixel_changed = f._pixel_changed
        f.set_formula("test.frm","test_simpleshape")
        f.set_outer("gf4d.cfrm","default")
        f.compile()
        f.reset()
        self.assertEqual(f.initparams,[])
        self.assertEqual(f.antialias,1)
        (w,h) = (30,30)
        im = fract4dc.image_create(w,h)
        f.draw(im)

        buf = fract4dc.image_buffer(im,0,0)
        for y in xrange(h):
            for x in xrange(w):
                if x > y:
                    self.assertWhite(buf,x,y,w)
                elif y > x:
                    self.assertBlack(buf,x,y,w)
                else:
                    # pixels on boundary should be antialiased to 25% grey
                    # because 3 subpixels are white and 1 black
                    self.assertColor(buf,x,y,w,(255*3)/4)
        
    def testCubicRead(self):
        file = '''gnofract4d parameter file
version=1.7
bailout=4
x=0.2488828125
y=-1.3533515625
z=0
w=0
size=0.3365625
xy=0
xz=0
xw=0
yz=0
yw=0
zw=0
maxiter=256
antialias=1
bailfunc=0
inner=2
outer=1
[function]
function=Cubic Mandelbrot
a=(0.34,-0.28)
[endsection]
[colorizer]=0
colorizer=1
colordata=00000044286c441c704c4c7850788058a8885cd48c58cc8858c48858bc8854b48854ac8854a88850a0885098885090845088844c80844c7c844c7484486c84486484485c8448548044508044488044408040388040308040288040248044287c482c7c4c307c4c347c50387c543c7c54407c58447c5c487c60487c604c7c64507c68547c68587c6c5c7c70607c70647c74687c78687c7c6c7c7c707c80747c84787c847c788880788c84788c8878908c78948c789890789894789c9878a09c78a0a078a4a478a8a878a8ac78acac78b0b078b4b478b4b878b8bc78bcc078bcc478c0c878c4cc78c4cc78c0c06cc0b464bcac58bca050b89444b88c3cb48030b47428b06c1cb06014b0580cac5414a85018a4501ca04c249c4c289c482c98483494443890443c8c4044884048883c4c843c548038587c385c78346474346874306c7030706c2c78682c7c64288060288860248c5c249058209854209c501ca04c1ca84c18ac4818b04414b84014bc3c10c03c10c44014bc4018b4401cac4420a444249c442894442c8c48308448347c483874483c6c4c40644c445c4c48544c4c4c50504450543c505834505c2c54602454641c546814546c105068184c6420486028485c3044583840543c3c50443c4c4c38485434445c304060303c682c3870283478243080242c8434387c4044744c4c6c585868646060746c588078548c804c988c44a494409c8c4894884c908050887c5484785c7c7060746c64706468686070645c745c547854507c50488448448844408c3c3890343498302c9c2828a02424a41c1cac1418b01010b4080cb80408bc0810b80c14b81018b8141cb81820b41c24b42028b4242cb42830b02c34b0303cb03440b03844ac3c48ac3c4cac4050ac4454ac4858a84c5ca85060a85468a8586ca45c70a46074a46478a4687ca06c80a07084a07488a0748ca07080a86c74ac6868b4645cb86050c05c44c45838cc582cd05428cc5024cc4c24c84c20c8481cc4441cc44018c04018c058e81c58d82454c82854b83050a83850983c5088444c784c4c6850485858484860443864
[endsection]
'''

        # FIXME: not supported yet
        extra_colorizer = '''[colorizer]=1
colorizer=0
red=0.377255787461439
green=1
blue=0.5543108971162746
[endsection]
'''
        f = fractal.T(self.compiler);
        f.loadFctFile(StringIO.StringIO(file))

        self.assertEqual(f.initparams,[0.34,-0.28,4.0])
                         
    def failBuf(self,buf):
        self.failUnless(False)
        
    def assertWhite(self,buf,x,y,w):
        self.assertColor(buf,x,y,w,255)

    def assertBlack(self,buf,x,y,w):
        self.assertColor(buf,x,y,w,0)

    def assertColor(self,buf,x,y,w,c):
        off = (x+y*w)*3
        r = ord(buf[off])
        g = ord(buf[off+1])
        b = ord(buf[off+2])
        self.assertEqual(r,c)
        self.assertEqual(g,c)
        self.assertEqual(b,c)

    def testSet(self):
        f = fractal.T(self.compiler)
        f.set_formula("gf4d.frm","Mandelbar")
        f.set_inner("gf4d.cfrm","zero")
        f.set_outer("gf4d.cfrm","default")
        f.compile()
        image = fract4dc.image_create(4,3)
        f.draw(image)

    def testFct(self):
        file = open("test.fct")
        f = fractal.T(self.compiler);
        f.loadFctFile(file)
        f.compile()
        image = fract4dc.image_create(64,48)
        f.draw(image)
        #fract4dc.image_save(image,"mandel3.tga")

        
    def testFractalBadness(self):
        f = fractal.T(self.compiler)
        self.assertRaises(ValueError,f.set_formula,"gf4d.frm","xMandelbrot")
        self.assertRaises(ValueError,f.set_inner,"gf4d.cfrm","xdefault")
        self.assertRaises(ValueError,f.set_outer,"gf4d.cfrm","xzero")
        self.assertRaises(ValueError,f.compile)

def suite():
    return unittest.makeSuite(FctTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
