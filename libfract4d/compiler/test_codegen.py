#!/usr/bin/env python

import unittest
import absyn
import ir
import symbol
from fracttypes import *
import codegen

class CodegenTest(unittest.TestCase):
    def setUp(self):
        self.fakeNode = absyn.Empty(0)
        self.codegen = codegen.T(symbol.T())

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
    def binop(self,stms,op="+"):
        return ir.Binop(op,stms,self.fakeNode, Int)
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
        self.assertEqual(self.codegen.match(tree).__name__,"binop_const_exp")

    def testGen(self):
        tree = self.binop([self.const(),self.var()])
        self.codegen.generate_code(tree)
        self.assertEqual(len(self.codegen.out),1)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))

    def testGenComplex(self):
        tree = self.binop([self.const([1,3],Complex),self.var("a",Complex)])
        tree.datatype = Complex
        self.codegen.generate_code(tree)
        self.assertEqual(len(self.codegen.out),2)
        self.failUnless(isinstance(self.codegen.out[0],codegen.Oper))
            
        self.assertEqual(self.codegen.out[0].format(), "t__temp0 = 1 + a_re")
        self.assertEqual(self.codegen.out[1].format(), "t__temp1 = 3 + a_im")

    def printAsm(self):
        for i in self.codegen.out:
            print i
        
def suite():
    return unittest.makeSuite(CodegenTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

