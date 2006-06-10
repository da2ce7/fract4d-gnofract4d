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
        self.assertEqual(16777216, len(mm.nodes))

    def testGetIndex(self):
        mm = makemap.T()
        self.assertEqual(0x000000,mm.getIndex(0,0,0,8))
        self.assertEqual(0x010000,mm.getIndex(1,0,0,8))
        self.assertEqual(0x000100,mm.getIndex(0,1,0,8))
        self.assertEqual(0x000001,mm.getIndex(0,0,1,8))

        self.assertEqual(0x400308,mm.getIndex(0x40,3,8,8))
        self.assertEqual(0xffffff,mm.getIndex(0xff,0xff,0xff,8))

        self.assertEqual(0x20 << 12 | 0x10 << 6 | 0x1 ,
                         mm.getIndex(0x80,0x41,0x7,6))
    
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
        self.assertEqual(50, mm.nodes[0])
        self.assertEqual(50, mm.nodes[0xffffff])

    def testPopularity(self):
        mm = makemap.T()
        mm.load(open("test001.png","rb"))
        mm.build()

        # contains 50 black, 10 white, 15 d80000, 25 ff0000 pixels
        self.assertEqual(50, mm.nodes[0])
        self.assertEqual(10, mm.nodes[0xffffff])
        self.assertEqual(15, mm.nodes[0xd80000])
        self.assertEqual(25, mm.nodes[0xff0000])

        mp = mm.most_popular(3)
        self.assertEqual([0,0xff0000, 0xd80000 ], mp)

    def testChildren(self):
        mm = makemap.T()
        children = mm.children(0,0,0,8)
        print ["%06x" % x for x in children]

        children = mm.children(0,0,0,2)
        print ["%06x" % x for x in children]

        children = mm.children(0xfe,0xfe,0xfe,8)
        print ["%06x" % x for x in children]

    def disabled_testTatteredPopularity(self):
        mm = makemap.T()
        mm.load(open("tattered.jpg","rb"))
        mm.build()
        mp = mm.most_popular(20)
        for c in mp:
            (r,g,b) = (c >> 16, c >> 8 & 0xff, c & 0xff)
            print "%d %d %d" % (r,g,b)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

