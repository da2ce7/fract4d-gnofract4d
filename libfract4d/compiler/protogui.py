#!/usr/bin/env python

import sys
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

class GuiFractal(fractal.Threaded):
    def __init__(self,comp):
        fractal.Threaded.__init__(self,comp)
        gtk.input_add(self.readfd, gtk.gdk.INPUT_READ, self.onData)
        
        self.image = fract4d.image_create(640,480)
        self.buf = fract4d.image_buffer(self.image)

        c = gtk.gdk.rgb_get_cmap()        
        drawing_area = gtk.DrawingArea()
        drawing_area.add_events(gtk.gdk.BUTTON_RELEASE_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK)
        drawing_area.connect('button_release_event', self.onButtonRelease)
        drawing_area.connect('expose_event',self.onExpose)
        
        drawing_area.set_colormap(c)        
        drawing_area.set_size_request(640,480)

        self.widget = drawing_area
        self.compile()

        self.skip_updates = False
        self.draw(self.image)

    def interrupt(self):
        fract4d.interrupt(self.site)
        self.skip_updates = True
        
    def draw_image(self,dummy):
        print "draw image"
        self.skip_updates = False
        self.draw(self.image)
        return gtk.FALSE
    
    def image_changed(self,x1,y1,x2,y2):
        if not self.skip_updates:
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
        gtk.idle_add(self.draw_image,self)
        
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
        self.window.set_default_size(640,400)
        self.window.set_title('Gnofract 4D')

        self.f = GuiFractal(g_comp)
        self.window.add(self.f.widget)

        self.window.show_all()

         
    def quit(self,action,widget=None):
        gtk.main_quit()

def main():
    mainWindow = MainWindow()
    gtk.main()
    
if __name__ == '__main__':
    main()
