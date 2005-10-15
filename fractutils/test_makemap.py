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
        self.assertRootGrey(mm)

        mm.insert_pixel(0,0,0) # 3rd color
        #print "\nBlue,Reddish,Black\n", mm.dump_octree(mm.root)
        
        self.assertEqual(mm.root.children[0].rgb, (0,0,0))
        self.assertRootGrey(mm)

        mm.insert_pixel(0,0,127) # split 0'th child pixel
        #print "\nBlue,Reddish,Black,DarkBlue\n", mm.dump_octree(mm.root)
        
        child0 = mm.root.children[0]
        
        self.assertEqual(child0.rgb, (127.0/2,127.0/2,127.0/2))
        self.assertEqual(child0.children[0].rgb,(0,0,0))
        self.assertEqual(child0.children[1].rgb,(0,0,127))

    def test_slightly_different(self):
        mm = makemap.T(open("test002.png","rb"))
        mm.build_octree()

        #print mm.dump_octree(mm.root)
        parent = mm.root.children[7].children[7].children[7].children[7].children[7].children[7].children[7]
        self.assertEqual(parent.children[7].n_local_pixels, 50)
        self.assertEqual(parent.children[6].n_local_pixels, 50)
        self.assertEqual(parent.error, 3 * 100 * 0.5**2)
        #self.assertEqual(mm.root.error, 5 * 50 * 127.5**2 + 1 * 50 * 126.5**2)
        
    def test_build_octree(self):
        # 50 black and 50 white pixels
        mm = makemap.T(open("test000.png","rb"))
        mm.build_octree()

        #print mm.dump_octree(mm.root)
        self.assertRootGrey(mm)
        self.assertEqual(mm.root.n_tree_pixels, 100)
        self.assertEqual(mm.root.error, 3 * 100 * 127.5**2)
        self.assertEqual(mm.root.children[0].n_local_pixels, 50)
        self.assertEqual(mm.root.children[7].n_local_pixels, 50)

    def test_larger_tree(self):
        mm = makemap.T(open("tattered.jpg","rb"))
        mm.build_octree()
        #print "\n",mm.dump_octree(mm.root)
        self.assertEqual(mm.root.n_tree_pixels, 40*30)

    def x_test_bigass_tree(self):
        mm = makemap.T(open("tattered2.jpg","rb"))
        mm.build_octree()
        #print "\n",mm.dump_octree(mm.root)
        self.assertEqual(mm.root.n_tree_pixels, 640*480)
        
    def test_reduction(self):
        mm = makemap.T(open("test001.png","rb"))
        # contains 50 black, 10 white, 15 d80000, 25 ff0000 pixels
        mm.build_octree()
        self.assertEqual(mm.root.n_tree_pixels, 100)

        self.assertEqual(4, mm.count_leaves(mm.root))

        targets =  mm.get_reduce_targets(mm.root,None)

        child = mm.root.children[4]
        grandchild = child.children[4]
        self.assertEqual(targets,[
            (mm.root.error, mm.root,None),
            (child.error, child, mm.root),
            (grandchild.error, grandchild, child)])
                         
        targets.sort()
        self.assertEqual(targets[0][1], grandchild)
        self.assertEqual(targets[1][1], child)
        self.assertEqual(targets[2][1], mm.root)
        
        print mm.dump_octree(mm.root)
        mm.reduce(3)
        print mm.dump_octree(mm.root)
        self.assertEqual(3, mm.count_leaves(mm.root))
                
    def assertRootGrey(self,mm):
        self.assertEqual(mm.root.rgb, (127.5,127.5,127.5))
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

