#!/usr/bin/env python

import unittest

import makemap

class Test(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def testAllocate(self):
        mm = makemap.T()

        self.assertEqual(None,mm.root)

    def testAddOnePixel(self):
        mm = makemap.T()
        mm.insert_pixel(0,0,0)
        n = mm.root
        self.assertEqual((0,0,0,1), (n.r, n.g, n.b, n.count))

    def testAddOnePixelTwice(self):
        mm = makemap.T()
        mm.insert_pixel(0,0,0)
        mm.insert_pixel(0,0,0)
        n = mm.root
        self.assertEqual((0,0,0,2), (n.r, n.g, n.b, n.count))

    def testAddTwoPixels(self):
        mm = makemap.T()
        mm.insert_pixel(0,0,0)
        mm.insert_pixel(0xff,0xff,0xff)
        self.checkTwoPixels(mm)
        
    def testAddTwoPixelsReversed(self):
        mm = makemap.T()
        mm.insert_pixel(0xff,0xff,0xff)
        mm.insert_pixel(0,0,0)
        self.checkTwoPixels(mm)

    def checkTwoPixels(self,mm):
        n = mm.root
        self.assertEqual((127,127,127,0), (n.r, n.g, n.b, n.count))
        n1 = n.branches[0]
        self.assertEqual((0,0,0,1), (n1.r, n1.g, n1.b, n1.count))
        n2 = n.branches[7]
        self.assertEqual((0xff,0xff,0xff,1), (n2.r, n2.g, n2.b, n2.count))

    def testAddThreePixels(self):
        mm = makemap.T()
        mm.insert_pixel(0xff,0xff,0xff)
        mm.insert_pixel(0,0,0)
        mm.insert_pixel(0xff,0x00,0x00)
        self.checkThreePixels(mm)

    def checkThreePixels(self,mm):
        self.checkTwoPixels(mm)
        n3 = mm.root.branches[4]
        self.assertEqual((0xff,0x00,0x00,1), (n3.r, n3.g, n3.b, n3.count))

    def testAddTwoPixelsToSameBranch(self):
        mm = makemap.T()
        mm.insert_pixel(0xff,0xff,0xff)
        mm.insert_pixel(0x80,0x80,0x80)
        r = mm.root
        self.assertEqual(False,r.isleaf())
        b = r.branches[7]
        self.assertEqual(False,b.isleaf())

    def testAddTwoVerySimilarPixels(self):
        mm = makemap.T()
        mm.insert_pixel(0xff,0xff,0xff)
        mm.insert_pixel(0xff,0xff,0xfe)
        r = mm.root
        depth=0
        n = 127
        size = 64
        while not r.branches[7].isleaf():
            self.assertEqual((r.r,r.g,r.b),(n,n,n))
            n = n + size
            size = size / 2
            depth += 1
            r = r.branches[7]
        self.assertEqual(7, depth)
        self.assertEqual(False, r.isleaf())
        self.assertEqual((0xfe,0xfe,0xfe,0), (r.r, r.g, r.b, r.count))
        leaf1 = r.branches[6]
        self.assertEqual((0xff,0xff,0xfe,1),
                         (leaf1.r, leaf1.g, leaf1.b, leaf1.count))
        leaf2 = r.branches[7]
        self.assertEqual((0xff,0xff,0xff,1),
                         (leaf2.r, leaf2.g, leaf2.b, leaf2.count))

        
    def testNode(self):
        n = makemap.Node(0,0,0,0)
        self.assertEqual([None]*8, n.branches)

        self.assertEqual(True, n.isleaf())
        
    def testLoadPicture(self):
        'Load a very simple test image and check correctly parsed'
        mm = makemap.T()
        mm.load(open("test000.png","rb"))

        seq = mm.getdata()
        self.assertEqual(len(seq),10 * 10)
        i = 0
        for pix in seq:
            if i % 10 < 5:
                # left half of image is black
                self.assertEqual(pix,(0,0,0))
            else:
                # right half is white
                self.assertEqual(pix,(255,255,255))
            i+= 1
            
        mm.build()
        r = mm.root
        self.assertEqual(False, r.isleaf())
        blackNode = r.branches[0]
        whiteNode = r.branches[7]
        self.assertEqual(blackNode.count,50)
        self.assertEqual(whiteNode.count,50)
        
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

