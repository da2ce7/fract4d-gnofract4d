# whimsical feature to zoom in search of interesting items

import random
import operator

import gtk

_autozoom = None

def show_autozoom(parent,f):
    global _autozoom
    if not _autozoom:
        _autozoom = AutozoomDialog(parent,f)
    _autozoom.show_all()

class AutozoomDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        gtk.Dialog.__init__(
            self,
            "Gnofract4D Autozoom",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f

        self.table = gtk.Table(2,2)
        self.vbox.add(self.table)
        
        self.zoombutton = gtk.ToggleButton("Start Zooming")
        self.zoombutton.connect('toggled',self.onZoomToggle)
        f.connect('status-changed',self.onStatusChanged)

        self.table.attach(self.zoombutton,0,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.minsize = 1.0E-13 # FIXME, should calculate this better

        self.table.attach(gtk.Label("Min Size"),0,1,1,2,0,0,2,2)
        self.minsize_entry = gtk.Entry()

        def set_entry(*args):
            self.minsize_entry.set_text("%g" % self.minsize)

        def change_entry(*args):
            m = float(self.minsize_entry.get_text())
            if m != 0.0 and m != self.minsize:
                self.minsize = m
                set_entry()
            return False
        
        self.connect('focus-out-event',change_entry)
        set_entry()

        self.table.attach(self.minsize_entry,
                          1,2,1,2,
                          gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        self.connect('response',self.onResponse)
        
    def onZoomToggle(self,*args):
        if self.zoombutton.get_active():
            self.zoombutton.child.set_text("Stop Zooming")
            self.select_quadrant_and_zoom()
        else:
            self.zoombutton.child.set_text("Start Zooming")
            
    def select_quadrant_and_zoom(self,*args):
        (wby2,hby2) = (self.f.width/2,self.f.height/2)
        (w,h) = (self.f.width,self.f.height)
        regions = [ (0,   0,   wby2,hby2),# topleft
                    (wby2,0,   w,   hby2),# topright
                    (0,   hby2,wby2,h),   # botleft
                    (wby2,hby2,w,   h)]   # botright   

        counts = [self.f.count_colors(r) for r in regions]
        m = max(counts)
        i = counts.index(m)

        # some level of randomness
        j = random.randrange(0,4)
        if float(counts[j]) / counts[i] > 0.75:
            i = j
            
        #print "counts: %s max %d i %d" % (counts,m,i)
        
        # centers of each quadrant
        coords = [(1,1),(3,1),(1,3),(3,3)]

        (x,y) = coords[i]
        self.f.recenter(x * self.f.width/4, y * self.f.height/4, 0.75)
            
    def onStatusChanged(self,f,status_val):
        if status_val == 0:
            # done drawing current fractal.
            if self.zoombutton.get_active():
                if self.f.params[self.f.MAGNITUDE] > self.minsize:
                    self.select_quadrant_and_zoom()
                else:
                    self.zoombutton.set_active(False)
                
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.zoombutton.set_active(False)
            self.hide()
    
