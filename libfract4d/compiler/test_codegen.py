#!/usr/bin/env python

import unittest
import tempfile
import os
import commands
import math
import cmath

import absyn
import ir
import symbol
from fracttypes import *
import codegen
import translate
import fractparser
import fractlexer
import stdlib

class CodegenTest(unittest.TestCase):
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
        self.assertNoErrors(t)
        self.codegen = codegen.T(t.symbols,dump)
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
        pf_fake f;
        f.p = params;
        pf_fake *pfo = &f;
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
        z = self.codegen.symbols["z"] # ping z to get it in output list
        out = self.codegen.output_symbols({})
        l = [x for x in out if x.assem == "double z_re = 0.00000000000000000;"]
        self.failUnless(len(l)==1)
        out = self.codegen.output_symbols({ "z" : "foo"})
        l = [x for x in out if x.assem == "foo"]
        self.failUnless(len(l)==1)
        
    def testC(self):
        # basic end-to-end testing. Compile a code fragment + instrumentation,
        # run it and check output
        src = 't_c1 {\nloop: int a = 1\nz = z + a\n}'
        self.assertCSays(src,"loop","printf(\"%g,%g\\n\",z_re,z_im);","1,0")
        
        src = '''t_c2{\ninit:int a = 1 + 3 * 7\n}'''
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
        
    def testUseBeforeAssign(self):
        src = 't_uba0{\ninit: z = z - x\n}'
        self.assertCSays(src,"init",self.inspect_complex("z"),
                         "z = (0,0)")
        
    def inspect_complex(self,name):
        return "printf(\"%s = (%%g,%%g)\\n\", %s_re, %s_im);" % (name,name,name)

    def predict(self,f,arg1=0,arg2=1):
        # compare our compiler results to Python stdlib
        return "(%.6g,%.6g)" % (f(arg1),f(arg2))

    def cpredict(self,f,arg=(1+0j)):
        try:
            z = f(arg)
            return "(%.6g,%.6g)" % (z.real,z.imag) 
        except OverflowError:
            return "(inf,inf)"
    
    def make_test(self,myfunc,pyfunc,val,n):
        codefrag = "ct_%s%d = %s((%d,%d))" % (myfunc, n, myfunc, val.real, val.imag)
        lookat = "ct_%s%d" % (myfunc, n)
        result = self.cpredict(pyfunc,val)
        return [ codefrag, lookat, result]
        
    def manufacture_tests(self,myfunc,pyfunc):
        vals = [ 0+0j, 0+1j, 1+0j, 1+1j, 3+2j, 1-0j, 0-1j ]
        return map(lambda (x,y) : self.make_test(myfunc,pyfunc,x,y), \
                   zip(vals,range(1,len(vals))))
                                
    def test_stdlib(self):
        tests = [
            # code to run, var to inspect, result
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
            # trig functions
            [ "t_sin = (sin(0),sin(1))","t_sin", self.predict(math.sin)],
            [ "t_cos = (cos(0),cos(1))","t_cos", self.predict(math.cos)],
            [ "t_tan = (tan(0),tan(1))","t_tan", self.predict(math.tan)],
            [ "t_sinh = (sinh(0),sinh(1))","t_sinh", self.predict(math.sinh)],
            [ "t_cosh = (cosh(0),cosh(1))","t_cosh", self.predict(math.cosh)],
            [ "t_tanh = (tanh(0),tanh(1))","t_tanh", self.predict(math.tanh)],

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
        logtests = self.manufacture_tests("log",cmath.log)
        
        logtests[0][2] = "(-inf,0)" # log(0+0j) is overflow in python
        tests += logtests

        
        
        src = 't_c6{\ninit: y = (1,2)\n' + \
              string.join(map(lambda x : x[0], tests),"\n") + "\n}"

        check = string.join(map(lambda x : self.inspect_complex(x[1]),tests),"\n")

        #check = check + "printf(\"temp52 = %g\\\n\", t__temp52);"
        exp = map(lambda x : "%s = %s" % (x[1],x[2]), tests)

        self.assertCSays(src,"init",check,exp)

    def testMandel(self):
        src = '''t_mandel{
init:
loop:
z = z*z + pixel
bailout:
|z| < 4.0
}'''
        t = self.translate(src)
        self.codegen.output_all(t, {"z" : "", "pixel" : ""} )

        inserts = {
            "loop_inserts":"printf(\"(%g,%g)\\n\",z_re,z_im);",
            "main_inserts": self.main_stub
            }
        c_code = self.codegen.output_c(t,inserts)
        #print c_code
        output = self.compileAndRun(c_code)
        lines = string.split(output,"\n")
        # 1st point we try should bail out 
        self.assertEqual(lines[0:3],["(1.5,0)","(3.75,0)", "(2,0,0)"],output)

        # 2nd point doesn't
        self.assertEqual(lines[3],"(0.02,0.26)",output)
        self.assertEqual(lines[-1],"(20,1,0)",output)
        self.assertEqual(lines[-2],lines[-3],output)

        # try again with sqr function and check results match
        src = '''t_mandel{
init:
loop:
z = sqr(z) + pixel
bailout:
|z| < 4.0
}'''
        t = self.translate(src)
        self.codegen.output_all(t, {"z" : "", "pixel" : ""} )
        c_code = self.codegen.output_c(t,inserts)
        output2 = self.compileAndRun(c_code)
        lines2 = string.split(output2,"\n")
        # 1st point we try should bail out 
        self.assertEqual(lines, lines2, output2)

        # and again with ^2
        src = '''t_mandel{
init:
loop:
z = z^2 + pixel
bailout:
|z| < 4.0
}'''
        t = self.translate(src)
        self.codegen.output_all(t, {"z" : "", "pixel" : ""} )
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
}'''
        t = self.translate(src)
        self.codegen.output_all(t, {"z" : "", "pixel" : ""} )

        inserts = {
            "main_inserts": self.main_stub,
            "done_inserts": "printf(\"(%g,%g)\\n\",z_re,z_im);",
            "pre_final_inserts": "printf(\"(%g,%g)\\n\",z_re,z_im);"
            }
        c_code = self.codegen.output_c(t,inserts)
        #print c_code
        output = self.compileAndRun(c_code)
        lines = string.split(output,"\n")
        self.assertEqual(lines[1],"(-77,9)")
        self.assertEqual(lines[4],"(-77,9)")
        
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
        self.codegen.output_all(t, {"z" : "", "pixel" : ""} )
        c_code = self.codegen.output_c(t)

        cFileName = self.codegen.writeToTempFile(c_code,".c")
        oFileName = self.codegen.writeToTempFile(None,".so")
        #print c_code
        cmd = "gcc -Wall -fPIC -dPIC -shared %s -o %s -lm" % (cFileName, oFileName)
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

    def assertNoErrors(self,t):
        self.assertEqual(len(t.errors),0,
                         "Unexpected errors %s" % t.errors)
    def assertMatchResult(self, tree, template,result):
        template = self.codegen.expand(template)
        self.assertEqual(self.codegen.match_template(tree,template),result,
                         "%s mismatches %s" % (tree.pretty(),template))


    
def suite():
    return unittest.makeSuite(CodegenTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

