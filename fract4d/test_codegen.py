#!/usr/bin/env python

import unittest
import tempfile
import os
import commands
import math
import cmath
import sys

import testbase

import absyn
import ir
import symbol
from fracttypes import *
import codegen
import translate
import fractparser
import fractlexer
import stdlib

g_exp = None
g_x = None

class CodegenTest(testbase.TestBase):
    def setUp(self):
        self.fakeNode = absyn.Empty(0)
        self.codegen = codegen.T(symbol.T())
        self.parser = fractparser.parser
        self.main_stub = '''
int main()
{
    double pparams[] = { 1.5, 0.0, 0.0, 0.0};
    double initparams[] = {5.0, 2.0};
    int nItersDone=0;
    int nFate=0;
    double dist=0.0;
    pf_obj *pf = pf_new();
    pf->vtbl->init(pf,0.001,initparams,2);
    
    pf->vtbl->calc(
         pf,
         pparams,
         100, 100,
         0,0,0,
         &nItersDone, &nFate, &dist);
    
    printf("(%d,%d,%g)\\n",nItersDone,nFate,dist);

    pparams[0] = 0.1; pparams[1] = 0.2;
    pparams[2] = 0.1; pparams[3] = 0.3;
    initparams[0] = 3.0; initparams[1] = 3.5;
    
    pf->vtbl->calc(
        pf,
        pparams,
        20, 20,
        0,0,0,
        &nItersDone, &nFate, &dist);

    printf("(%d,%d,%g)\\n",nItersDone,nFate,dist);

    pf->vtbl->kill(pf);
    return 0;
}
'''
    
    def tearDown(self):
        pass

    # convenience methods to make quick trees for testing
    def eseq(self,stms, exp):
        return ir.ESeq(stms, exp, self.fakeNode, Int)
    def seq(self,stms):
        return ir.Seq(stms,self.fakeNode)
    def var(self,name="a",type=Int):
        return ir.Var(name,self.fakeNode, type)
    def const(self,value=None,type=Int):
        if value == None:
            value = default_value(type)
        return ir.Const(value, self.fakeNode, type)
    def binop(self,stms,op="+",type=Int):
        return ir.Binop(op,stms,self.fakeNode, type)
    def move(self,dest,exp):
        return ir.Move(dest, exp, self.fakeNode, Int)
    def cjump(self,e1,e2,trueDest="trueDest",falseDest="falseDest"):
        return ir.CJump(">", e1, e2, trueDest, falseDest, self.fakeNode)
    def jump(self,dest):
        return ir.Jump(dest,self.fakeNode)
    def cast(self, e, type):
        return ir.Cast(e,self.fakeNode, type)
    def label(self,name):
        return ir.Label(name,self.fakeNode)

    def generate_code(self,t):
        self.codegen = codegen.T(symbol.T())
        self.codegen.generate_code(t)

    def translate(self,s,dump=None):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        #print pt.pretty()
        t = translate.T(pt.children[0],dump)
        #print t.pretty()
        self.assertNoErrors(t)
        self.codegen = codegen.T(t.symbols,dump)
        return t

    def translatecf(self,s,name,dump=None):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        #print pt.pretty()
        t = translate.ColorFunc(pt.children[0],name,dump)
        #print t.pretty()
        self.assertNoErrors(t)
        return t
        
    def sourceToAsm(self,s,section,dump=None):
        t = self.translate(s,dump)
        self.codegen.generate_all_code(t.canon_sections[section])
        if dump != None and dump.get("dumpAsm") == 1:
            self.printAsm()
        return self.codegen.out

    def printAsm(self):
        for i in self.codegen.out:
            try:
                #print i
                print i.format()
            except Exception, e:
                print "Can't format %s:%s" % (i,e)

    def makeC(self,user_preamble="", user_postamble=""):
        # construct a C stub for testing
        preamble = '''
        #include <stdio.h>
        #include <math.h>
        typedef struct {
            double *p;
        } pf_fake;

        int main(){
        double params[20]= {0.0, 0.0, 0.0, 0.0};
        pf_fake t__f;
        t__f.p = params;
        pf_fake *t__pfo = &t__f;
        double pixel_re = 0.0, pixel_im = 0.0;
        double t__h_zwpixel_re = 0.0, t__h_zwpixel_im = 0.0;
        '''
        decls = string.join(map(lambda x: x.format(),
                                self.codegen.output_symbols({})),"\n")
        str_output = string.join(map(lambda x : x.format(), self.codegen.out),"\n")
        postamble = "\nreturn 0;}\n"

        return string.join([preamble,decls,"\n",
                            user_preamble,str_output,"\n",
                            user_postamble,postamble],"")

    def compileAndRun(self,c_code):
        cFileName = self.codegen.writeToTempFile(c_code,".c")
        oFileName = self.codegen.writeToTempFile("")
        #print c_code
        cmd = "gcc -Wall %s -o %s -lm" % (cFileName, oFileName)
        #print cmd
        (status,output) = commands.getstatusoutput(cmd)
        self.assertEqual(status,0,"C error:\n%s\nProgram:\n%s\n" % \
                         ( output,c_code))
        #print "status: %s\noutput:\n%s" % (status, output)
        cmd = oFileName
        (status,output) = commands.getstatusoutput(cmd)
        self.assertEqual(status,0, "Runtime error:\n" + output)
        #print "status: %s\noutput:\n%s" % (status, output)
        return output

    # test methods
    def testMatching(self):
        template = "[Binop, Const, Const]"

        tree = self.binop([self.const(),self.const()])
        self.assertMatchResult(tree,template,1)

        tree = self.const()
        self.assertMatchResult(tree,template,0)
        
        tree = self.binop([self.const(), self.var()])
        self.assertMatchResult(tree, template,0)

        template = "[Binop, Exp, Exp]"
        self.assertMatchResult(tree, template,1)
        
    def testWhichMatch(self):
        tree = self.binop([self.const(),self.const()])
        self.assertEqual(self.codegen.match(tree).__name__,"binop")

    def testGen(self):
        tree = self.const()
        x = self.codegen.generate_code(tree)
        self.assertEqual(isinstance(x,codegen.ConstIntArg),1)
        self.assertEqual(x.value,0)
        self.assertEqual(x.format(),"0")

        tree = self.var()
        x = self.codegen.generate_code(tree)
        self.assertEqual(isinstance(x,codegen.TempArg),1)
        self.assertEqual(x.value,"a")
        self.assertEqual(x.format(),"a")

        tree = self.var("b",Complex)
        x = self.codegen.generate_code(tree)
        self.assertEqual(isinstance(x,codegen.ComplexArg),1)
        self.assertEqual(x.re.value,"b_re")
        self.assertEqual(x.im.format(),"b_im")
        
        tree = self.binop([self.const(),self.var()])
        x = self.codegen.generate_code(tree)
        self.assertEqual(isinstance(x,codegen.TempArg),1,x)
        self.assertEqual(x.value,"t__temp0")
        self.assertEqual(x.format(),"t__temp0")

        self.assertEqual(len(self.codegen.out),1)
        op = self.codegen.out[0]
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))
        self.assertEqual(op.format(),"t__temp0 = 0 + a;",op.format())

    def testComplexAdd(self):
        # (1,3) + a
        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)],"+",Complex)
        x = self.codegen.generate_code(tree)
        self.assertEqual(isinstance(x,codegen.ComplexArg),1,x)

        self.assertEqual(len(self.codegen.out),2)

        expAdd = "t__temp0 = 1.00000000000000000 + a_re;\n" + \
                 "t__temp1 = 3.00000000000000000 + a_im;"
        self.assertOutputMatch(expAdd)

        # a + (1,3) 
        tree = self.binop([self.var("a",Complex),self.const([1,3],Complex)],"+",Complex)
        self.generate_code(tree)
        self.assertEqual(len(self.codegen.out),2)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))

        expAdd = "t__temp0 = a_re + 1.00000000000000000;\n" + \
                 "t__temp1 = a_im + 3.00000000000000000;"

        self.assertOutputMatch(expAdd)

        # a + b + c
        tree = self.binop([
            self.binop([
                self.var("a",Complex),
                self.var("b",Complex)],"+",Complex),
            self.var("c", Complex)],"+",Complex)
        self.generate_code(tree)
        self.assertEqual(len(self.codegen.out),4)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))

        expAdd = "t__temp0 = a_re + b_re;\n" + \
                 "t__temp1 = a_im + b_im;\n" + \
                 "t__temp2 = t__temp0 + c_re;\n" +\
                 "t__temp3 = t__temp1 + c_im;"

        self.assertOutputMatch(expAdd)

    def testComplexMul(self):
        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)],"*",Complex)
        self.generate_code(tree)
        self.assertEqual(len(self.codegen.out),6)
        exp = '''t__temp0 = 1.00000000000000000 * a_re;
t__temp1 = 3.00000000000000000 * a_im;
t__temp2 = 3.00000000000000000 * a_re;
t__temp3 = 1.00000000000000000 * a_im;
t__temp4 = t__temp0 - t__temp1;
t__temp5 = t__temp2 + t__temp3;'''
        
        self.assertOutputMatch(exp)

        # a * b * c
        tree = self.binop([
            self.binop([
                self.var("a",Complex),
                self.var("b",Complex)],"*",Complex),
            self.var("c", Complex)],"*",Complex)
        self.generate_code(tree)

        expAdd = '''t__temp0 = a_re * b_re;
t__temp1 = a_im * b_im;
t__temp2 = a_im * b_re;
t__temp3 = a_re * b_im;
t__temp4 = t__temp0 - t__temp1;
t__temp5 = t__temp2 + t__temp3;
t__temp6 = t__temp4 * c_re;
t__temp7 = t__temp5 * c_im;
t__temp8 = t__temp5 * c_re;
t__temp9 = t__temp4 * c_im;
t__temp10 = t__temp6 - t__temp7;
t__temp11 = t__temp8 + t__temp9;'''
        self.assertOutputMatch(expAdd)
        
    def testCompare(self):
        tree = self.binop([self.const(3,Int),self.var("a",Int)],">",Bool)
        self.generate_code(tree)
        self.assertOutputMatch("t__temp0 = 3 > a;")

        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)],">",Complex)
        self.generate_code(tree)
        self.assertOutputMatch("t__temp0 = 1.00000000000000000 > a_re;")

        tree.op = "=="
        self.generate_code(tree)
        self.assertOutputMatch('''t__temp0 = 1.00000000000000000 == a_re;
t__temp1 = 3.00000000000000000 == a_im;
t__temp2 = t__temp0 && t__temp1;''')

        tree.op = "!="
        self.generate_code(tree)
        self.assertOutputMatch('''t__temp0 = 1.00000000000000000 != a_re;
t__temp1 = 3.00000000000000000 != a_im;
t__temp2 = t__temp0 || t__temp1;''')

    def testS2A(self):
        asm = self.sourceToAsm('''t_s2a {
init:
int a = 1
loop:
z = z + a
}''', "loop")
        self.assertOutputMatch('''t__start_loop:
t__temp0 = ((double)a);
t__temp1 = 0.0;
t__temp2 = z_re + t__temp0;
t__temp3 = z_im + t__temp1;
z_re = t__temp2;
z_im = t__temp3;
goto t__end_loop;''')

        asm = self.sourceToAsm('t_s2a_2{\ninit: a = -1.5\n}',"init")
        self.assertOutputMatch('''t__start_init:
t__temp0 = -(1.50000000000000000);
t__temp1 = t__temp0;
t__temp2 = 0.0;
a_re = t__temp1;
a_im = t__temp2;
goto t__end_init;''')
    
    def testSymbols(self):
        self.codegen.symbols["q"] = Var(Complex)
        z = self.codegen.symbols["q"] # ping z to get it in output list
        out = self.codegen.output_symbols({})
        l = [x for x in out if x.assem == "double q_re = 0.00000000000000000;"]
        self.failUnless(len(l)==1,l)

        z = self.codegen.symbols["z"] # ping z to get it in output list
        out = self.codegen.output_symbols({ "z" : "foo"})
        l = [x for x in out if x.assem == "foo"]
        self.failUnless(len(l)==1)

    def testCF(self):
        tcf0 = self.translatecf('''
        biomorph {
        init:
        float d = |z|
        loop:
        d = d + |z|
        final:
        #index = log(d+1.0)
        }''',"cf0")
        cg_cf0 = codegen.T(tcf0.symbols)
        cg_cf0.output_all(tcf0)

        tcf1 = self.translatecf('zero {\n float d = 1.0\n#index = 0.0\n}', "cf1")
        cg_cf1 = codegen.T(tcf1.symbols)
        cg_cf1.output_all(tcf1)

        t = self.translate('''
        mandel {
        loop:
        z = z*z + c
        bailout:
        |z| < 4.0
        }''')

        cg = codegen.T(t.symbols)
        cg.output_all(t)
        
        t.merge(tcf0,"cf0_")
        t.merge(tcf1,"cf1_")

        cg.output_decls(t)
        
        c_code = self.codegen.output_c(t)
        
        cFileName = self.codegen.writeToTempFile(c_code,".c")
        oFileName = self.codegen.writeToTempFile(None,".so")
        #print c_code
        cmd = "gcc -Wall -fPIC -DPIC -shared %s -o %s -lm" % (cFileName, oFileName)
        (status,output) = commands.getstatusoutput(cmd)
        self.assertEqual(status,0,"C error:\n%s\nProgram:\n%s\n" % \
                         ( output,c_code))

    def testC(self):
        # basic end-to-end testing. Compile a code fragment + instrumentation,
        # run it and check output
        src = 't_c1 {\nloop: int a = 1\nz = z + a\n}'
        self.assertCSays(src,"loop","printf(\"%g,%g\\n\",z_re,z_im);","1,0")
        
        src = '''t_c2{\ninit:int a = 1 + 3 * 7 + 4 % 2\n}'''
        self.assertCSays(src,"init","printf(\"%d\\n\",a);","22")

        src = 't_c3{\ninit: b = 1 + 3 * 7 - 2\n}'
        self.assertCSays(src,"init","printf(\"%g\\n\",b_re);","20")

        src = 't_c4{\ninit: bool x = |z| < 4.0\n}'
        self.assertCSays(src,"init","printf(\"%d\\n\",x);","1")

        src = 't_c5{\ninit: complex x = (1,3), complex y = (2.5,1.5)\n' + \
              'z = x - y\n}'
        self.assertCSays(src,"init","printf(\"(%g,%g)\\n\", z_re, z_im);",
                         "(-1.5,1.5)")

        src = 't_c5{\ninit: complex x = #Pixel\nz = z - x\n}'
        self.assertCSays(src,"init","printf(\"(%g,%g)\\n\", z_re, z_im);",
                         "(0,0)")

        src = 't_c6{\ninit: complex x = y = (2,1), real(y)=3\n}'
        self.assertCSays(src,"init",
                         self.inspect_complex("x") +
                         self.inspect_complex("y"),
                         "x = (2,1)\ny = (3,1)")

        src = 't_c7{\ninit: complex x = (2,1), y = -x\n}'
        self.assertCSays(src,"init",
                         self.inspect_complex("x") +
                         self.inspect_complex("y"),
                         "x = (2,1)\ny = (-2,-1)")

        src = '''t_c_if{
        init:
        int x = 1
        int y = 0
        if x == 1
            y = 2
        else
            y = 3
        endif
        }'''
        self.assertCSays(src,"init","printf(\"%d\\n\",y);","2")

        # casts to & from bool
        src = '''t_c7{
        init:
        bool t = 1
        bool f = 0
        bool temp
        int i7 = 7
        int i0 = 0
        float f0 = 0.0
        float f7 = 7.0
        complex c0 = (0.0,0.0)
        complex c1 = (1.0,0.0)
        complex ci1 = (0.0,1.0)
        complex c7 = (7,7)

        ; now check for casts by round-tripping
        temp = c7
        complex c_from_bt = temp
        temp = c0
        complex c_from_bf = temp
        temp = ci1
        complex c_from_bt2 = temp
        temp = i7
        int i_from_bt = temp
        temp = i0
        int i_from_bf = temp
        temp = f7
        float f_from_bt = temp
        temp = f0
        float f_from_bf = temp
        
        }'''

        tests = string.join([
            self.inspect_bool("t"),
            self.inspect_bool("f"),
            self.inspect_complex("c_from_bt"),
            self.inspect_complex("c_from_bt2"),
            self.inspect_complex("c_from_bf"),
            self.inspect_int("i_from_bt"),
            self.inspect_int("i_from_bf"),
            self.inspect_float("f_from_bt"),
            self.inspect_float("f_from_bf"),
            ])
        
        results = string.join([
            "t = 1",
            "f = 0",
            "c_from_bt = (1,0)",
            "c_from_bt2 = (1,0)",
            "c_from_bf = (0,0)",
            "i_from_bt = 1",
            "i_from_bf = 0",
            "f_from_bt = 1",
            "f_from_bf = 0",
            ],"\n")
        self.assertCSays(src,"init",tests,results)

    def testParams(self):
        src = 't_cp0{\ninit: complex @p = (2,1)\n}'
        self.assertCSays(src,"init",self.inspect_complex("t__a_p"),
                         "t__a_p = (2,1)")

        src = '''t_params {
        init: complex x = @p1 + p2 + @my_param
        complex y = @fn1((1,-1)) + fn2((2,0)) + @my_func((2,0))
        }'''

        # first without overrides
        t = self.translate(src)
        self.codegen.generate_all_code(t.canon_sections["init"])

        check = self.inspect_complex("x") + self.inspect_complex("y")
        postamble = "t__end_%s:\n%s\n" % ("init",check)
        c_code = self.makeC("", postamble)        
        output = self.compileAndRun(c_code)
        self.assertEqual(output,"x = (0,0)\ny = (5,-1)")

        # then again with overridden funcs
        t = self.translate(src)
        t.symbols["@my_func"][0].set_func(stdlib,"sqr")
        t.symbols["@fn1"][0].set_func(stdlib,"conj")
        t.symbols["@fn2"][0].set_func(stdlib,"ident")
        self.codegen.generate_all_code(t.canon_sections["init"])

        check = self.inspect_complex("x") + self.inspect_complex("y")
        postamble = "t__end_%s:\n%s\n" % ("init",check)
        c_code = self.makeC("", postamble)        
        output = self.compileAndRun(c_code)
        self.assertEqual(output,"x = (0,0)\ny = (7,1)")

    def testFormulas(self):
        # these caused an error at one point in development
        # so have been added ro regression suite
        t = self.translate('''andy03 {
        z = c = pixel/4:
        z = p1*z + c
        z = p2*z^3 + c
        z = c + c/2 + z
        ;SOURCE: andy_1.frm
        }''')

        self.assertNoErrors(t)

        # compiler error
        
        t = self.translate('''
TileMandel {; Terren Suydam (terren@io.com), 1996
            ; modified by Sylvie Gallet [101324,3444]
            ; Modified for if..else logic 3/19/97 by Sylvie Gallet
            ; p1 = center = coordinates for a good Mandel
   ; 0 <= real(p2) = magnification. Default for magnification is 1/3
   ; 0 <= imag(p2) = numtiles. Default for numtiles is 3
  center = p1
  IF (p2 > 0)
     mag = real(p2)
  ELSE
     mag = 1/3
  ENDIF
  IF (imag(p2) > 0)
     numtiles = imag(p2)
  ELSE
     numtiles = 3
  ENDIF
  omega = numtiles*2*pi/3
  x = asin(sin(omega*real(pixel))), y = asin(sin(omega*imag(pixel)))
  z = c = (x+flip(y)) / mag + center:
  z = z*z + c
  |z| <= 4
  ;SOURCE: fract196.frm
}
''')
        self.assertNoErrors(t)
        

    def testUseBeforeAssign(self):
        src = 't_uba0{\ninit: z = z - x\n}'
        self.assertCSays(src,"init",self.inspect_complex("z"),
                         "z = (0,0)")

    def inspect_bool(self,name):
        return "printf(\"%s = %%d\\n\", %s);" % (name,name)

    def inspect_float(self,name):
        return "printf(\"%s = %%g\\n\", %s);" % (name,name)

    def inspect_int(self,name):
        return "printf(\"%s = %%d\\n\", %s);" % (name,name)

    def inspect_complex(self,name):
        return "printf(\"%s = (%%g,%%g)\\n\", %s_re, %s_im);" % (name,name,name)

    def predict(self,f,arg1=0,arg2=1):
        # compare our compiler results to Python stdlib
        try:
            x = "%.6g" % f(arg1)
        except ZeroDivisionError:
            x = "inf"
        try:
            y = "%.6g" % f(arg2)
        except ZeroDivisionError:
            y = "inf"
        
        return "(%s,%s)" % (x,y)

    def cpredict(self,f,arg=(1+0j)):
        try:
            z = f(arg)
            return "(%.6g,%.6g)" % (z.real,z.imag) 
        except OverflowError:
            return "(inf,inf)"
        except ZeroDivisionError:
            return "(nan,nan)"
    
    def make_test(self,myfunc,pyfunc,val,n):
        codefrag = "ct_%s%d = %s((%d,%d))" % (myfunc, n, myfunc, val.real, val.imag)
        lookat = "ct_%s%d" % (myfunc, n)
        result = self.cpredict(pyfunc,val)
        return [ codefrag, lookat, result]
        
    def manufacture_tests(self,myfunc,pyfunc):
        vals = [ 0+0j, 0+1j, 1+0j, 1+1j, 3+2j, 1-0j, 0-1j, -3+2j, -2-2j, -1+0j ]
        return map(lambda (x,y) : self.make_test(myfunc,pyfunc,x,y), \
                   zip(vals,range(1,len(vals))))

    def cotantests(self):
        def mycotan(z):
            return cmath.cos(z)/cmath.sin(z)

        tests = self.manufacture_tests("cotan",mycotan)
        
        # CONSIDER: comes out as -0,1.31304 in python, but +0 in C++ and gf4d
        # think Python's probably in error, but not 100% sure
        tests[6][2] = "(0,1.31304)"
        
        return tests

    def logtests(self):
        tests = self.manufacture_tests("log",cmath.log)
                    
        tests[0][2] = "(-inf,0)" # log(0+0j) is overflow in python
        return tests

    def asintests(self):
        tests = self.manufacture_tests("asin",cmath.asin)
        # asin(x+0j) = (?,-0) in python, which is wrong
        tests[0][2] = "(0,0)" 
        tests[2][2] = tests[5][2] = "(1.5708,0)"

        return tests

    def acostests(self):
        # work around buggy python acos 
        tests = self.manufacture_tests("acos",cmath.acos)
        tests[0][2] = "(1.5708,0)"
        tests[2][2] = tests[5][2] = "(0,0)"
        return tests

    def atantests(self):
        tests = self.manufacture_tests("atan",cmath.atan)
        tests[1][2] = "(nan,nan)"
        tests[6][2] = "(nan,-inf)" # not really sure who's right on this
        return tests

    def atanhtests(self):
        tests = self.manufacture_tests("atanh",cmath.atanh)
        tests[2][2] = tests[5][2] = "(inf,0)" # Python overflows the whole number
        return tests

    def test_stdlib(self):

        # additions to python math stdlib
        def myfcotan(x):
            return math.cos(x)/math.sin(x)
        
        def myfcotanh(x):
            return math.cosh(x)/math.sinh(x)

        def mycotanh(z):
            return cmath.cosh(z)/cmath.sinh(z)

        def myasinh(z):
            return cmath.log(z + cmath.sqrt(z*z+1))

        def myacosh(z):
            return cmath.log(z + cmath.sqrt(z-1) * cmath.sqrt(z+1))

        def myctrunc(z):
            return complex(int(z.real),int(z.imag))

        def mycfloor(z):
            return complex(math.floor(z.real),math.floor(z.imag))

        def mycround(z):
            return complex(int(z.real+0.5),int(z.imag+0.5))

        def mycceil(z):
            return complex(math.ceil(z.real),math.ceil(z.imag))

        def myczero(z):
            return complex(0,0)
        
        tests = [
            # code to run, var to inspect, result
            [ "fm = (3.0 % 2.0, 3.1 % 1.5)","fm","(1,0.1)"], 
            [ "cj = conj(y)", "cj", "(1,-2)"],
            [ "fl = flip(y)", "fl", "(2,1)"],
            [ "ri = (imag(y),real(y))","ri", "(2,1)"],
            [ "m = |y|","m","(5,0)"],
            [ "t = (4,2) * (2,-1)", "t", "(10,0)"],
            [ "d1 = y/(1,0)","d1","(1,2)"],
            [ "d2 = y/y","d2","(1,0)"],
            [ "d3 = (4,2)/y","d3","(1.6,-1.2)"],
            [ "d4 = (2,1)/2","d4","(1,0.5)"],
            [ "recip1 = recip((4,0))/recip(4)", "recip1", "(1,0)"],
            [ "i = ident(y)","i","(1,2)"],
            [ "a = (abs(4),abs(-4))","a","(4,4)"],
            [ "a2 = abs((4,-4))","a2","(4,4)"],
            [ "cab = (cabs((0,0)), cabs((3,4)))", "cab", "(0,5)"],
            [ "sq = (sqrt(4),sqrt(2))", "sq", self.predict(math.sqrt,4,2)],
            [ "l = (log(1),log(3))", "l", self.predict(math.log,1,3)],
            [ "ex = (exp(1),exp(2))","ex", self.predict(math.exp,1,2)],
            [ "p = (2^2,9^0.5)","p", "(4,3)"],
            [ "pow1 = (1,0)^2","pow1", "(1,0)"],
            [ "pow2 = (-2,-3)^7.5","pow2","(-13320.5,6986.17)"],
            [ "pow3 = (-2,-3)^(1.5,-3.1)","pow3","(0.00507248,-0.00681128)"],
            [ "pow4 = (0,0)^(1.5,-3.1)","pow4","(0,0)"],
            [ "manh1 = (manhattanish(2.0,-1.0),manhattanish(0.1,-0.1))",
              "manh1", "(1,0)"],
            [ "manh2 = (manhattan(2.0,-1.5),manhattan(-2,1.7))",
              "manh2", "(3.5,3.7)"],
            [ "manh3 = (manhattanish2(2.0,-1.0),manhattanish2(0.1,-0.1))",
              "manh3", "(25,0.0004)"],
            [ "mx2 = (max2(2,-3),max2(-3,0))", "mx2", "(9,9)"],
            [ "mn2 = (min2(-1,-2),min2(7,4))", "mn2", "(1,16)"],
            [ "r2 = (real2(3,1),real2(-2.5,2))","r2","(9,6.25)"],
            [ "i2 = (imag2(3,2),imag2(2,-0))", "i2", "(4,0)"],
            [ "ftrunc1 = (trunc(0.5), trunc(0.4))", "ftrunc1", "(0,0)"],
            [ "ftrunc2 = (trunc(-0.5), trunc(-0.4))", "ftrunc2", "(0,0)"],
            [ "frnd1 = (round(0.5), round(0.4))", "frnd1", "(1,0)"],
            [ "frnd2 = (round(-0.5), round(-0.4))", "frnd2", "(0,0)"],
            [ "fceil1 = (ceil(0.5), ceil(0.4))", "fceil1", "(1,1)"],
            [ "fceil2 = (ceil(-0.5), ceil(-0.4))", "fceil2", "(-0,-0)"],
            [ "ffloor1 = (floor(0.5), floor(0.4))", "ffloor1", "(0,0)"],
            [ "ffloor2 = (floor(-0.5), floor(-0.4))", "ffloor2", "(-1,-1)"],
            [ "fzero = (zero(77),zero(-41.2))", "fzero", "(0,0)"],
            
            # trig functions
            [ "t_sin = (sin(0),sin(1))","t_sin", self.predict(math.sin)],
            [ "t_cos = (cos(0),cos(1))","t_cos", self.predict(math.cos)],
            [ "t_tan = (tan(0),tan(1))","t_tan", self.predict(math.tan)],
            [ "t_cotan = (cotan(0),cotan(1))","t_cotan", self.predict(myfcotan)],
            [ "t_sinh = (sinh(0),sinh(1))","t_sinh", self.predict(math.sinh)],
            [ "t_cosh = (cosh(0),cosh(1))","t_cosh", self.predict(math.cosh)],
            [ "t_tanh = (tanh(0),tanh(1))","t_tanh", self.predict(math.tanh)],
            [ "t_cotanh = (cotanh(0),cotanh(1))","t_cotanh",
              self.predict(myfcotanh)],
              
            # inverse trig functions
            [ "t_asin = (asin(0),asin(1))","t_asin", self.predict(math.asin)],
            [ "t_acos = (acos(0),acos(1))","t_acos", self.predict(math.acos)],
            [ "t_atan = (atan(0),atan(1))","t_atan", self.predict(math.atan)],
            [ "t_atan2 = (atan2((1,1)),atan2((-1,-1)))",
              "t_atan2", "(0.785398,-2.35619)"],
            # these aren't in python stdlib, need to hard-code results
            [ "t_asinh = (asinh(0),asinh(1))","t_asinh", "(0,0.881374)" ],
            [ "t_acosh = (acosh(10),acosh(1))","t_acosh", "(2.99322,0)" ],
            [ "t_atanh = (atanh(0),atanh(0.5))","t_atanh", "(0,0.549306)" ],
        ]
        tests += self.manufacture_tests("sin",cmath.sin)
        tests += self.manufacture_tests("cos",cmath.cos)
        tests += self.manufacture_tests("tan",cmath.tan)
        tests += self.manufacture_tests("sinh",cmath.sinh)
        tests += self.manufacture_tests("cosh",cmath.cosh)
        tests += self.manufacture_tests("tanh",cmath.tanh)
        tests += self.manufacture_tests("exp",cmath.exp)
        tests += self.manufacture_tests("sqrt",cmath.sqrt)
        tests += self.manufacture_tests("round",mycround)
        tests += self.manufacture_tests("ceil",mycceil)
        tests += self.manufacture_tests("floor",mycfloor)
        tests += self.manufacture_tests("trunc",myctrunc)
        tests += self.manufacture_tests("zero",myczero)
        tests += self.cotantests()
        tests += self.manufacture_tests("cotanh",mycotanh)
        tests += self.logtests()
        
        tests += self.asintests()
        tests += self.acostests()
        tests += self.atantests()
        tests += self.manufacture_tests("asinh",myasinh)
        tests += self.manufacture_tests("acosh",myacosh)
        tests += self.atanhtests()

        # construct a formula calculating all of the above,
        # run it and compare results with expected values
        src = 't_c6{\ninit: y = (1,2)\n' + \
              string.join(map(lambda x : x[0], tests),"\n") + "\n}"

        check = string.join(map(lambda x :self.inspect_complex(x[1]),tests),"\n")
        exp = map(lambda x : "%s = %s" % (x[1],x[2]), tests)
        self.assertCSays(src,"init",check,exp)

    def testExpression(self):
        # this is for quick manual experiments - skip if input var not set
        global g_exp,g_x
        if g_exp == None:
            return
        x = g_x or "(1,0)"        
        src = 't_test {\ninit:\nx = %s\nresult = %s\n}' % (x,g_exp)
        asm = self.sourceToAsm(src,"init",{})
        postamble = "t__end_init:\nprintf(\"(%g,%g)\\n\",result_re,result_im);"
        c_code = self.makeC("", postamble)
        output = self.compileAndRun(c_code)
        print output

    def testMandel(self):
        src = '''t_mandel{
init:
z = #zwpixel
loop:
z = z*z + pixel
bailout:
|z| < 4.0
}'''
        t = self.translate(src)
        self.codegen.output_all(t)
        self.codegen.output_decls(t)
        
        inserts = {
            "loop_inserts":"printf(\"(%g,%g)\\n\",z_re,z_im);",
            "main_inserts": self.main_stub
            }
        c_code = self.codegen.output_c(t,inserts)
        #print c_code
        output = self.compileAndRun(c_code)
        lines = string.split(output,"\n")
        # 1st point we try should bail out 
        self.assertEqual(lines[0:3],["(1.5,0)","(3.75,0)", "(1,0,0)"],output)

        # 2nd point doesn't
        self.assertEqual(lines[3],"(0.02,0.26)",output)
        self.assertEqual(lines[-1],"(20,1,0)",output)
        self.assertEqual(lines[-2],lines[-3],output)

        # try again with sqr function and check results match
        src = '''t_mandel{
init:
z = #zwpixel
loop:
z = sqr(z) + pixel
bailout:
|z| < 4.0
}'''
        t = self.translate(src)
        self.codegen.output_all(t)
        self.codegen.output_decls(t)
        c_code = self.codegen.output_c(t,inserts)
        output2 = self.compileAndRun(c_code)
        lines2 = string.split(output2,"\n")
        # 1st point we try should bail out 
        self.assertEqual(lines, lines2, output2)

        # and again with ^2
        src = '''t_mandel{
init:
z = #zwpixel
loop:
z = z^2 + pixel
bailout:
|z| < 4.0
}'''
        t = self.translate(src)
        self.codegen.output_all(t)
        self.codegen.output_decls(t)
        c_code = self.codegen.output_c(t,inserts)
        output3 = self.compileAndRun(c_code)
        lines3 = string.split(output2,"\n")
        # 1st point we try should bail out 
        self.assertEqual(lines, lines3, output3)

    def testFinal(self):
        # test that final section works
        src = '''t_mandel{
init:
loop:
z = z*z + pixel
bailout:
|z| < 4.0
final:
z = (-77.0,9.0)
float t = #tolerance
}'''
        t = self.translate(src)
        self.codegen.output_all(t)
        self.codegen.output_decls(t)
        
        inserts = {
            "main_inserts": self.main_stub,
            "done_inserts": "printf(\"(%g,%g,%g)\\n\",z_re,z_im,t);",
            "pre_final_inserts": "printf(\"(%g,%g)\\n\",z_re,z_im);"
            }
        c_code = self.codegen.output_c(t,inserts)
        #print c_code
        output = self.compileAndRun(c_code)
        lines = string.split(output,"\n")
        self.assertEqual(lines[1],"(-77,9,0.001)")
        self.assertEqual(lines[4],"(-77,9,0.001)")
        
    def testLibrary(self):
        # create a library containing the compiled code
        src = '''
Newton4(XYAXIS) {; Mark Peterson
  ; Note that floating-point is required to make this compute accurately
  z = pixel, Root = 1:
   z3 = z*z*z
   z4 = z3 * z
   z = (3 * z4 + Root) / (4 * z3)
    .004 <= |z4 - Root|
  }
'''
        t = self.translate(src)
        self.codegen.output_all(t)
        self.codegen.output_decls(t)
        c_code = self.codegen.output_c(t)

        cFileName = self.codegen.writeToTempFile(c_code,".c")
        oFileName = self.codegen.writeToTempFile(None,".so")
        #print c_code
        cmd = "gcc -Wall -fPIC -DPIC -shared %s -o %s -lm" % (cFileName, oFileName)
        (status,output) = commands.getstatusoutput(cmd)
        self.assertEqual(status,0,"C error:\n%s\nProgram:\n%s\n" % \
                         ( output,c_code))

        

    # assertions
    def assertCSays(self,source,section,check,result,dump=None):
        asm = self.sourceToAsm(source,section,dump)
        postamble = "t__end_%s:\n%s\n" % (section,check)
        c_code = self.makeC("", postamble)        
        output = self.compileAndRun(c_code)
        if isinstance(result,types.ListType):
            outputs = string.split(output,"\n")
            for (exp,res) in zip(result,outputs):
                self.assertEqual(exp,res)
        else:
            self.assertEqual(output,result)
        
    def assertOutputMatch(self,exp):
        str_output = string.join(map(lambda x : x.format(), self.codegen.out),"\n")
        self.assertEqual(str_output,exp)

    def assertMatchResult(self, tree, template,result):
        template = self.codegen.expand(template)
        self.assertEqual(self.codegen.match_template(tree,template),result,
                         "%s mismatches %s" % (tree.pretty(),template))


    
def suite():
    return unittest.makeSuite(CodegenTest,'test')

if __name__ == '__main__':
    # special cases for manual experiments.
    # ./test_codegen.py --x "(1,2)" --exp "1+2+x" compiles and runs 1+2+x
    # and prints the result

    try:
        index = sys.argv.index("--exp")
        g_exp = sys.argv[index+1]
        sys.argv[index] = "CodegenTest.testExpression"
        del sys.argv[index+1]
    except ValueError:
        pass
    
    try:
        index = sys.argv.index("--x")
        g_x = sys.argv[index+1]
        del sys.argv[index:index+2]
    except ValueError:
        pass
    
    unittest.main(defaultTest='suite')

