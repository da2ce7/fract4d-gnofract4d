#!/usr/bin/env python

import string
import unittest
import StringIO
import sys
import math
import copy
import os
import time
import types

import fc
import fractal
import fract4dc
import fracttypes

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../formulas")
g_comp.load_formula_file("gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")
        
g_testfile = '''gnofract4d parameter file
version=2.0
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

g_test2file='''gnofract4d parameter file
version=2.0
[function]
formulafile=gf4d.frm
function=Mandelbrot
@bailfunc=manhattanish
@bailout=1e20
[endsection]
[inner]
formulafile=test.cfrm
function=flat
@_density=2.0
@_offset=0.5
@b=0
@col=(0.09,0.08,0.07,0.06)
@ep=2
@i=78
@myfunc=sqrt
@val=3.3
@val2=(2.0,3.7,6.1,8.9)
[endsection]
[outer]
formulafile=test.cfrm
function=Triangle
@power=3.0
@bailout=1.0e12
[endsection]
[colors]
colorizer=1
solids=[
000000ff
000000ff
]
colorlist=[
0.000000=00000000
1.000000=ffffffff
]
'''

class WarningCatcher:
    def __init__(self):
        self.warnings = []
    def warn(self,msg):
        self.warnings.append(msg)
        
class Test(unittest.TestCase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp
        self.default_flat_params = [
            1.0, #_density
            0.0, #_offset
            1, # bool b
            0.01, 0.02, 0.03, 0.04, # color col
            1, # enum ep
            4, # int i 
            0.4, # float val
            0.7, 0.8, 0.9, 1.0 # hyper val2
            ]

    def tearDown(self):
        pass

    def testRead(self):
        file = g_testfile
        
        f = fractal.T(self.compiler);
        f.loadFctFile(StringIO.StringIO(file))
        self.assertExpectedValues(f)
        
    def testUpsideDown(self):
        file = g_testfile

        file = file.replace('version=2.0','version=1.9',1)
        f = fractal.T(self.compiler);
        f.loadFctFile(StringIO.StringIO(file))
        self.assertEqual(f.params[f.XYANGLE], 0.00000001)
        self.assertEqual(f.yflip, True)
        f.reset()
        self.assertEqual(f.yflip, False)
        
    def assertExpectedValues(self,f):        
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

        self.assertEqual(
            f.initparams[f.order_of_name("@bailout", f.formula.symbols)],5.1)
        
        self.assertEqual(f.funcName,"Mandelbar")
        self.assertEqual(f.funcFile,"gf4d.frm")
        self.assertEqual(f.cfunc_names, ["continuous_potential", "zero"])
        self.assertEqual(f.cfunc_files, ["gf4d.cfrm"]*2)
        
        self.assertEqual(f.maxiter, 259)
        self.failUnless(len(f.gradient.segments)> 1)
        self.assertEqual(f.gradient.segments[0].left,0.0)
        self.assertEqual(f.gradient.segments[-1].right,1.0)
        self.assertEqual(f.solids[0],(0,0,0,255))
        self.assertEqual(f.yflip,False)
        
        sofile = f.compile()
        image = fract4dc.image_create(40,30)
        f.draw(image)

    def testRefresh(self):
        try:
            formula = '''
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
'''
            ff = open("fracttest.frm","w")
            ff.write(formula)
            ff.close()

            f = fractal.T(self.compiler)
            f.set_formula("fracttest.frm","test_circle")

            self.assertEqual(f.get_initparam(1,0), 4.0)
            time.sleep(1.0)
            formula = formula.replace('4.0','6.0')
            ff = open("fracttest.frm","w")
            ff.write(formula)
            ff.close()

            self.assertEqual(f.get_initparam(1,0), 4.0)
            f.refresh()
            self.assertEqual(f.get_initparam(1,0), 6.0)
        finally:
            os.remove("fracttest.frm")

    def testLoadMaliciousFile(self):
        'Try to inject code into a file'
        bad_testfile = '''gnofract4d parameter file
version(2.0,None)+open("foo.txt","w")=2.0
[function]
formulafile=test.frm
function=parse_error
[endsection]
[inner]
formulafile=test.cfrm
function=flat
@myfunc=sqrt
[endsection]
[outer]
formulafile=test.cfrm
function=Triangle
@power=3.0
@bailout=1.0e12
[endsection]
[colors]
colorizer=1
solids=[
000000ff
000000ff
]
colorlist=[
0.000000=00000000
1.000000=ffffffff
]
'''
        f = fractal.T(self.compiler)
        self.assertRaises(ValueError,f.loadFctFile,
                          (StringIO.StringIO(bad_testfile)))

        self.assertEqual(os.path.exists('foo.txt'),False)
        
    def testLoadFileWithBadFormula(self):
        bad_testfile = '''gnofract4d parameter file
version=2.0
[function]
formulafile=test.frm
function=parse_error
[endsection]
[inner]
formulafile=test.cfrm
function=flat
@myfunc=sqrt
[endsection]
[outer]
formulafile=test.cfrm
function=Triangle
@power=3.0
@bailout=1.0e12
[endsection]
[colors]
colorizer=1
solids=[
000000ff
000000ff
]
colorlist=[
0.000000=00000000
1.000000=ffffffff
]
'''
        f = fractal.T(self.compiler)
        self.assertRaises(ValueError,f.loadFctFile,
                          (StringIO.StringIO(bad_testfile)))

    def testSaveFlag(self):
        'Test that we know when we\'re up-to-date on disk'
        f = fractal.T(self.compiler)
        self.assertEqual(f.saved, True)

        f.set_param(0,7.3)
        self.assertEqual(f.saved, False)

        savefile = StringIO.StringIO("")
        f.save(savefile)
        self.assertEqual(f.saved, True)

        c = copy.copy(f)
        self.assertEqual(c.saved, True)

        f.set_param(0,7.3)
        self.assertEqual(f.saved, True)

        f.set_param(0,7.7)
        self.assertEqual(f.saved, False)

        x = f.serialize()
        self.assertEqual(f.saved, False)

        f.loadFctFile(StringIO.StringIO(g_testfile))
        self.assertEqual(f.saved, True)

    def testLoadBadFileRaises(self):
        'Test we throw an exception when loading an invalid file'
        f = fractal.T(self.compiler)
        not_a_file = StringIO.StringIO("ceci n'est pas un file")
        self.assertRaises(Exception,f.loadFctFile,not_a_file)

    def testIntParams(self):
        f = fractal.T(self.compiler)
        f.set_formula("test.frm", "fn_with_intparam")

        p = f.formula.symbols.parameters()
        op = f.formula.symbols.order_of_params()
        
        self.assertEqual(len(p), 2)
        self.assertEqual(p["t__a_x"].type, fracttypes.Int)
        self.assertEqual(op["t__a_x"], 1)
        self.assertEqual(op["__SIZE__"], 2)

        tp = f.formula.symbols.type_of_params()

        self.assertEqual(len(tp),2)
        self.assertEqual(tp[1], fracttypes.Int)
        
        f.set_initparam(1, "17", 0)
        self.assertEqual(f.initparams[1],17)
        self.failUnless(isinstance(f.initparams[1],types.IntType))
            
    def testCFParams(self):
        f = fractal.T(self.compiler)

        self.assertEqual(f.cfunc_params[0],[1.0,0.0,4.0])
        
        f.set_outer("test.cfrm", "Triangle")

        self.assertEqual(f.cfunc_params[0],[ 1.0, 0.0, 1.0e20, 2.0])
        
        cf0p = f.cfuncs[0].symbols.parameters()
        self.assertEqual(cf0p["t__a_bailout"].cname, "t__a_cf0bailout")
        p = f.formula.symbols.parameters()
        self.assertEqual(p["t__a_bailout"].cname, "t__a_fbailout")

        cg = self.compiler.compile(f.formula)
        self.compiler.compile(f.cfuncs[0])
        self.compiler.compile(f.cfuncs[1])

        f.formula.merge(f.cfuncs[0],"cf0_")        
        f.formula.merge(f.cfuncs[1],"cf1_")        

        p2 = f.formula.symbols.parameters()

        # 11 = (2 x bailout), bailfunc, size, gradient +
        #      2x (density, offset, transfer)
        self.assertEqual(len(p2),11) 
        self.assertEqual(p2["t__a_bailout"].cname, "t__a_fbailout")
        self.assertEqual(p2["t__a_cf0bailout"].cname, "t__a_cf0bailout") 

        op2 = f.formula.symbols.order_of_params()
        self.assertEqual(op2, {
            't__a__gradient' : 0,
            't__a_bailout' : 1,
            't__a_cf0_density' : 2,
            't__a_cf0_offset' : 3,
            't__a_cf0bailout' : 4,
            't__a_cf0power' : 5,
            't__a_cf1_density' : 6,
            't__a_cf1_offset' : 7,
            '__SIZE__' : 8
            })
        params = f.all_params()
        self.assertEqual(params,[f.gradient, 4.0,1.0, 0.0, 1.0e20, 2.0, 1.0, 0.0])

        # check for appropriate snippets in the code
        cg.output_decls(f.formula)
        c_code = cg.output_c(f.formula)

        self.assertNotEqual( # init
            c_code.find("double t__a_cf0bailout = t__pfo->p[4]"),-1)
        self.assertNotEqual( # use
            c_code.find("log(t__a_cf0bailout)"),-1)
        
    def assertNearlyEqual(self,a,b):
        # check that each element is within epsilon of expected value
        epsilon = 1.0e-12
        for (ra,rb) in zip(a,b):
            d = abs(ra-rb)
            self.failUnless(d < epsilon,"%f != %f (by %f)" % (ra,rb,d))

    def testLoadRGBColorizer(self):
        'load an rgb colorizer (not supported)'
        file='''gnofract4d parameter file
version=1.6
bailout=4
x=-0.13125000000000000555
y=-0.7562499999999999778
z=0
w=0
size=0.4000000000000000222
xy=0
xz=0
xw=0
yz=0
yw=0
zw=0
maxiter=1600
antialias=1
bailfunc=0
inner=1
outer=1
[function]
function=Mandelbrot
[endsection]
[colors]
colorizer=0
red=0.87
green=0.666
blue=0.3
[endsection]
'''
        f = fractal.T(self.compiler);
        rgb_file = StringIO.StringIO(file)
        
        f.loadFctFile(rgb_file)
        self.assertEqual(f.cfunc_names[0],"rgb")

    def testSaveWithCFParams(self):
        'load and save a file with a colorfunc which has parameters'
        f1 = fractal.T(self.compiler)
        file1 = StringIO.StringIO(g_test2file)
        f1.loadFctFile(file1)

        f1.compile()
        
        self.assertEqual(f1.cfunc_params[0],[1.0, 0.0, 1.0e12, 3.0])
        self.assertEqual(f1.cfunc_params[1],[
            2.0, #_density
            0.5, #_offset
            0, # bool b
            0.09, 0.08, 0.07, 0.06, # color col
            2, # enum ep
            78, # int i 
            3.3, # float val
            2.0, 3.7, 6.1, 8.9 # hyper val2
            ])
        self.assertEqual(f1.get_func_value("@myfunc",f1.cfuncs[1]),"sqrt")
        
        # save again
        file2 = StringIO.StringIO()
        f1.save(file2)
        saved = file2.getvalue()
        self.failUnless(saved.startswith("gnofract4d parameter file"))
        self.assertNotEqual(saved.find("@power=3.0"),-1)
        
        # load it into another instance
        file3 = StringIO.StringIO(saved)
        f3 = fractal.T(self.compiler)
        f3.loadFctFile(file3)

        self.assertFractalsEqual(f1,f3)
        self.assertEqual(f3.get_func_value("@myfunc",f3.cfuncs[1]),"sqrt")

    def assertFuncsEqual(self, f1, form1, f2, form2):
        for name in f1.func_names(form1):
            self.assertEqual(f1.get_func_value(name,form1),
                             f2.get_func_value(name,form2))
        
    def assertFractalsEqual(self,f1,f2):
        # check that they are equivalent
        self.assertEqual(f1.maxiter, f2.maxiter)
        self.assertEqual(f1.params, f2.params)
        
        self.assertEqual(f1.initparams,f2.initparams)
        self.assertEqual(f1.paramtypes, f2.paramtypes)        
        self.assertEqual(f1.funcName,f2.funcName)
        self.assertEqual(f1.funcFile,f2.funcFile)

        self.assertEqual(f1.cfunc_params, f2.cfunc_params)
        self.assertEqual(f1.cfunc_paramtypes, f2.cfunc_paramtypes)
        self.assertEqual(f1.cfunc_names, f2.cfunc_names)
        self.assertEqual(f1.cfunc_files, f2.cfunc_files)
        
        self.assertFuncsEqual(f1, f1.formula,f2, f2.formula)
        self.assertFuncsEqual(f1, f1.cfuncs[0],f2, f2.cfuncs[0])
        self.assertFuncsEqual(f1, f1.cfuncs[1],f2, f2.cfuncs[1])
        self.assertEqual(f1.yflip,f2.yflip)

        self.assertEqual(f1.gradient, f2.gradient)
        
    def testSave(self):
        # load some settings
        f1 = fractal.T(self.compiler)
        file1 = StringIO.StringIO(g_testfile)        
        f1.loadFctFile(file1)

        # save again
        file2 = StringIO.StringIO()
        f1.save(file2)
        saved = file2.getvalue()
        self.failUnless(saved.startswith("gnofract4d parameter file"))
        
        # load it into another instance
        file3 = StringIO.StringIO(saved)
        f2 = fractal.T(self.compiler)
        f2.loadFctFile(file3)
        f2.auto_deepen = False

        self.assertExpectedValues(f2)

        # check that they are equivalent
        self.assertFractalsEqual(f1,f2)

        
    def testRelocation(self):
        f = fractal.T(self.compiler)
        
        f.compile()

        # zoom
        f.relocate(0.0,0.0,2.0)
        tparams = [0.0] * 11
        tparams[f.MAGNITUDE] = 8.0
        self.assertNearlyEqual(f.params,tparams)

        # relocate
        f.relocate(1.0,2.0,1.0)
        tparams[f.XCENTER] = 8.0
        tparams[f.YCENTER] = -16.0
        self.assertNearlyEqual(f.params,tparams)

        # rotated relocation
        f.relocate(-1.0,-2.0,1.0)
        f.params[f.XYANGLE]= -math.pi/2.0
        f.relocate(1.0,2.0,1.0)
        tparams[f.XCENTER] = 16.0
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
        tparams[f.WCENTER] = -16.0
        tparams[f.XZANGLE] = tparams[f.YWANGLE] = math.pi/2.0
        
        self.assertNearlyEqual(f.params,tparams)

        # equivalent Julia relocation using axis param
        f.reset()

        f.relocate(-1.0,-2.0,1.0,2)

        tparams = [0.0] * 11
        tparams[f.MAGNITUDE] = 4.0
        tparams[f.ZCENTER] = -4.0
        tparams[f.WCENTER] = 8.0

        self.assertNearlyEqual(f.params,tparams)

    def testNudges(self):
        f = fractal.T(self.compiler)
        
        f.compile()

        f.nudge(-1,0)
        tparams = [0.0] * 11
        tparams[f.MAGNITUDE] = 4.0
        tparams[f.XCENTER] = -4.0 * 0.025
        
        self.assertNearlyEqual(f.params,tparams)

        f.nudge(0,1)
        tparams[f.YCENTER] = -4.0 * 0.025
        
        self.assertNearlyEqual(f.params,tparams)

        f.nudge(-1,-1,2)
        tparams[f.ZCENTER] = -4.0 * 0.025
        tparams[f.WCENTER] = 4.0 * 0.025
        
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
        self.assertEqual(f.initparams, [f.gradient, 4.0])

        f.compile()
        (w,h) = (40,30)
        image = fract4dc.image_create(w,h)
        f.draw(image)

        buf = fract4dc.image_buffer(image,0,0)

        fract4dc.image_save(image,"def.tga")
        
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
        f.set_named_item("@bailout",7.1, f.formula, f.initparams)

        f.set_inner("test.cfrm", "flat")
        f.set_named_item("@val",0.2, f.cfuncs[1], f.cfunc_params[1])

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
        self.assertEqual(f.initparams,[f.gradient, 8.0,7.0,1.0])
        self.assertEqual(f.periodicity, 0)
        
        self.assertEqual(
            f.cfunc_params[1],
            self.default_flat_params)
        
    def testFutureWarning(self):
        'load a file from the future and check we complain'
        file='''gnofract4d parameter file
version=3.4
'''
        warning_catcher = WarningCatcher()
        f = fractal.T(self.compiler);
        future_file = StringIO.StringIO(file)
        
        f.warn = warning_catcher.warn
        f.loadFctFile(future_file)
        self.assertEqual(len(warning_catcher.warnings),1)
        self.assertEqual(warning_catcher.warnings[0],
            '''This file was created by a newer version of Gnofract 4D.
The image may not display correctly. Please upgrade to version 3.4.''')

    def testNoPeriodIfNoZ(self):
        'if z isn\'t used in the fractal, disable periodicity'
        f = fractal.T(self.compiler)

        f.set_formula("test.frm","test_noz")
        f.compile()
        

    def testCircle(self):
        f = fractal.T(self.compiler)

        f.set_formula("test.frm","test_circle")
        f.set_outer("gf4d.cfrm","continuous_potential")
        f.compile()
        f.reset()
        self.assertEqual(f.initparams,[f.gradient, 4.0])
        (w,h) = (40,30)
        im = fract4dc.image_create(w,h)
        f.draw(im)

        fract4dc.image_save(im,"foo.tga")
        # check that result is horizontally symmetrical
        buf = fract4dc.image_buffer(im,0,0)
        for y in xrange(h):
            line = map(ord,list(buf[y*w*3:(y*w+w)*3]))
            line.reverse()
            revline = line
            line = map(ord,list(buf[y*w*3:(y*w+w)*3]))
            for x in xrange(w):
                a = line[x*3:(x+1)*3]
                b = revline[x*3:(x+1)*3]

                if a != b:
                    fate_buf = fract4dc.image_fate_buffer(im,0,y)
                    print map(ord,list(fate_buf[0:w]))
                    self.assertEqual(a,b,"%s != %s, %d != %d" % (a,b,x,w-x))


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
        f.set_formula("test.frm","test_simpleshape")
        f.set_outer("gf4d.cfrm","default")
        f.compile()
        f.reset()
        self.assertEqual(f.initparams,[f.gradient, 0.0])
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

        
    def testRecolor(self):
        f = fractal.T(self.compiler)
        f.set_formula("test.frm","test_simpleshape")
        f.set_outer("gf4d.cfrm","default")
        f.compile()
        f.reset()
        self.assertEqual(f.initparams,[f.gradient, 0.0])
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
        
    def testDiagonalWithColorFuncs(self):
        f = fractal.T(self.compiler)
        #f.pixel_changed = f._pixel_changed
        f.set_formula("test.frm","test_simpleshape")
        f.set_inner("test.cfrm","flat")
        f.set_outer("test.cfrm","flat")
        f.set_named_item("@val",0.7, f.cfuncs[0], f.cfunc_params[0])
        f.set_named_item("@myfunc","sqrt", f.cfuncs[0], f.cfunc_params[0])

        f.set_named_item("@val",0.2, f.cfuncs[1], f.cfunc_params[1])
        f.set_named_item("@myfunc","sin", f.cfuncs[1], f.cfunc_params[1])

        outgrey = int(math.sqrt(0.7) * 255)
        ingrey = int(math.sin(0.2) * 255)

        self.check_diagonal_image(f, ingrey, outgrey)

        # check all this stuff survives serialization
        saved = f.serialize()

        f2 = fractal.T(self.compiler)
        f2.loadFctFile(StringIO.StringIO(saved))
        self.check_diagonal_image(f2, ingrey, outgrey)
        
    def check_diagonal_image(self,f,ingrey,outgrey):
        f.gradient.load_list([(0.0,0,0,0,255),(1.0,255,255,255,255)])
        f.compile()
        (w,h) = (30,30)
        im = fract4dc.image_create(w,h)
        f.antialias = False
        f.draw(im)

        buf = fract4dc.image_buffer(im,0,0)
        
        for y in xrange(h):
            for x in xrange(w):
                if x >= y:
                    self.assertColor(buf,x,y,w,outgrey)
                else:
                    self.assertColor(buf,x,y,w,ingrey)
        
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
[colorizer]=1
colorizer=0
red=0.377255787461439
green=1
blue=0.5543108971162746
[endsection]
'''
        f = fractal.T(self.compiler)
        wc = WarningCatcher()
        f.warn = wc.warn
        f.loadFctFile(StringIO.StringIO(file))

        self.assertEqual(f.initparams,[f.gradient, 0.34,-0.28,4.0])
                         
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

        self.assertEqual(f.cfunc_files, ["gf4d.cfrm"] * 2)
        self.assertEqual(f.cfunc_names, ["default", "zero"])
        
        f.compile()
        image = fract4dc.image_create(4,3)
        f.draw(image)

    def testFct(self):
        file = open("../testdata/test.fct")
        f = fractal.T(self.compiler);
        f.loadFctFile(file)
        f.compile()
        image = fract4dc.image_create(64,48)
        f.draw(image)
        #fract4dc.image_save(image,"mandel3.tga")

    def testCopy(self):
        f = fractal.T(self.compiler)
        f.set_formula("gf4d.frm","Barnsley Type 1")
        f.set_named_item("@bailfunc","manhattanish",f.formula,f.initparams)
        f.set_outer("test.cfrm","flat")
        f.set_named_item("@ep", 2, f.cfuncs[0], f.cfunc_params[0])
        f.set_named_item("@i", 789, f.cfuncs[0], f.cfunc_params[0])
        f.set_named_item("@_transfer","sqrt",f.cfuncs[0],f.cfunc_params[0])
        c = copy.copy(f)

        self.assertFractalsEqual(f,c)

        # some tests to ensure data is actually separate
        
        # test a parameter        
        mag = c.get_param(c.MAGNITUDE)
        self.assertEqual(mag,f.get_param(f.MAGNITUDE))

        f.set_param(f.MAGNITUDE,89.1)
        self.assertEqual(mag,c.get_param(c.MAGNITUDE))
        self.assertNotEqual(mag,f.get_param(f.MAGNITUDE))
        
        # test formula
        formName = c.funcName
        self.assertEqual(formName,f.funcName)

        f.set_formula("gf4d.frm","Mandelbar")
        self.assertEqual(formName,c.funcName)
        self.assertNotEqual(formName,f.funcName)

        # test colors
        colors = c.gradient.segments
        c0 = colors[0].left_color
        for i in xrange(len(colors)):
            self.assertEqual(colors[i].left_color,
                             f.gradient.segments[i].left_color)

        f.gradient.segments[0].left_color = [0.7,0.3,0.6,0.5]
        self.assertEqual(c0,c.gradient.segments[0].left_color)
        self.assertNotEqual(c0,f.gradient.segments[0].left_color)

    def testCopy2(self):
        '''There was a bug where copy() would reset func values.
        Check for recurrence'''
        f = fractal.T(self.compiler)
        f.loadFctFile(open("../testdata/julfn.fct"))
        f.set_named_item("@fn1","sinh",f.formula,f.initparams)

        self.assertEqual(f.get_func_value("@fn1",f.formula),"sinh")
        
        c = copy.copy(f)

        self.assertEqual(f.get_func_value("@fn1",f.formula),"sinh")
        
    def assertDirty(self,f):
        self.assertEqual(f.dirty,True)

    def assertClean(self,f):
        self.assertEqual(f.dirty,False)
        
    def testDirtyFlag(self):
        f = fractal.T(self.compiler)
        self.assertDirty(f)
        f.clean()
        self.assertClean(f)

        # set to existing value
        f.set_param(f.MAGNITUDE,f.params[f.MAGNITUDE])
        self.assertClean(f)

        # set to different value
        f.set_param(f.MAGNITUDE,f.params[f.MAGNITUDE] * 2.0)
        self.assertDirty(f)

        f.clean()
        f.set_named_func("@bailfunc","real2",f.formula)
        self.assertDirty(f)

    def testLoadGivesCorrectParameters(self):
        f = fractal.T(self.compiler)
        self.assertEqual(len(f.formula.symbols.parameters()),3)
        f.loadFctFile(open("../testdata/elfglow.fct"))
        self.assertEqual(len(f.formula.symbols.parameters()),5)
        
        
    def testFractalBadness(self):
        f = fractal.T(self.compiler)
        self.assertRaises(ValueError,f.set_formula,"gf4d.frm","xMandelbrot")
        self.assertRaises(ValueError,f.set_inner,"gf4d.cfrm","xdefault")
        self.assertRaises(ValueError,f.set_outer,"gf4d.cfrm","xzero")

        # none of these should have changed the fractal, which should still work
        self.assertEqual(f.funcName,"Mandelbrot")
        f.compile()

def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
