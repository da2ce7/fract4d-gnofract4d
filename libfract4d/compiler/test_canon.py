#!/usr/bin/env python

# unit tests for canon module

import unittest
import canon
import absyn
import ir
from fracttypes import *

class CanonTest(unittest.TestCase):
    def setUp(self):
        self.fakeNode = absyn.Empty(0)
    def tearDown(self):
        pass

    # convenience methods to make quick trees for testing
    def eseq(self,stms, exp):
        return ir.ESeq(stms, exp, self.fakeNode, Int)
    def var(self,name="a"):
        return ir.Var(name,self.fakeNode, Int)
    def const(self,value=0):
        return ir.Const(value, self.fakeNode, Int)
    def binop(self,stms,op="+"):
        return ir.Binop(op,stms,self.fakeNode, Int)
    def move(self,dest,exp):
        return ir.Move(dest, exp, self.fakeNode, Int)
    
    def testEmptyTree(self):
        self.assertEqual(canon.linearize(None),None)

    def testBinop(self):
        tree = self.binop([self.var(), self.const()])
        ltree = canon.linearize(tree)
        self.assertTreesEqual(tree, ltree)

        tree = self.binop([self.eseq([self.move(self.var(),self.const())],
                                      self.var("b")),
                           self.const()])

        ltree = canon.linearize(tree)
        self.failUnless(isinstance(ltree,ir.ESeq) and \
                        isinstance(ltree.children[0],ir.Move) and \
                        isinstance(ltree.children[1],ir.Binop) and \
                        isinstance(ltree.children[1].children[0],ir.Var))
        
    def assertTreesEqual(self, t1, t2):
        self.failUnless(
            t1.pretty() == t2.pretty(),
            ("%s, %s should be equivalent" % (t1.pretty(), t2.pretty())))

def suite():
    return unittest.makeSuite(CanonTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

