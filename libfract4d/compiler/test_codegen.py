#!/usr/bin/env python

import unittest
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
        
    def sourceToAsm(self,s,section):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        #print pt.pretty()
        ir = translate.T(pt.children[0])        
        self.codegen = codegen.T(symbol.T())
        self.codegen.generate_all_code(ir.sections["c_" + section])
        return self.codegen.out
    
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
        
    def assertMatchResult(self, tree, template,result):
        template = self.codegen.expand(template)
        self.assertEqual(self.codegen.match_template(tree,template),result,
                         "%s mismatches %s" % (tree.pretty(),template))

    def testWhichMatch(self):
        tree = self.binop([self.const(),self.const()])
        self.assertEqual(self.codegen.match(tree).__name__,"binop_exp_exp")

    def testGen(self):
        tree = self.binop([self.const(),self.var()])
        self.codegen.generate_code(tree)
        self.assertEqual(len(self.codegen.out),1)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))

    def testComplexAdd(self):
        # (1,3) + a
        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)],"+",Complex)
        self.generate_code(tree)
        self.assertEqual(len(self.codegen.out),2)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))

        expAdd = "t__temp0 = 1.00000000000000000 + a_re\n" + \
                 "t__temp1 = 3.00000000000000000 + a_im"
        self.assertOutputMatch(expAdd)

        # a + (1,3) gets reversed
        tree = self.binop([self.var("a",Complex),self.const([1,3],Complex)],"+",Complex)
        self.generate_code(tree)
        self.assertEqual(len(self.codegen.out),2)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))

        expAdd = "t__temp0 = a_re + 1.00000000000000000\n" + \
                 "t__temp1 = a_im + 3.00000000000000000"

        self.assertOutputMatch(expAdd)

    def testComplexMul(self):
        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)],"*",Complex)
        self.generate_code(tree)
        self.assertEqual(len(self.codegen.out),6)
        exp = '''t__temp0 = 1.00000000000000000 * a_re
t__temp1 = 3.00000000000000000 * a_im
t__temp2 = 3.00000000000000000 * a_re
t__temp3 = 1.00000000000000000 * a_im
t__temp4 = t__temp0 - t__temp1
t__temp5 = t__temp2 + t__temp3'''
        
        self.assertOutputMatch(exp)

    def testCompare(self):
        tree = self.binop([self.const(3,Int),self.var("a",Int)],">",Bool)
        self.generate_code(tree)
        self.assertOutputMatch("t__temp0 = 3 > a")

        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)],">",Complex)
        self.generate_code(tree)
        self.assertOutputMatch("t__temp0 = 1.00000000000000000 > a_re")

        tree.op = "=="
        self.generate_code(tree)
        self.assertOutputMatch('''t__temp0 = 1.00000000000000000 == a_re
t__temp1 = 3.00000000000000000 == a_im
t__temp2 = t__temp0 && t__temp1''')

        tree.op = "!="
        self.generate_code(tree)
        self.assertOutputMatch('''t__temp0 = 1.00000000000000000 != a_re
t__temp1 = 3.00000000000000000 != a_im
t__temp2 = t__temp0 || t__temp1''')

    def testS2A(self):
        asm = self.sourceToAsm('''t_s2a {
init:
int a = 1
loop:
z = z + a
}''', "loop")
        self.printAsm()


    def testFormatString(self):
        t = self.const(0,Int)
        self.assertEqual(self.codegen.format_string(t,-1,0),("0",0))

        t = self.const(0.5,Float)
        self.assertEqual(self.codegen.format_string(t,-1,0),("0.50000000000000000",0))

        t = self.const([1,4],Complex)
        self.assertEqual(self.codegen.format_string(t,0,0),
                         ("1.00000000000000000", 0))

        t = self.var("a",Int)
        self.assertEqual(self.codegen.format_string(t,0,0),("%(s0)s",1))

        
    def assertOutputMatch(self,exp):
        str_output = string.join(map(lambda x : x.format(), self.codegen.out),"\n")
        self.assertEqual(str_output,exp)
        
    def printAsm(self):
        for i in self.codegen.out:
            try:
                #print i
                print i.format()
            except Exception, e:
                print "Can't format %s:%s" % (i,e)
        
def suite():
    return unittest.makeSuite(CodegenTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

