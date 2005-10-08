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
        length = 200//2

        self.assertEqual(mm.adjust_dimension(min,length,7,0), False)
        self.assertEqual(min[0],0)

        self.assertEqual(mm.adjust_dimension(min,length,187,1), True)
        self.assertEqual(min[1],100)
        
    def test_which_child(self):
        mm = makemap.T(open("test000.png","rb"))

        min = [0,0,0]
        length = 200//2

        # g & b, not r
        self.assertEqual(mm.which_child(min,length,1,120,100), 3) 
        self.assertEqual(min,[0,100,100])

    def test_insert_pixel(self):
        mm = makemap.T(open("test000.png","rb"))

        mm.insert_pixel(0,0,255) # blue-only pixel
        #print "\nBlue\n", mm.dump_octree(mm.root)
        
        self.assertEqual(mm.root.n_local_pixels,1)
        self.assertEqual(mm.root.rgb,(0,0,255))
        self.assertEqual(mm.root.children, [None] * 8)

        mm.insert_pixel(128,7,1) # other color
        #print "\nBlue,Reddish\n", mm.dump_octree(mm.root)
        
        self.assertEqual(mm.root.children[4].rgb, (128,7,1))
        self.assertEqual(mm.root.children[1].rgb, (0,0,255))
        self.assertEqual(mm.root.rgb, None)        

        mm.insert_pixel(0,0,0) # 3rd color
        #print "\nBlue,Reddish,Black\n", mm.dump_octree(mm.root)
        
        self.assertEqual(mm.root.children[0].rgb, (0,0,0))
        self.assertEqual(mm.root.rgb, None)        

        mm.insert_pixel(0,0,127) # split 0'th child pixel
        #print "\nBlue,Reddish,Black,DarkBlue\n", mm.dump_octree(mm.root)
        
        child0 = mm.root.children[0]
        
        self.assertEqual(child0.rgb, None)
        self.assertEqual(child0.children[0].rgb,(0,0,0))
        self.assertEqual(child0.children[1].rgb,(0,0,127))
        
    def test_build_octree(self):
        # 50 black and 50 white pixels
        mm = makemap.T(open("test000.png","rb"))
        mm.build_octree()

        #print mm.dump_octree(mm.root)
        self.assertEqual(mm.root.rgb, None)
        self.assertEqual(mm.root.n_tree_pixels, 100)
        self.assertEqual(mm.root.children[0].n_local_pixels, 50)
        self.assertEqual(mm.root.children[7].n_local_pixels, 50)

    def test_larger_tree(self):
        mm = makemap.T(open("tattered.jpg","rb"))
        mm.build_octree()
        #print "\n",mm.dump_octree(mm.root)
        self.assertEqual(mm.root.n_tree_pixels, 40*30)

    def test_bigass_tree(self):
        mm = makemap.T(open("tattered2.jpg","rb"))
        mm.build_octree()
        #print "\n",mm.dump_octree(mm.root)
        self.assertEqual(mm.root.n_tree_pixels, 640*480)
        
    def test_reduction(self):
        mm = makemap.T(open("test001.png","rb"))
        # contains 50 black, 10 white, 15 d80000, 25 ff0000 pixels
        mm.build_octree()
        self.assertEqual(mm.root.n_tree_pixels, 100)
    
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

