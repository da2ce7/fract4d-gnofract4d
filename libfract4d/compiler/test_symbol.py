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
                        
def suite():
    return unittest.makeSuite(SymbolTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

