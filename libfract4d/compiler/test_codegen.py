#!/usr/bin/env python

import unittest
import ir
import symbol
from fracttypes import *
import codegen

class CodegenTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def testStub(self):
        pass
    
def suite():
    return unittest.makeSuite(CodegenTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

