#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path
import struct
import math
import types
import filecmp
import commands

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
            # retains large size even if allocation fails
            self.assertEqual(400000, im.xsize)
            self.assertEqual(300000, im.ysize)
            pass

    def assertImageInvariants(self, im):
        self.assertEqual(im.xsize*im.ysize*im.FATE_SIZE, len(im.fate_buffer()))
        self.assertEqual(im.xsize*im.ysize*im.COL_SIZE, len(im.image_buffer()))

    def testInvalidImages(self):
        self.assertRaises(ValueError, image.T, 0, 100)
        self.assertRaises(ValueError, image.T, 100, 0)
        self.assertRaises(ValueError, image.T, 0, 0)
        
    def testTiledImage(self):
        # check defaults work OK
        im = image.T(40,30)
        self.assertEqual(40, im.total_xsize)
        self.assertEqual(30, im.total_ysize)
        self.assertEqual(0, im.xoffset)
        self.assertEqual(0, im.yoffset)
        
        # check a different total size is honored
        im = image.T(40,30,400,300)
        self.assertEqual(400, im.total_xsize)
        self.assertEqual(300, im.total_ysize)
        self.assertEqual(0, im.xoffset)
        self.assertEqual(0, im.yoffset)

        # check offset has an effect
        im.set_offset(40,30)
        self.assertEqual(40, im.xoffset)
        self.assertEqual(30, im.yoffset)

        # check offset bounds-checking
        self.assertRaises(ValueError, im.set_offset, 400,0)
        self.assertRaises(ValueError, im.set_offset, 361,0)
        self.assertRaises(ValueError, im.set_offset, 0,300)
        self.assertRaises(ValueError, im.set_offset, 0,271)
        self.assertRaises(ValueError, im.set_offset, -1,0)
        self.assertRaises(ValueError, im.set_offset, 0,-1)

        # check offset wasn't changed
        self.assertEqual(40, im.xoffset)
        self.assertEqual(30, im.yoffset)

    def testTileList(self):
        # a single tile
        im = image.T(100,50)
        self.assertEqual(
            [(0,0,100,50)],
            im.get_tile_list())

        # 2 wide, 1 high
        im = image.T(100,50,200,50)
        self.assertEqual(
            [ (0,0, 100,50) ,(100,0,100,50)],
            im.get_tile_list())

        # 2 high, 1 wide
        im = image.T(100,50,100,100)
        self.assertEqual(
            [ (0,0, 100,50) ,(0,50,100,50)],
            im.get_tile_list())

        # not evenly divisible, odd-shaped chunks at edges
        im = image.T(100,50,101,51)
        self.assertEqual(
            [ (0,0,100,50), (100,0,1,50),
              (0,50,100,1,), (100,50,1,1)],
            im.get_tile_list())

    def testSaveTGA(self):
        self.doTestSave("tga","TGA")
        self.doTestSave("TGA","TGA")

    def testSavePNG(self):
        self.doTestSave("png","PNG")
        self.doTestSave("PNG","PNG")

    def testSaveJPEG(self):
        self.doTestSave("jpg","JPEG")
        self.doTestSave("JPG","JPEG")
        self.doTestSave("jpeg","JPEG")
        self.doTestSave("JPEG","JPEG")

    def testFileExtensionLookup(self):
        im = image.T(40,30)
        self.assertRaises(ValueError, im.file_type, "hello.gif")
        self.assertRaises(ValueError, im.file_type, "hello")
        
    def assertImageFileFormat(self, name, format):
        # run ImageMagick to test file contents
        (status,output) = commands.getstatusoutput("identify %s" % name)
        self.assertEqual(status,0)
        fields = output.split()
        self.assertEqual(fields[0],name)
        self.assertEqual(fields[1],format)
        self.assertEqual(fields[2],"640x400")
        
    def doTestSave(self,ext,format):
        f1 = "save1.%s" % ext
        f2 = "save2.%s" % ext
        try:
            im = image.T(640,400)
            im.save(f1)
            self.failUnless(os.path.exists(f1))
            self.assertImageFileFormat(f1,format)
            
            im = image.T(640,40,640,400)
            im.start_save(f2)
            for (xoff,yoff,w,h) in im.get_tile_list():
                im.resize(w,h)
                im.set_offset(xoff,yoff)
                im.save_tile()
            im.finish_save()
            self.failUnless(os.path.exists(f2))
            self.assertImageFileFormat(f2,format)
            
            self.assertEqual(True, filecmp.cmp(f1,f2,False))
                        
        finally:
            if os.path.exists(f1):
                os.remove(f1)
            if os.path.exists(f2):
                os.remove(f2)

    def saveAndCheck(self,name,format):
        im = image.T(640,400)
        im.save(name)
        self.failUnless(os.path.exists(name))
        self.assertImageFileFormat(name,format)
            
    def testBadSaves(self):
        try:
            self.saveAndCheck("test.gif","GIF")
            self.fail("No exception thrown")
        except ValueError, err:
            self.assertEqual(
                str(err),
                "Unsupported file format '.gif'. Please use one of: .JPEG, .JPG, .PNG, .TGA")

        try:
            self.saveAndCheck("no_extension","GIF")
            self.fail("No exception thrown")
        except ValueError, err:
            self.assertEqual(
                str(err),
                "No file extension in 'no_extension'. " +
                "Can't determine file format. " +
                "Please use one of: .JPEG, .JPG, .PNG, .TGA")

        try:
            self.saveAndCheck("no_such_dir/test.png","PNG")
            self.fail("No exception thrown")
        except IOError, err:
            self.assertEqual(
                str(err),
                "Unable to save image to 'no_such_dir/test.png' : " +
                "No such file or directory")

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


