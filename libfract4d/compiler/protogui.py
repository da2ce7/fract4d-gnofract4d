#!/usr/bin/env python

import sys
import os
import struct
import math

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
            if not self.skip_updates: self.image_changed(p1,p2,p3,p4)
        elif t == 2:
            if not self.skip_updates: self.progress_changed(float(p1))
        elif t == 3:
            if p1 == 0: # DONE
                print "done"
                self.running = False
            if not self.skip_updates: self.status_changed(p1)
        elif t == 4:
            # FIXME pixel_changed
            pass
        else:
            raise Exception("Unknown message from fractal thread")

class GuiFractal(Threaded):
    def __init__(self,comp):
        Threaded.__init__(self,comp)
        gtk.input_add(self.readfd, gtk.gdk.INPUT_READ, self.onData)

        self.width = 640
        self.height = 480
        self.image = fract4d.image_create(self.width,self.height)
        self.buf = fract4d.image_buffer(self.image)


        drawing_area = gtk.DrawingArea()
        drawing_area.add_events(gtk.gdk.BUTTON_RELEASE_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK)
        drawing_area.connect('button_release_event', self.onButtonRelease)
        drawing_area.connect('expose_event',self.onExpose)

        c = gtk.gdk.rgb_get_cmap()
        drawing_area.set_colormap(c)        
        drawing_area.set_size_request(self.width,self.height)

        self.widget = drawing_area
        self.compile()
        
    def draw_image(self,dummy):
        print "draw image"
        self.draw(self.image)
        return gtk.FALSE
    
    def image_changed(self,x1,y1,x2,y2):
        #print "img changed: %d %d %d %d" % (x1,y1,x2,y2)
        #gtk.idle_add(self.redraw_rect,x1,y1,x2-y1,y2-y1)
        self.redraw_rect(x1,y1,x2-x1,y2-y1)

    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        self.redraw_rect(r.x,r.y,r.width,r.height)

    def onButtonRelease(self,widget,event):
        if event.button == 1:
            zoom = 0.5
        elif event.button == 2:
            zoom = 1.0
            self.params[self.XZANGLE] += math.pi / 2
            self.params[self.YWANGLE] += math.pi / 2
        else:
            zoom = 2.0
            
        print "click (%d,%d)" % (event.x, event.y)
        self.interrupt()        
        self.recenter(event.x,event.y,zoom)
        self.draw_image(False)

    def recenter(self,x,y,zoom):
        dx = float(x - self.width/2)/self.width
        dy = float(y - self.height/2)/self.height
        print "%f, %f" % (dx,dy)
        self.relocate(dx,dy,zoom)
        
    def redraw_rect(self,x,y,w,h):
        gc = self.widget.get_style().white_gc
        
        # FIXME should draw smaller chunks but buf interface makes that tricky
        # FIXME remove hard-coded constants
        if self.widget.window:
            self.widget.window.draw_rgb_image(
                gc,
                0, 0,
                self.width,
                self.height,
                gtk.gdk.RGB_DITHER_NONE,
                self.buf,
                self.width*3)

class MainWindow:
    def __init__(self):
        global g_comp
        self.compiler = g_comp
        self.window = gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(640+8,480+40)
        self.window.set_title('Gnofract 4D')

        self.accelgroup = gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

        self.create_menu()
        self.create_fractal()

        self.window.show_all()

    def create_fractal(self):
        window = gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.f = GuiFractal(self.compiler)
        if len(sys.argv) > 1:
            self.load(sys.argv[1])

        self.f.draw_image(None)
        window.add_with_viewport(self.f.widget)
        self.vbox.pack_start(window)

    def create_menu(self):
        menu_items = (
            ('/_File', None, None, 0, '<Branch>' ),
            ('/File/_Open', '<control>O', self.open, 0, '<StockItem>', gtk.STOCK_OPEN),
            ('/File/_Save', '<control>S', self.save, 0, '<StockItem>', gtk.STOCK_SAVE),
            ('/File/Save _As', '<control><shift>S', self.saveas, 0, '<StockItem>', gtk.STOCK_SAVE_AS),
            ('/File/Save _Image', '<control>I', self.save_image, 0, ''),
            ('/File/sep1', None, None, 0, '<Separator>'),
            ('/File/_Quit', '<control>Q', self.quit, 0, '<StockItem>', gtk.STOCK_QUIT),   
            ('/_Edit', None, None, 0, '<Branch>'),
            ('/Edit/_Fractal Settings','<control>F',self.settings, 0, ''),
            ('/Edit/_Colors', '<control>L', self.colors, 0, ''),
            ('/Edit/_Preferences', None, self.preferences, 0, ''),
            ('/Edit/_Undo', '<control>Z', self.undo, 0, ''),
            ('/Edit/_Redo', '<control>Y', self.redo, 0, ''),
            ('/Edit/R_eset', 'Home', self.reset, 0, ''),
            ('/_Help', None, None, 0, '<Branch>'),
            ('/_Help/Contents', '<function>1', self.contents, 0, ''),
            ('/Help/_About', None, self.about, 0, ''),
            )
    
        item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>', self.accelgroup)
        item_factory.create_items(menu_items)

        menubar = item_factory.get_widget('<main>')

        self.vbox.pack_start(menubar, expand=gtk.FALSE)

    def save(self,action,widget):
        print "save"

    def saveas(self,action,widget):
        print "save as"
    def save_image(self,action,widget):
        print "save_image"
    def settings(self,action,widget):
        print "settings"
    def colors(self,action,widget):
        print "colors"
    def preferences(self,action,widget):
        print "prefs"
    def undo(self,action,widget):
        print "undo"
    def redo(self,action,widget):
        print "redo"
    def reset(self,action,widget):
        print "reset"
    def contents(self,action,widget):
        print "contents"

    def open(self,action,widget):
        fs = gtk.FileSelection("Open Formula File")
        result = fs.run()
        
        if result == gtk.RESPONSE_OK:
            self.load(fs.get_filename())
        fs.destroy()

    def load(self,file):
        self.f.loadFctFile(open(file))
        self.f.compile()
        
    def about(self,action,widget):
        print "about"

    def quit(self,action,widget=None):
        gtk.main_quit()

def main():
    mainWindow = MainWindow()
    gtk.main()
    
if __name__ == '__main__':
    main()
