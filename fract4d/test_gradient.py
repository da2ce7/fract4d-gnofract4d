#!/usr/bin/env python

import unittest

import testbase
import sys

import gradient

class Test(testbase.TestBase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testLoad(self):
        g = gradient.Gradient()

        self.assertEqual(len(g.segments), 2)
        first_seg = g.segments[0]
        last_seg = g.segments[-1]
        self.assertEqual(first_seg[2][0], 0.0)
        self.assertEqual(last_seg[3][0], 1.0)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
