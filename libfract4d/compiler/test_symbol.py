#!/usr/bin/env python

# test symbol table implementation

import symbol
import unittest
from fracttypes import *

class SymbolTest(unittest.TestCase):
    def setUp(self):
        self.t = symbol.T()

    def tearDown(self):
        pass

    def testSqr(self):
        self.failUnless(isinstance(self.t[("sqr",[Complex])], Func))
        self.failUnless(isinstance(self.t[("sqR",[Int])], Func))

    def testNoOverride(self):
        self.assertRaises(KeyError,self.t.__setitem__,("sqr",[Complex]),1)

    def testAddCheckVar(self):
        self.t["fish"] = Var(Int,1)
        x = self.t["fish"]
        self.failUnless(isinstance(x,Var) and x.value == 1 and x.type == Int)
        
def suite():
    return unittest.makeSuite(SymbolTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

