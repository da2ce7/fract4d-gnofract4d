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

        self.assertEqual(len(g.segments), 4)
        self.assertWellFormedGradient(g)
        
    def assertWellFormedGradient(self, g):
        # check starts and sends at 0 and 1
        first_seg = g.segments[0]
        last_seg = g.segments[-1]
        self.assertEqual(first_seg.left.pos, 0.0)
        self.assertEqual(last_seg.right.pos, 1.0)

        # check segments line up
        previous_seg = g.segments[0]
        for seg in g.segments[1:]:
            self.failUnless(seg.right.pos > seg.left.pos)
            self.failUnless(seg.left.pos == previous_seg.right.pos)
            previous_seg = seg
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
