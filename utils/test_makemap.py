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
        length = 200

        self.assertEqual(mm.adjust_dimension(min,length,7,0), False)
        self.assertEqual(min[0],0)

        self.assertEqual(mm.adjust_dimension(min,length,187,1), True)
        self.assertEqual(min[1],100)
        
    def test_which_child(self):
        mm = makemap.T(open("test000.png","rb"))

        min = [0,0,0]
        length = 200

        # g & b, not r
        self.assertEqual(mm.which_child(min,length,1,120,100), 3) 
        self.assertEqual(min,[0,100,100])

    def test_insert_pixel(self):
        mm = makemap.T(open("test000.png","rb"))

        mm.root = makemap.Node()
        mm.insert_pixel(0,0,255) # blue-only pixel

        self.assertEqual(mm.root.n_tree_pixels,1)
        self.assertEqual(mm.root.n_local_pixels,0)

        self.assertChildSequence(mm.root,[1] * 8,1)

        mm.insert_pixel(128,7,1) # other color
        self.assertEqual(mm.root.n_tree_pixels,2)

        red_bits =   [1,0,0,0,0,0,0,0]
        green_bits = [0,0,0,0,0,1,1,1]
        blue_bits =  [0,0,0,0,0,0,0,1]

        search = []
        for i in range(8):
            index = 4 * red_bits[i] + 2 * green_bits[i] + blue_bits[i]
            search.append(index)

        self.assertChildSequence(mm.root, search,1)

    def test_build_octree(self):
        mm = makemap.T(open("test000.png","rb"))
        mm.build_octree()

        self.assertChildSequence(mm.root,[0] * 8, 50)
        self.assertChildSequence(mm.root,[7] * 8, 50)
        
    def assertChildSequence(self,node,list,n):
        if list == []:
            self.assertEqual(node.n_local_pixels,n)
            return

        self.assertNotEqual(node.children[list[0]], None, list)
        self.assertChildSequence(node.children[list[0]], list[1:],n)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

