#!/usr/bin/env python

# unit tests for renderqueue module

import unittest
import sys
import os
import commands

import gtk

import renderqueue

sys.path.append("..")

from fract4d import fractal, image

class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testRQ(self):
        rq = renderqueue.T()
                
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
