#!/usr/bin/env python

import unittest
import string
import sys


sys.path.append("build/lib.linux-i686-2.2") # FIXME
import pf

class PfTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testLoad(self):
        handle = pf.load("./test-out.so")
        pfunc = pf.create(handle)
        pf.init(pfunc,0.001,[0.5])
        pfunc = None
        handle = None

    def testBadLoad(self):
        # wrong arg type/number
        self.assertRaises(TypeError,pf.load,1)
        self.assertRaises(TypeError,pf.load,"foo","bar")

        # nonexistent
        self.assertRaises(ValueError,pf.load,"garbage.xxx")

        # not a DLL
        self.assertRaises(ValueError,pf.load,"test_pf.py")
        
def suite():
    return unittest.makeSuite(PfTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


