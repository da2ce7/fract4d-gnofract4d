#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path
import struct
import math
import types

import testbase

import image

class Test(testbase.TestBase):
    def testColossalImage(self):
        try:
            im = image.T(400000,300000)
            self.fail("Should have raised an exception")
        except MemoryError, err:
            pass

        im = image.T(40,30)
        try:
            im.resize(400000,300000)
            self.fail("Should have raised an exception")
        except MemoryError, err:
            self.assertEqual(40, im.xsize)
            self.assertEqual(30, im.ysize)
            pass

    def assertImageInvariants(self, im):
        self.assertEqual(im.xsize*im.ysize*im.FATE_SIZE, len(im.fate_buffer()))
        self.assertEqual(im.xsize*im.ysize*im.COL_SIZE, len(im.image_buffer()))
        
    def testResize(self):
        im = image.T(10,20)
        self.assertEqual(10,im.xsize)
        self.assertEqual(20,im.ysize)
        self.assertImageInvariants(im)
        
        im.resize(30,17)
        self.assertEqual(30,im.xsize)
        self.assertEqual(17,im.ysize)
        self.assertImageInvariants(im)
        
    def testClear(self):
        # check clear() works
        (xsize,ysize) = (61,33)
        im = image.T(xsize, ysize)
        im.clear()
        buf = im.image_buffer()
        fate_buf = im.fate_buffer()
        self.assertEqual(
            list(fate_buf), [chr(im.UNKNOWN)] * im.FATE_SIZE * xsize * ysize)

        bytes = map(ord,list(buf))
        self.assertEqual(bytes, [0] * xsize * ysize * im.COL_SIZE)

    def testBufferBounds(self):
        im = image.T(40,30)
        im.resize(80,60)
        buf = im.image_buffer()
        fate_buf = im.fate_buffer()

        self.assertRaises(ValueError,im.image_buffer, -1, 0)
        self.assertRaises(ValueError,im.image_buffer, 80, 0)
        self.assertRaises(ValueError,im.image_buffer, 41, 67)

        self.assertRaises(ValueError,im.fate_buffer, -1, 0)
        self.assertRaises(ValueError,im.fate_buffer, 80, 0)
        self.assertRaises(ValueError,im.fate_buffer, 41, 67)

        buf = im.image_buffer(5,10)
        self.assertEqual(len(buf),80*60*im.COL_SIZE - (10*80+5)*im.COL_SIZE)
        
        buf = im.fate_buffer(5,10)
        self.assertEqual(len(buf),80*60*im.FATE_SIZE - (10*80+5)*im.FATE_SIZE)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


