#!/usr/bin/env python

import unittest
import tempfile
import os
import commands

import absyn
import ir
import symbol
from fracttypes import *
import codegen
import translate
import fractparser
import fractlexer

class CodegenTest(unittest.TestCase):
    def setUp(self):
        self.fakeNode = absyn.Empty(0)
        self.codegen = codegen.T(symbol.T())
        self.parser = fractparser.parser
        
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
        if dump != None and dump["dumpAsm"] == 1:
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
        preamble = "#include <stdio.h>\nint main(){\n"
        decls = string.join(map(lambda x: x.format(),
                                self.codegen.output_symbols({})),"\n")
        str_output = string.join(map(lambda x : x.format(), self.codegen.out),"\n")
        postamble = "\nreturn 0;}\n"

        return string.join([preamble,decls,"\n",
                            user_preamble,str_output,"\n",
                            user_postamble,postamble],"")

    def writeToTempFile(self,data=None,suffix=""):
        'try mkstemp or mktemp if missing'
        try:
            (cFile,cFileName) = tempfile.mkstemp("gf4d",suffix)
        except AttributeError, err:
            # this python is too antique for mkstemp
            cFileName = tempfile.mktemp(suffix)
            cFile = open(cFileName,"w+b")

        if data != None:
            cFile.write(data)
        cFile.close()
        return cFileName
    
    def compileAndRun(self,c_code):
        cFileName = self.writeToTempFile(c_code,".c")
        oFileName = self.writeToTempFile("")
        #print c_code
        cmd = "gcc -Wall %s -o %s" % (cFileName, oFileName)
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
t__temp0 = ((double)0);
t__temp1 = t__temp0 - 1.50000000000000000;
t__temp2 = t__temp1;
t__temp3 = 0.0;
a_re = t__temp2;
a_im = t__temp3;
goto t__end_init;''')
        
    def testSymbols(self):
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

    def inspect_complex(self,name):
        return "printf(\"%s = (%%g,%%g)\\n\", %s_re, %s_im);" % (name,name,name)
    
    def test_stdlib(self):
        tests = [
            # code to run, var to inspect, result
            [ "cj = conj(y)", "cj", "(1,-2)"],
            [ "fl = flip(y)", "fl", "(2,1)"],
            [ "ri = (imag(y),real(y))","ri", "(2,1)"]
            ]

        src = 't_c6{\ninit: y = (1,2)\n' + \
              string.join(map(lambda x : x[0], tests),"\n") + "\n}"

        check = string.join(map(lambda x : self.inspect_complex(x[1]),tests),"\n");
        
        exp = string.join(map(lambda x : "%s = %s" % (x[1],x[2]), tests),"\n")

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
            "main_inserts":'''
int main()
{
    double params[4] = { 0.0, 0.0, 1.5, 0.0 };
    int nItersDone=0;
    pf_calc(params, 100, &nItersDone);
    printf("(%d)\\n",nItersDone);

    params[0] = 0.1; params[1] = 0.3; params[2]= 0.1; params[3] = 0.2;
    pf_calc(params, 20, &nItersDone);
    printf("(%d)\\n",nItersDone);
        
    return 0;
}
'''
            }
        c_code = self.codegen.output_c(t,inserts)
        #print c_code
        output = self.compileAndRun(c_code)
        lines = string.split(output,"\n")
        # 1st point we try should bail out 
        self.assertEqual(lines[0:3],["(1.5,0)","(3.75,0)", "(2)"],output)

        # 2nd point doesn't
        self.assertEqual(lines[3],"(0.02,0.26)",output)
        self.assertEqual(lines[-1],"(20)",output)
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
        return # not working yet
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
        
    # assertions
    def assertCSays(self,source,section,check,result,dump=None):
        asm = self.sourceToAsm(source,section,dump)
        postamble = "t__end_%s:\n%s\n" % (section,check)
        c_code = self.makeC("", postamble)
        output = self.compileAndRun(c_code)
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

