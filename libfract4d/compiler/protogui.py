#!/usr/bin/env python

import sys
import os
import struct

import gtk
import gobject

import fractal
import fc

sys.path.append("build/lib.linux-i686-2.2") # FIXME
import fract4d

#gtk.gdk.threads_init()

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.load_formula_file("./gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")


#file = open(sys.argv[1])
#f.loadFctFile(file)

class Threaded(fractal.T):
    def __init__(self,comp):
        (r,w) = os.pipe()
        self.readfd = r
        s = fract4d.fdsite_create(w)
        fractal.T.__init__(self,comp,s)
        self.msgformat = "5i"
        self.msgsize = struct.calcsize(self.msgformat)

        self.name_of_msg = [
            "PARAMS",
            "IMAGE",
            "PROGRESS",
            "STATUS",
            "PIXEL"
            ]

        self.skip_updates = False

    def interrupt(self):
        print "interrupt"
        fract4d.interrupt(self.site)
        self.skip_updates = True

        n = 0
        # wait for stream from worker to flush
        while self.running:
            n += 1
            gtk.main_iteration(True)
        print "waited %d" % n
        
    def draw(self,image):
        print "drawing with %s" % self.pfunc
        self.cmap = fract4d.cmap_create(self.colorlist)
        
        fract4d.pf_init(self.pfunc,0.001,self.initparams)

        self.skip_updates = False
        self.running = True
        fract4d.async_calc(self.params,self.antialias,self.maxiter,1,
                           self.pfunc,self.cmap,1,image,self.site)

    def onData(self,fd,condition):
        #print "data!"
        bytes = os.read(fd,self.msgsize)
        if len(bytes) < self.msgsize:
            print "bad message"
            return

        (t,p1,p2,p3,p4) = struct.unpack("5i",bytes)
        m = self.name_of_msg[t] 
        #print "msg: %s %d %d %d %d" % (m,p1,p2,p3,p4)
        if t == 0:
            if not self.skip_updates: self.parameters_changed()
        elif t == 1:
            self.image_changed(p1,p2,p3,p4)
        elif t == 2:
            self.progress_changed(float(p1))
        elif t == 3:
            if p1 == 0: # DONE
                print "done"
                self.running = False
            self.status_changed(p1)
        elif t == 4:
            # FIXME pixel_changed
            pass
        else:
            raise Exception("Unknown message from fractal thread")

class GuiFractal(Threaded):
    def __init__(self,comp):
        Threaded.__init__(self,comp)
        gtk.input_add(self.readfd, gtk.gdk.INPUT_READ, self.onData)
        
        self.image = fract4d.image_create(640,480)
        self.buf = fract4d.image_buffer(self.image)


        drawing_area = gtk.DrawingArea()
        drawing_area.add_events(gtk.gdk.BUTTON_RELEASE_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK)
        drawing_area.connect('button_release_event', self.onButtonRelease)
        drawing_area.connect('expose_event',self.onExpose)

        c = gtk.gdk.rgb_get_cmap()
        drawing_area.set_colormap(c)        
        drawing_area.set_size_request(640,480)

        self.widget = drawing_area
        self.compile()
        
    def draw_image(self,dummy):
        print "draw image"
        self.draw(self.image)
        return gtk.FALSE
    
    def image_changed(self,x1,y1,x2,y2):
        #print "img changed: %d %d %d %d" % (x1,y1,x2,y2)
        self.redraw_rect(x1,y1,x2-x1,y2-y1)

    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        self.redraw_rect(r.x,r.y,r.width,r.height)

    def onButtonRelease(self,widget,event):
        print "button release"
        print "click (%d,%d)" % (event.x, event.y)
        self.interrupt()        
        self.params[self.XCENTER] += 0.3
        self.draw_image(False)
        #gtk.idle_add(self.draw_image,self)
        
    def redraw_rect(self,x,y,w,h):
        gc = self.widget.get_style().white_gc
        
        # FIXME should draw smaller chunks but buf interface makes that tricky
        # FIXME remove hard-coded constants
        if self.widget.window:
            self.widget.window.draw_rgb_image(
                gc,
                0, 0,
                640,
                480,
                gtk.gdk.RGB_DITHER_NONE,
                self.buf,
                640*3)

class MainWindow:
    def __init__(self):
        global g_comp
        self.window = gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(640,480)
        self.window.set_title('Gnofract 4D')

        self.f = GuiFractal(g_comp)
        if len(sys.argv) > 1:
            self.f.loadFctFile(open(sys.argv[1]))
            self.f.compile()

        self.f.draw_image(None)
        self.window.add(self.f.widget)

        self.window.show_all()

         
    def quit(self,action,widget=None):
        gtk.main_quit()

def main():
    mainWindow = MainWindow()
    gtk.main()
    
if __name__ == '__main__':
    main()
