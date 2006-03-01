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
import fract4dc

class Test(testbase.TestBase):
    def testColossalImage(self):
        try:
            image = fract4dc.image_create(400000,300000)
            self.fail("Should have raised an exception")
        except MemoryError, err:
            pass

        image = fract4dc.image_create(40,30)
        try:
            fract4dc.image_resize(image, 400000,300000)
            self.fail("Should have raised an exception")
        except MemoryError, err:
            pass

    def testImage(self):
        image = fract4dc.image_create(40,30)
        fract4dc.image_resize(image,80,60)
        buf = fract4dc.image_buffer(image)
        self.assertEqual(len(buf),80*60*3)

        fate_buf = fract4dc.image_fate_buffer(image)
        self.assertEqual(len(fate_buf),80*60*4)
        
        bytes = list(buf)
        self.assertEqual(ord(bytes[0]),0)
        self.assertEqual(ord(bytes[1]),0)
        self.assertEqual(ord(bytes[2]),0)

        fate_bytes = list(fate_buf)
        for fb in fate_bytes:
            self.assertEqual(ord(fb), 255)
            
        self.assertRaises(ValueError,fract4dc.image_buffer, image, -1, 0)
        self.assertRaises(ValueError,fract4dc.image_buffer, image, 80, 0)
        self.assertRaises(ValueError,fract4dc.image_buffer, image, 41, 67)

        self.assertRaises(ValueError,fract4dc.image_fate_buffer, image, -1, 0)
        self.assertRaises(ValueError,fract4dc.image_fate_buffer, image, 80, 0)
        self.assertRaises(ValueError,fract4dc.image_fate_buffer, image, 41, 67)

        buf = fract4dc.image_buffer(image,5,10)
        self.assertEqual(len(buf),80*60*3 - (10*80+5)*3)
        
        buf = fract4dc.image_fate_buffer(image,5,10)
        self.assertEqual(len(buf),80*60*4 - (10*80+5)*4)
        
    def printStuff(self):
        print
        for y in xrange(xsize):
            lower = ""
            upper = ""
            for x in xrange(ysize):
                fract4dc.fw_pixel(fw,x,y,1,1)
                fract4dc.fw_pixel_aa(fw,x,y)
                fates = iw.get_all_fates(x,y)
                upper += "%2x%2x " % (fates[0],fates[1])
                lower += "%2x%2x " % (fates[2],fates[3])
            print upper
            print lower
        print

    def print_fates(self,image,x,y):
        buf = fract4dc.image_fate_buffer(image)
        for i in xrange(len(buf)):
            v = ord(buf[i])
            if v == 255:
                print "U",
            else:
                print v,
                
            if i % (x*4) == 4*x-1:
                print ""            

def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


