#!/usr/bin/env python

import unittest
import copy

import gtkfractal
import gtk

from fract4d import fc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.load_formula_file("./gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")

class FakeEvent:
    def __init__(self,**kwds):
        self.__dict__.update(kwds)
        
class FctTest(unittest.TestCase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp
        self.window = gtk.Window()
        self.f = gtkfractal.T(self.compiler)
        self.window.add(self.f.widget)
        self.f.widget.realize()
                
    def tearDown(self):
        self.window.destroy()
        self.f= None
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            print "done"
            gtk.main_quit()

    def testCreate(self):
        # draw a default fractal
        self.f.connect('status-changed', self.quitloop)
        self.f.draw_image()
        self.wait()

    def testZoom(self):
        f = self.f
        
        # check click updates member vars
        f.onButtonPress(f.widget,FakeEvent(x=17,y=88))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(17,88,17,88))

        # click+release in middle of screen zooms but doesn't change params
        (xp,yp) = (f.width/2,f.height/2)
        f.onButtonPress(f.widget,FakeEvent(x=xp,y=yp))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(xp,yp,xp,yp))
        tparams = copy.copy(f.params)
        tparams[f.MAGNITUDE] /= 2.0

        f.onButtonRelease(f.widget,FakeEvent(button=1))
        self.assertEqual(f.params,tparams)

        # select entire screen & release should be a no-op
        f.onButtonPress(f.widget,FakeEvent(x=0,y=0))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(0,0,0,0))

        f.onMotionNotify(f.widget,FakeEvent(x=f.width-1,y=f.height-1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(0,0,f.width-1,f.height-1))

        f.onButtonRelease(f.widget,FakeEvent(button=1))
        self.assertEqual(f.params,tparams)

        # same if you do the corners the other way and get newy automatically
        (wm1,hm1) = (f.width-1,f.height-1)
        f.onButtonPress(f.widget,FakeEvent(x=wm1,y=hm1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(wm1,hm1,wm1,hm1))

        f.onMotionNotify(f.widget,FakeEvent(x=0,y=hm1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(wm1,hm1,0,0))

        f.onButtonRelease(f.widget,FakeEvent(button=1))
        self.assertEqual(f.params,tparams)
        
        
def suite():
    return unittest.makeSuite(FctTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
