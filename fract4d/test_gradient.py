#!/usr/bin/env python

import unittest
import sys
import math
import StringIO

import testbase

import gradient

from gradient import Blend, ColorMode

class Test(testbase.TestBase):
    def setUp(self):
        self.white = [1.0, 1.0, 1.0, 1.0]
        self.black = [0.0, 0.0, 0.0, 1.0]
        self.grey_33 = [1.0/3.0, 1.0/3.0, 1.0/3.0, 1.0]
        self.mid_grey = [0.5, 0.5, 0.5, 1.0]
        self.grey_66 = [2.0/3.0, 2.0/3.0, 2.0/3.0, 1.0]
        self.red = [1.0, 0.0, 0.0, 1.0]
        self.green = [0.0, 1.0, 0.0, 1.0]
        self.blue = [0.0, 0.0, 1.0, 1.0]
    
    def tearDown(self):
        pass

    def testLoad(self):
        g = gradient.Gradient()

        self.assertEqual(len(g.segments), 1)
        self.assertWellFormedGradient(g)

    def create_rgb_gradient(self):
        # make a simple gradient which goes from R -> G -> B
        g = gradient.Gradient()
        g.segments = [
           gradient.Segment(0.0, self.red, 0.333, self.red),
           gradient.Segment(0.333, self.green, 0.667, self.green),
           gradient.Segment(0.667, self.blue, 1.0, self.blue)]
        return g
    
    def testGetSegments(self):
        g = self.create_rgb_gradient()
        self.assertWellFormedGradient(g)
        self.assertEqual(g.get_segment_at(0.0), g.segments[0])
        self.assertEqual(g.get_segment_at(0.5), g.segments[1])
        self.assertEqual(g.get_segment_at(1.0), g.segments[2])

        self.assertEqual(g.get_segment_at(0.333), g.segments[0])
        self.assertEqual(g.get_segment_at(0.667), g.segments[1])
        
        self.assertRaises(IndexError, g.get_segment_at, -1.0)
        self.assertRaises(IndexError, g.get_segment_at, 2.0)

    def testGetSegmentIndexes(self):
        g = self.create_rgb_gradient()
        self.assertWellFormedGradient(g)
        self.assertEqual(g.get_index_at(0.0), 0)
        self.assertEqual(g.get_index_at(0.5), 1)
        self.assertEqual(g.get_index_at(1.0), 2)

        self.assertEqual(g.get_index_at(0.333), 0)
        self.assertEqual(g.get_index_at(0.667), 1)
        
        self.assertRaises(IndexError, g.get_index_at, -1.0)
        self.assertRaises(IndexError, g.get_index_at, 2.0)

    def testLinearSegment(self):
        seg = gradient.Segment(0.0, self.red, 0.333, self.red)
        self.assertEqual(seg.get_linear_factor(0.0, 0.5),0.0)
        self.assertEqual(seg.get_linear_factor(0.5, 0.5),0.5)
        self.assertEqual(seg.get_linear_factor(1.0, 0.5),1.0)

        # middle close to left end
        self.assertEqual(seg.get_linear_factor(0.0, 0.0),0.0)
        self.assertEqual(seg.get_linear_factor(0.5, 0.0),0.75)
        self.assertEqual(seg.get_linear_factor(1.0, 0.0),1.0)

        # middle close to right end
        self.assertEqual(seg.get_linear_factor(0.0, 1.0),0.0)
        self.assertEqual(seg.get_linear_factor(0.5, 1.0),0.25)
        self.assertEqual(seg.get_linear_factor(1.0, 1.0),0.5)

    def testVeryShortSegment(self):
        seg = gradient.Segment(0.0, self.black, 0.0, self.white)
        self.assertEqual(seg.get_color_at(0.0), self.mid_grey)
        self.assertEqual(seg.get_color_at(0.5), self.mid_grey)
        self.assertEqual(seg.get_color_at(1.0), self.mid_grey)
        
    def testGetFlatColors(self):
        g = self.create_rgb_gradient()
        self.assertWellFormedGradient(g)
        self.assertEqual(g.get_color_at(0.0), self.red)
        self.assertEqual(g.get_color_at(0.3), self.red)
        self.assertEqual(g.get_color_at(0.333), self.red)
        self.assertEqual(g.get_color_at(0.334), self.green)
        self.assertEqual(g.get_color_at(0.666), self.green)
        self.assertEqual(g.get_color_at(0.668), self.blue)
        self.assertEqual(g.get_color_at(1.0), self.blue)

    def checkGreyGradient(self, g, midpoint, oracle):
        self.assertWellFormedGradient(g)
        
        for i in xrange(256):
            x = i * 1.0/256.0
            fx = oracle(x,midpoint)

            self.failUnless(0.0 <= fx <= 1.0,
                            "dubious value %f for %x" % (fx,x))
            
            col = g.get_color_at(x)
            expected = [fx,fx,fx,1.0]
            self.assertNearlyEqual(col, expected,
                                   "%s != %s for %s (int %s)" % \
                                   (col, expected, x, i))

        # should be 0 at start, 1 at end
        self.assertEqual(g.get_color_at(0.0), [0.0, 0.0, 0.0, 1.0])
        self.assertEqual(g.get_color_at(1.0), [1.0, 1.0, 1.0, 1.0])
                
        # should be halfway at the midpoint
        self.assertEqual(g.get_color_at(midpoint), [0.5, 0.5, 0.5, 1.0])

    def testGreyGradient(self):
        g = gradient.Gradient()

        # linear, central midpoint
        g.segments[0].mid = 0.5
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

        # linear, off-center midpoint
        def predict_025_linear(x, dummy):
            if x <= 0.25:
                fx = 0.5 * x/0.25
            else:
                fx = 0.5 + 0.5 * (x-0.25)/0.75
            return fx

        g.segments[0].mid = 0.25
        self.checkGreyGradient(g, 0.25, predict_025_linear)
        
        # curved, central midpoint
        # (curved = linear if midpoint = 0.5)
        g.segments[0].bmode = Blend.CURVED
        g.segments[0].mid = 0.5
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

        # curved, non-central midpoint, sharper at the start
        def predict_025_curved(x, dummy):
            if x == 0.0:
                fx = 0.0
            else:
                fx = math.pow(x,math.log(0.5)/math.log(0.25))
            return fx

        g.segments[0].mid = 0.25
        self.checkGreyGradient(g, 0.25, predict_025_curved)

        # TODO: sine, sphere_increasing/decreasing
        
    def testAlphaChannel(self):
        g = gradient.Gradient()
        g.segments[0].left_color[3] = 0.5
        self.assertWellFormedGradient(g)
        for i in xrange(256):
            x = i * 1.0/256.0
            self.assertEqual(g.get_color_at(x), [x,x,x,0.5+x/2.0])

    def testSave(self):
        g = gradient.Gradient()
        s = StringIO.StringIO()
        g.save(s)
        self.assertEqual(
            s.getvalue(),
            '''GIMP Gradient
1
0.000000 0.500000 1.000000 0.000000 0.000000 0.000000 1.000000 1.000000 1.000000 1.000000 1.000000 0 0
''')

    def testLoadSimple(self):
        wood='''GIMP Gradient
Name: Wood 2
9
0.000000 0.069491 0.138982 1.000000 0.700000 0.400000 1.000000 0.944844 0.616991 0.289137 1.000000 3 0
0.138982 0.208472 0.277963 0.800000 0.522406 0.244813 1.000000 0.928860 0.592934 0.257008 1.000000 3 0
0.277963 0.347454 0.416945 0.820000 0.523444 0.226888 1.000000 0.922120 0.582791 0.243462 1.000000 3 0
0.416945 0.486436 0.555927 0.770000 0.486649 0.203299 1.000000 0.920000 0.579600 0.239200 1.000000 3 0
0.555927 0.609140 0.662354 0.780000 0.491400 0.202800 1.000000 0.903086 0.568944 0.234802 1.000000 4 0
0.662354 0.715568 0.768781 0.810000 0.510300 0.210600 1.000000 0.850329 0.535708 0.221086 1.000000 4 0
0.768781 0.821995 0.875209 0.760000 0.478800 0.197600 1.000000 0.708598 0.446417 0.184235 1.000000 4 0
0.875209 0.928422 0.981636 0.620000 0.390600 0.161200 1.000000 0.000000 0.000000 0.000000 1.000000 4 0
0.981636 0.991653 1.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 0.000000 4 0
'''
        g = gradient.Gradient()
        s = StringIO.StringIO(wood)
        g.load(s)

        s2 = StringIO.StringIO()
        g.save(s2)
        self.assertEqual(wood,s2.getvalue())

    def testAddSegment(self):
        # add some segments, ensure invariants hold and correct
        # outcome occurs.
        g = gradient.Gradient()

        # add a segment at left-hand end
        g.add(0.0)
        self.assertWellFormedGradient(g)
        self.assertEqual(len(g.segments),2)
        left = g.segments[0]
        right = g.segments[1]
        self.assertEqual(left.right_color, right.left_color)
        self.assertEqual(left.right_color,[0.5,0.5,0.5,1.0])
        self.assertEqual(right.right_color, [1.0, 1.0, 1.0, 1.0])
        self.assertEqual(left.mid, 0.25)
        self.assertEqual(left.right, 0.5)
        self.assertEqual(right.mid, 0.75)
        self.assertEqual(right.right, 1.0)

        # should have no effect on resulting pattern
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)
        
        # add another one
        g.add(0.0)
        self.assertWellFormedGradient(g)
        self.assertEqual(len(g.segments),3)
        left = g.segments[0]
        right = g.segments[1]
        self.assertEqual(left.right_color, right.left_color)
        self.assertEqual(left.right_color,[0.25,0.25,0.25,1.0])
        self.assertEqual(left.mid, 0.125)
        self.assertEqual(left.right, 0.25)
        self.assertEqual(right.mid, 0.375)
        self.assertEqual(right.right, 0.5)

        # still no effect
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

        # one more at the other end
        g.add(1.0)
        self.assertWellFormedGradient(g)
        self.assertEqual(len(g.segments),4)
        left = g.segments[2]
        right = g.segments[3]
        self.assertEqual(left.right_color, right.left_color)
        self.assertEqual(left.right_color,[0.75,0.75,0.75,1.0])
        self.assertEqual(left.mid, 0.625)
        self.assertEqual(left.right, 0.75)
        self.assertEqual(right.mid, 0.875)
        self.assertEqual(right.right, 1.0)

        # still no effect
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

    def three_segments(self):
        # set up 3 equal segments
        return [
            gradient.Segment(0,self.black, 1.0/3.0, self.grey_33),
            gradient.Segment(1.0/3.0,self.grey_33, 2.0/3.0, self.grey_66),
            gradient.Segment(2.0/3.0,self.grey_66, 1.0, self.white)]

    def testRemove(self):
        # test removal of segments
        g = gradient.Gradient()

        # shouldn't be able to remove last segment
        self.assertRaises(gradient.Error, g.remove, 0.0)

        g.segments = self.three_segments()
        self.assertWellFormedGradient(g)
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

        # remove middle one
        g.remove(0.5)

        self.assertEqual(len(g.segments),2)
        self.assertWellFormedGradient(g)
        self.assertEqual(g.segments[0].right, 0.5)

        # recreate and remove left one
        g.segments = self.three_segments()
        self.assertWellFormedGradient(g)
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

        g.remove(0.1)
        
        self.assertEqual(len(g.segments),2)
        self.assertWellFormedGradient(g)
        self.assertEqual(g.segments[0].right, 2.0/3.0)

        # recreate and remove right one
        g.segments = self.three_segments()
        self.assertWellFormedGradient(g)
        self.checkGreyGradient(g, 0.5, lambda x,mid : x)

        g.remove(0.9)
        
        self.assertEqual(len(g.segments),2)
        self.assertWellFormedGradient(g)
        self.assertEqual(g.segments[1].left, 1.0/3.0)
        
    def assertNearlyEqual(self,a,b,msg):
        # check that each element is within epsilon of expected value
        epsilon = 1.0e-12
        for (ra,rb) in zip(a,b):
            d = abs(ra-rb)
            self.failUnless(d < epsilon,msg)

    def assertWellFormedGradient(self, g):
        # check starts and sends at 0 and 1
        first_seg = g.segments[0]
        last_seg = g.segments[-1]
        self.assertEqual(first_seg.left, 0.0)
        self.assertEqual(last_seg.right, 1.0)

        # check segments line up and types are in range
        previous_seg = g.segments[0]
        for seg in g.segments[1:]:
            # check offsets
            self.failUnless(0.0 <= seg.left <= 1.0)
            self.failUnless(0.0 <= seg.right <= 1.0)
            self.failUnless(
                seg.left <= seg.mid <= seg.right,
                "midpoint %g not between endpoints %g,%g" % \
                (seg.mid, seg.left, seg.right))

            # check colors
            self.assertEquals(len(seg.left_color),4)
            self.assertEquals(len(seg.right_color),4)
            for x in seg.left_color + seg.right_color:
                self.failUnless(0.0 <= x <= 1.0)

            # check modes
            self.failUnless(Blend.LINEAR <= seg.bmode <= Blend.SPHERE_DECREASING)
            self.failUnless(ColorMode.RGB <= seg.cmode <= ColorMode.HSV_CW)

            # check offset chaining
            self.failUnless(seg.right > seg.left)
            self.assertEqual(seg.left, previous_seg.right)
            previous_seg = seg


def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
