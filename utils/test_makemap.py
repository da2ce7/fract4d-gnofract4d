#!/usr/bin/env python

import unittest

import makemap

class Test(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def testLoadPicture(self):
        'Load a very simple test image and check correctly parsed'
        mm = makemap.T(open("test000.png","rb"))

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
            
        mm.build_octree()
        self.assertEqual(isinstance(mm.root,makemap.Node),True)

    def test_adjust_dimension(self):
        mm = makemap.T(open("test000.png","rb"))

        min = [0,0,0]
        max = [201,201,201]

        self.assertEqual(mm.mid(0,200),100)
        self.assertEqual(mm.mid(0,201),100)

        self.assertEqual(mm.adjust_dimension(min,max,7,0), False)
        self.assertEqual(min[0],0)
        self.assertEqual(max[0],101)

        self.assertEqual(mm.adjust_dimension(min,max,187,1), True)
        self.assertEqual(min[1],100)
        self.assertEqual(max[1],201)
        
    def test_which_child(self):
        mm = makemap.T(open("test000.png","rb"))

        min = [0,0,0]
        max = [201,201,201]

        self.assertEqual(mm.which_child(min,max,1,120,101), 3) # g & b, not r
        self.assertEqual(min,[0,100,100])
        self.assertEqual(max,[101,201,201])
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

