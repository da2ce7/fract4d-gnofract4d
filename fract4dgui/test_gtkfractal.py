#!/usr/bin/env python

import unittest
import copy
import math

import gtkfractal
import gtk

from fract4d import fc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.file_path.append("../formulas")

class FakeEvent:
    def __init__(self,**kwds):
        self.__dict__.update(kwds)

class CallCounter:
    def __init__(self):
        self.count = 0
    def cb(self,*args):
        self.count += 1

class Recurser:
    def __init__(self):
        self.count = 0
    def cb(self,f,*args):
        self.count += 1
        nv = f.params[f.MAGNITUDE]
        f.set_param(f.MAGNITUDE, nv * 2.0)
        
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
        self.f = None
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):
        # draw a default fractal
        self.f.connect('status-changed', self.quitloop)
        self.f.draw_image(0,1)
        self.wait()

    def testSignals(self):
        cc = CallCounter()
        self.f.connect('parameters-changed', cc.cb)
        self.assertEqual(cc.count,0)
        
        self.f.set_param(self.f.MAGNITUDE,0.7)
        self.assertEqual(cc.count,1)

        # set to the same value, no callback
        self.f.set_param(self.f.MAGNITUDE,0.7)
        self.assertEqual(cc.count,1)

        # maxiter
        self.f.set_maxiter(778)
        self.f.set_maxiter(778)
        self.assertEqual(cc.count,2)

        # size
        self.f.set_size(57,211)
        self.f.set_size(57,211)
        while cc.count < 3:
            gtk.main_iteration()
        

    def testLoad(self):
        self.f.loadFctFile(file("../testdata/test_bail.fct"))
        self.assertEqual(self.f.saved, True)
        
        self.testSignals()
        self.f.connect('status-changed', self.quitloop)
        self.f.draw_image(0,1)
        self.wait()        
                
    def disabled_testSignalsDontRecurse(self):
        # test no recurse, but doesn't work. Maybe I've misunderstood
        # signal recursion semantics?
        r = Recurser()
        self.f.connect('parameters-changed', r.cb)

        self.f.set_param(self.f.MAGNITUDE,0.7)
        self.assertEqual(r.count,1)

    def testParamSettings(self):
        self.f.set_formula("test.frm","test_func")
        self.f.set_outer("test.cfrm","flat")
        
        table = self.f.populate_formula_settings(0)

        children = table.get_children()
        list.reverse(children)

        names = [x.get_text() for x in children if isinstance(x,gtk.Label)]

        self.assertEqual(names[0],"Max Iterations :")
        self.assertEqual(names[1],"bailfunc")
        self.assertEqual(names[2],"bailout")
        self.assertEqual(names[3],"myfunc")
        
        table = self.f.populate_formula_settings(1)

        children = table.get_children()
        list.reverse(children)

        names = [x.get_text() for x in children if isinstance(x,gtk.Label)]

        self.assertEqual(
            names,
            [ "_density", "_offset", "_transfer", "ep", "i", "myfunc", "val",
              "val2 (re)", "val2 (i)", "val2 (j)", "val2 (k)"])

    def testIntParamSetting(self):
        self.f.set_formula("testx.frm","fn_with_intparam")

        table = self.f.populate_formula_settings(0)
        
    def testButton1(self):
        f = self.f

        # check click updates member vars
        f.onButtonPress(f.widget,FakeEvent(x=17,y=88,button=1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(17,88,17,88))

        # click+release in middle of screen zooms but doesn't change params
        (xp,yp) = (f.width/2,f.height/2)
        f.onButtonPress(f.widget,FakeEvent(x=xp,y=yp,button=1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(xp,yp,xp,yp))
        tparams = copy.copy(f.params())
        tparams[f.MAGNITUDE] /= 2.0

        f.onButtonRelease(f.widget,FakeEvent(button=1))
        self.assertEqual(f.params(),tparams)

        # select entire screen & release should be a no-op
        f.onButtonPress(f.widget,FakeEvent(x=0,y=0,button=1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(0,0,0,0))

        f.onMotionNotify(f.widget,FakeEvent(x=f.width-1,y=f.height-1,button=1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(0,0,f.width-1,f.height-1))

        f.onButtonRelease(f.widget,FakeEvent(button=1))
        self.assertEqual(f.params(),tparams)

        # same if you do the corners the other way and get newx automatically
        (wm1,hm1) = (f.width-1,f.height-1)
        f.onButtonPress(f.widget,FakeEvent(x=wm1,y=hm1,button=1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(wm1,hm1,wm1,hm1))

        f.onMotionNotify(f.widget,FakeEvent(x=0,y=hm1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(wm1,hm1,0,0))

        f.onButtonRelease(f.widget,FakeEvent(button=1))
        self.assertEqual(f.params(),tparams)

    def testCtrlButton1(self):
        f = self.f

        # ctrl + click on center should have no effect
        (xp,yp) = (f.width/2,f.height/2)
        f.onButtonPress(f.widget,FakeEvent(x=xp,y=yp,button=1))
        self.assertEqual((f.x,f.y,f.newx,f.newy),(xp,yp,xp,yp))
        tparams = copy.copy(f.params())

        f.onButtonRelease(f.widget,
                          FakeEvent(button=1,state=gtk.gdk.SHIFT_MASK))
        self.assertEqual(f.params(),tparams)

        
    def testZooms(self):
        self.doTestZooms(1)

    def testFlipYZooms(self):
        self.f.f.yflip = True
        self.doTestZooms(-1)
            
    def doTestZooms(self,dir):
        # select each quarter of the screen to zoom into - check
        # that resulting params look correct
        f = self.f
        tparams = copy.copy(f.params())
        
        # select the top LH quadrant zooms and recenters
        f.onButtonPress(f.widget,FakeEvent(x=0,y=0,button=1))
        f.onMotionNotify(f.widget,FakeEvent(x=f.width/2-1,y=f.height/2-1))
        f.onButtonRelease(f.widget,FakeEvent(button=1))

        tparams[f.XCENTER] -= tparams[f.MAGNITUDE]/4.0
        tparams[f.YCENTER] += dir * tparams[f.MAGNITUDE]/4.0*(float(f.height)/f.width)
        tparams[f.MAGNITUDE] /= 2.0

        self.assertEqual(f.params(),tparams)

        # top RH quadrant
        f.onButtonPress(f.widget,FakeEvent(x=f.width/2,y=0,button=1))
        f.onMotionNotify(f.widget,FakeEvent(x=f.width-1,y=f.height/2-1))
        f.onButtonRelease(f.widget,FakeEvent(button=1))

        tparams[f.XCENTER] += tparams[f.MAGNITUDE]/4.0
        tparams[f.YCENTER] += dir * tparams[f.MAGNITUDE]/4.0*(float(f.height)/f.width)
        tparams[f.MAGNITUDE] /= 2.0

        self.assertEqual(f.params(),tparams)

        # bottom LH quadrant
        f.onButtonPress(f.widget,FakeEvent(x=0,y=f.height/2,button=1))
        f.onMotionNotify(f.widget,FakeEvent(x=f.width/2-1,y=f.height-1))
        f.onButtonRelease(f.widget,FakeEvent(button=1))

        tparams[f.XCENTER] -= tparams[f.MAGNITUDE]/4.0
        tparams[f.YCENTER] -= dir * tparams[f.MAGNITUDE]/4.0*(float(f.height)/f.width)
        tparams[f.MAGNITUDE] /= 2.0

        self.assertEqual(f.params(),tparams)

        # bottom RH quadrant
        f.onButtonPress(f.widget,FakeEvent(x=f.width/2,y=f.height/2,button=1))
        f.onMotionNotify(f.widget,FakeEvent(x=f.width-1,y=f.height-1))
        f.onButtonRelease(f.widget,FakeEvent(button=1))

        tparams[f.XCENTER] += tparams[f.MAGNITUDE]/4.0
        tparams[f.YCENTER] -= dir * tparams[f.MAGNITUDE]/4.0*(float(f.height)/f.width)
        tparams[f.MAGNITUDE] /= 2.0

        self.assertEqual(f.params(),tparams)

    def testButton3(self):
        f = self.f
        tparams = copy.copy(f.params())

        # right click in center just zooms out
        evt = FakeEvent(button=3,x=f.width/2,y=f.height/2)
        f.onButtonRelease(f.widget,evt)
        tparams[f.MAGNITUDE] *= 2.0

        self.assertEqual(f.params(),tparams)

        # right click in top corner zooms + recenters
        evt = FakeEvent(button=3,x=0,y=0)
        f.onButtonRelease(f.widget,evt)
        tparams[f.XCENTER] -= tparams[f.MAGNITUDE]/2.0
        tparams[f.YCENTER] += tparams[f.MAGNITUDE]/2.0*(float(f.height)/f.width)
        tparams[f.MAGNITUDE] *= 2.0

        self.assertEqual(f.params(),tparams)

    def testButton2(self):
        f = self.f
        tparams = copy.copy(f.params())

        # middle click in center goes to Julia 
        evt = FakeEvent(button=2,x=f.width/2,y=f.height/2)
        f.onButtonRelease(f.widget,evt)
        tparams[f.XZANGLE] = math.pi/2
        tparams[f.YWANGLE] = math.pi/2
        
        self.assertEqual(f.params(),tparams)

        # middle click again goes back to Mandelbrot
        evt = FakeEvent(button=2,x=f.width/2,y=f.height/2)
        f.onButtonRelease(f.widget,evt)
        tparams[f.XZANGLE] = 0.0
        tparams[f.YWANGLE] = 0.0
        
        self.assertEqual(f.params(),tparams)

        # click off to one side changes center
        evt = FakeEvent(button=2,x=f.width,y=0)
        f.onButtonRelease(f.widget,evt)
        tparams[f.XZANGLE] = math.pi/2
        tparams[f.YWANGLE] = math.pi/2
        tparams[f.XCENTER] += tparams[f.MAGNITUDE]/2.0
        tparams[f.YCENTER] += tparams[f.MAGNITUDE]/2.0*(float(f.height)/f.width)
        
        self.assertNearlyEqual(f.params(),tparams)

        # click off to the other side changes xycenter
        evt = FakeEvent(button=2,x=0,y=f.height)
        f.onButtonRelease(f.widget,evt)
        tparams[f.XZANGLE] = 0.0
        tparams[f.YWANGLE] = 0.0
        tparams[f.ZCENTER] -= tparams[f.MAGNITUDE]/2.0
        tparams[f.WCENTER] -= tparams[f.MAGNITUDE]/2.0*(float(f.height)/f.width)
        
        self.assertNearlyEqual(f.params(),tparams)
        
    def testCopy(self):
        copy = self.f.copy_f()
        mag = self.f.get_param(self.f.MAGNITUDE)
        copy.set_param(copy.MAGNITUDE,176.3)
        self.assertEqual(mag,self.f.get_param(self.f.MAGNITUDE))
        self.assertNotEqual(mag,copy.get_param(copy.MAGNITUDE))
        
    def assertNearlyEqual(self,a,b):
        # check that each element is within epsilon of expected value
        epsilon = 1.0e-12
        for (ra,rb) in zip(a,b):
            d = abs(ra-rb)
            self.failUnless(d < epsilon,"%f != %f (by %f)" % (ra,rb,d))

def suite():
    return unittest.makeSuite(FctTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
