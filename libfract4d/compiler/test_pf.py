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

    def testBasic(self):
        handle = pf.load("./test-out.so")
        pfunc = pf.create(handle)

        # 1 param
        pf.init(pfunc,0.001,[0.5])
        # empty param array
        pf.init(pfunc,0.001,[])

        # a point which doesn't bail out
        result = pf.calc(pfunc,[1.5,0.0,0.0,0.0],100,100,0,0,0)
        self.assertEqual(result,(100,1,0.0)) 
        # one which does
        result = pf.calc(pfunc,[17.5,14.0,0.0,0.0],100,100,0,0,0)
        self.assertEqual(result,(1,0,0.0)) 
        
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

    def testBadInit(self):
        handle = pf.load("./test-out.so")
        pfunc = pf.create(handle)
        self.assertRaises(TypeError,pf.init,pfunc,0.001,72)
        self.assertRaises(ValueError,pf.init,7,0.00,[0.4])
        self.assertRaises(ValueError,pf.init,pfunc,0.001,[0.0]*21)
        pfunc = None
        handle = None
        
def suite():
    return unittest.makeSuite(PfTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


