#!/usr/bin/env python

import sys
import gtk

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

f = fractal.Threaded(g_comp)
file = open(sys.argv[1])
f.loadFctFile(file)
f.compile()

image = fract4d.image_create(640,480)

f.draw(image)

buf = fract4d.image_buffer(image)

class MainWindow:
    def __init__(self):
        self.window = gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(640,400)
        self.window.set_title('Gnofract 4D')

        c = gtk.gdk.rgb_get_cmap()
        v = gtk.gdk.rgb_get_visual()
        
        drawing_area = gtk.DrawingArea()
        drawing_area.set_colormap(c)
        drawing_area.set_size_request(640,480)
        drawing_area.connect('expose_event',self.expose)
        drawing_area.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        
        self.window.add(drawing_area)

        self.window.show_all()

    def expose(self,widget,exposeEvent):
        global buf
        r = exposeEvent.area
        print "expose: widget %s x:%d y:%d w:%d h:%d" % (widget,r.x,r.y,r.width,r.height)

        gc = widget.get_style().white_gc

        # FIXME should draw smaller chunks but buf interface makes that tricky
        # FIXME remove hard-coded constants
        exposeEvent.window.draw_rgb_image(
            gc,
            0, 0,
            640,
            480,
            gtk.gdk.RGB_DITHER_NONE,
            buf,
            640*3)
         
    def quit(self,action,widget=None):
        gtk.main_quit()

def main():
    mainWindow = MainWindow()
    gtk.main()
    
if __name__ == '__main__':
    main()
