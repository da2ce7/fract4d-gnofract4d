#!/usr/bin/env python

#unit tests for gradient/colormap editor window

import unittest
import copy
import math
import os
import sys

import gtk
import gettext

os.environ.setdefault('LANG', 'en')
gettext.install('gnofract4d')
sys.path.append("..")

from fract4d import gradient, fc, fractal
import colors
import gtkfractal

class Test(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        self.compiler.file_path.append("../formulas")
        
        self.f = gtkfractal.T(self.compiler,self)

        self.red = [1.0, 0.0, 0.0, 1.0]
        self.green = [0.0, 1.0, 0.0, 1.0]
        self.blue = [0.0, 0.0, 1.0, 1.0]

    def tearDown(self):
        pass
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):        
        c = colors.ColorDialog(None,self.f)
        self.assertNotEqual(c,None)
        self.assertFractalSegmentsEqualEditorSegments(c)

    def testChangeColor(self):
        c = colors.ColorDialog(None,self.f)
        c.gradarea.realize()
        
        # if no segment selected, this should have no effect
        c.selected_segment = -1
        c.color_changed(0.3,0.4,0.5,True)
        self.assertFractalSegmentsEqualEditorSegments(c)

        c.selected_segment = 0
        alpha_l = c.grad.segments[0].left_color[3]
        alpha_r = c.grad.segments[0].right_color[3]
        
        c.color_changed(0.3,0.4,0.5,True)
        c.color_changed(0.8,0.5,0.3,False)
        
        self.assertEqual(c.grad.segments[0].left_color,
                         [0.3, 0.4, 0.5, alpha_l])

        self.assertEqual(c.grad.segments[0].right_color,
                         [0.8, 0.5, 0.3, alpha_r])

    def testUpdateGradient(self):
        c = colors.ColorDialog(None,self.f)
        self.f.set_gradient(self.make_rgb_gradient())
        c.update_gradient()
        self.assertFractalSegmentsEqualEditorSegments(c)

    def make_rgb_gradient(self):
        g = gradient.Gradient()
        g.segments = [
           gradient.Segment(0.0, self.red, 0.333, self.red),
           gradient.Segment(0.333, self.green, 0.667, self.green),
           gradient.Segment(0.667, self.blue, 1.0, self.blue)]
        return g
        
    def testApply(self):
        c = colors.ColorDialog(None,self.f)
        c.grad.segments[0].left_color = new_color = [0.4, 0.7, 0.3, 1.0]
        self.assertNotEqual(self.f.get_gradient().segments[0].left_color, new_color)

        c.onApply()
        self.assertFractalSegmentsEqualEditorSegments(c)
        
    def assertFractalSegmentsEqualEditorSegments(self, editor):
        for (seg1,seg2) in zip(self.f.get_gradient().segments, editor.grad.segments):
	    k1 = seg1.__dict__.keys()
	    k1.sort()
	    k2 = seg2.__dict__.keys()
	    k2.sort()
	    self.assertEqual(k1,k2)
	    for k in k1:
		self.assertEqual(seg1.__dict__[k], seg2.__dict__[k])
                
        for i in xrange(len(self.f.solids)):
            self.assertEqual(self.f.solids[i], editor.solids[i])
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
