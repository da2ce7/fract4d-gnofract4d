#!/usr/bin/env python

# Subclass of fract4d.fractal.T which works with a GUI

import sys
import os
import struct
import math
import copy

import gtk
import gobject

# so we can run without installing.
# FIXME is there a better way?
sys.path.append("..")

from fract4d import fractal,fract4dc,fracttypes
import fract4dguic

import undo

class T(gobject.GObject):
    __gsignals__ = {
        'parameters-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'formula-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'status-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT,)),
        'progress-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),        
        }

    def __init__(self,comp,parent=None,width=640,height=480):
        gobject.GObject.__init__(self) # MUST be called before threaded.init

        (self.readfd,self.writefd) = os.pipe()
        self.nthreads = 1        

        self.parent = parent
        
        self.site = fract4dc.fdsite_create(self.writefd)
        f = fractal.T(comp,self.site)
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
        self.running = False
        self.frozen = False # if true, don't emit signals
        
        self.f = None
        self.set_fractal(f)
        
        gtk.input_add(self.readfd, gtk.gdk.INPUT_READ, self.onData)
        
        self.width = width
        self.height = height
        self.image = fract4dc.image_create(self.width,self.height)

        drawing_area = gtk.DrawingArea()
        drawing_area.add_events(gtk.gdk.BUTTON_RELEASE_MASK |
                                gtk.gdk.BUTTON1_MOTION_MASK |
                                gtk.gdk.POINTER_MOTION_HINT_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK |
                                gtk.gdk.KEY_PRESS_MASK |
                                gtk.gdk.KEY_RELEASE_MASK
                                )
        
        drawing_area.connect('motion_notify_event', self.onMotionNotify)
        drawing_area.connect('button_release_event', self.onButtonRelease)
        drawing_area.connect('button_press_event', self.onButtonPress)
        drawing_area.connect('expose_event',self.onExpose)

        c = self.get_rgb_colormap()
        
        drawing_area.set_colormap(c)        
        drawing_area.set_size_request(self.width,self.height)

        self.widget = drawing_area
        self.f.compile()

    def get_rgb_colormap(self):
        # work around a difference between pygtk versions
        if hasattr(gtk.gdk,'rgb_get_colormap'):
            c = gtk.gdk.rgb_get_colormap()
        else:
            c = gtk.gdk.rgb_get_cmap()
        return c
    
    def update_formula(self):
        self.f.dirtyFormula = True
        
    def freeze(self):
        self.frozen = True

    def thaw(self):
        self.frozen = False
        was_dirty = self.f.dirty
        self.f.clean()
        return was_dirty

    def interrupt(self):
        #print "interrupted %d" % self.running
        if self.skip_updates:
            #print "skip recursive interrupt"
            return
        
        self.skip_updates = True
        
        fract4dc.interrupt(self.site)

        n = 0
        # wait for stream from worker to flush
        while self.running:
            n += 1
            gtk.main_iteration(True)

        self.skip_updates = False

    def copy_f(self):
        return copy.copy(self.f)
    
    def draw(self,image,width,height,nthreads):
        self.cmap = fract4dc.cmap_create(self.colorlist)
        (r,g,b,a) = self.f.solids[0]
        fract4dc.cmap_set_solid(self.cmap,0,r,g,b,a)

        t = self.f.tolerance(width,height)
        if self.f.auto_tolerance:
            self.f.set_named_param("@epsilon",t,
                                   self.f.formula, self.f.initparams)

        initparams = self.all_params()

        try:
            fract4dc.pf_init(self.f.pfunc,t,initparams)
        except ValueError:
            print initparams
            raise
            
        self.running = True
        fract4dc.async_calc(self.f.params,self.f.antialias,self.f.maxiter,
                            self.f.yflip,nthreads,
                            self.f.pfunc,self.cmap,self.f.auto_deepen,
                            image,self.site)

    def onData(self,fd,condition):
        bytes = os.read(fd,self.msgsize)
        if len(bytes) < self.msgsize:
            print "bad message: %s" % list(bytes)
            return True

        (t,p1,p2,p3,p4) = struct.unpack("5i",bytes)
        m = self.name_of_msg[t] 
        #print "msg: %s %d %d %d %d" % (m,p1,p2,p3,p4)
        if t == 0:
            if not self.skip_updates: self.iters_changed(p1)
        elif t == 1:
            if not self.skip_updates: self.image_changed(p1,p2,p3,p4)
        elif t == 2:
            if not self.skip_updates: self.progress_changed(float(p1))
        elif t == 3:
            if p1 == 0: # DONE
                #print "stop running"
                self.running = False
            if not self.skip_updates: self.status_changed(p1)
        elif t == 4:
            # FIXME pixel_changed
            pass
        else:
            print "Unknown message from fractal thread; %s" % list(bytes)
            
        return True
    
    def __getattr__(self,name):
        return getattr(self.f,name)

    def params(self):
        return self.f.params
    
    def get_param(self,n):
        return self.f.get_param(n)
    
    def param_display_name(self,name,param):
        if hasattr(param,"title"):
            return param.title.value
        if name[:5] == "t__a_":
            return name[5:]
        return name
    
    def add_formula_setting(
        self,table,i,name,part,param,order,formula,param_type):
        
        label = gtk.Label(self.param_display_name(name,param)+part)
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        if param.type == fracttypes.Float or param.type == fracttypes.Complex:
            widget = gtk.Entry()
            widget.set_activates_default(True)
            
            def set_entry(*args):
                widget.set_text("%.17f" % self.f.get_initparam(order,param_type))
                    
            def set_fractal(entry,event,f,order,param_type):
                try:
                    f.set_initparam(order,entry.get_text(),param_type)
                except Exception, err:
                    msg = "Invalid value '%s': must be a number" %widget.get_text()
                    gtk.idle_add(self.warn,msg)
                return False
            
            set_entry(self)

            widget.update = set_entry
            widget.f = self
            widget.connect('focus-out-event',set_fractal,self,order,param_type)
        else:
            raise "Unsupported parameter type"

        table.attach(widget,1,2,i,i+1,0,0,2,2)

    def construct_function_menu(self,param,formula):
        funclist = formula.symbols.available_param_functions(
            param.ret,param.args)
        funclist.sort()

        menu = gtk.Menu()
        for func in funclist:
            mi = gtk.MenuItem(func)
            menu.append(mi)

        return (menu,funclist)

    def set_fractal(self,f):
        if f != self.f:
            if self.f:
                self.interrupt()
            self.f = f

            # take over fractal's changed function
            f.changed = self.changed
            f.formula_changed = self.formula_changed
            f.warn = self.warn
            self.formula_changed()
            self.changed()

    def warn(self,msg):
        if self.parent:
            self.parent.show_warning(msg)
        else:
            print "Warning: ", msg
            
    def changed(self):
        self.f.dirty = True
        self.f.saved = False
        if not self.frozen:
            self.emit('parameters-changed')

    def formula_changed(self):
        self.f.dirtyFormula = True
        #if not self.frozen:
        self.emit('formula-changed')
            
    def set_auto_deepen(self,deepen):
        if self.f.auto_deepen != deepen:
            self.f.auto_deepen = deepen
            self.changed()
            
    def set_antialias(self,aa_type):
        if self.f.antialias != aa_type:
            self.f.antialias = aa_type
            self.changed()
        
    def set_func(self,func,fname,formula):
        self.f.set_func(func,fname,formula)
        
    def add_formula_function(self,table,i,name,param,formula):
        label = gtk.Label(self.param_display_name(name,param))
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        widget = gtk.OptionMenu()
        (menu, funclist) = self.construct_function_menu(param,formula)
        widget.set_menu(menu)

        def set_selected_function():
            try:
                selected_func_name = self.f.get_func_value(name,formula)
                index = funclist.index(selected_func_name)
            except ValueError, err:
                # func.cname not in list
                print "bad cname"
                return
            
            widget.set_history(index)
            
        def set_fractal_function(om,f,param,formula):
            index = om.get_history()
            if index != -1:
                # this shouldn't be necessary but I got weird errors
                # trying to reuse the old funclist
                list = formula.symbols.available_param_functions(
                    param.ret,param.args)
                list.sort()

                fname = list[index]
                f.set_func(param,fname,formula)

        set_selected_function()

        widget.update = set_selected_function

        widget.connect('changed',set_fractal_function,self,param,formula)
        
        table.attach(widget,1,2,i,i+1,gtk.EXPAND | gtk.FILL,0,2,2)

    def create_maxiter_widget(self,table,i):
        label = gtk.Label("Max Iterations :")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        widget = gtk.Entry()
        widget.set_activates_default(True)
        
        def set_entry(*args):
            widget.set_text("%d" % self.maxiter)

        def set_fractal(*args):
            try:
                i = int(widget.get_text())
                self.set_maxiter(int(widget.get_text()))
            except ValueError, err:
                msg = "Invalid value '%s': must be a number" % widget.get_text()
                gtk.idle_add(self.warn, msg)
                
            return False
        
        set_entry(self)

        self.connect('parameters-changed', set_entry)
        widget.connect('focus-out-event',set_fractal)

        table.attach(widget,1,2,i,i+1,0,0,2,2)
        return i+1
        
    def populate_formula_settings(self, param_type):
        # create widget to fiddle with this fractal's settings
        if param_type == 0:
            formula = self.f.formula
        else:
            formula = self.f.cfuncs[param_type-1]
        
        table = gtk.Table(5,2,gtk.FALSE)
        i = 0
        if param_type == 0:
            i = self.create_maxiter_widget(table,i)
        params = formula.symbols.parameters()
        op = formula.symbols.order_of_params()

        keys = params.keys()
        keys.sort()
        for name in keys:
            param = params[name]
            if isinstance(param,fracttypes.Func):
                self.add_formula_function(table,i,name,param,formula)
            else:
                if param.type == fracttypes.Complex:
                    self.add_formula_setting(
                        table,i,name," (re)",param,op[name],formula,param_type)
                    self.add_formula_setting(
                        table,i+1,name, " (im)",param,op[name]+1,
                        formula, param_type)
                    i+= 1
                else:
                    self.add_formula_setting(
                        table,i,name,"",param,op[name], formula, param_type)
            i += 1
        return table

    def double_maxiter(self):
        self.set_maxiter(self.f.maxiter*2)
        
    def set_maxiter(self,new_iter):
        if self.f.maxiter != new_iter:
            self.f.maxiter = new_iter
            self.changed()
        
    def set_size(self, new_width, new_height):
        self.interrupt()
        if self.width == new_width and self.height == new_height :
            return
        self.width = new_width
        self.height = new_height
        fract4dc.image_resize(self.image,self.width,self.height)
        self.widget.set_size_request(self.width,self.height)
        self.changed()
        
    def reset(self):
        self.f.reset()
        self.changed()

    def loadFctFile(self,file):
        new_f = fractal.T(self.compiler,self.site)
        new_f.warn = self.warn
        new_f.loadFctFile(file)
        self.set_fractal(new_f)
        self.f.saved = True
        
    def save_image(self,filename):
        fract4dguic.image_save(self.image,filename)
        
    def draw_image(self,aa,auto_deepen):
        self.interrupt()
        self.f.compile()
        self.f.antialias = aa
        self.f.auto_deepen = auto_deepen
        self.draw(self.image,self.width,self.height,self.nthreads)
        return gtk.FALSE

    def progress_changed(self,progress):
        self.emit('progress-changed',progress)
        
    def status_changed(self,status):
        self.emit('status-changed',status)
        
    def iters_changed(self,n):
        self.maxiter = n
        # don't emit a parameters-changed here to avoid deadlock
        
    def image_changed(self,x1,y1,x2,y2):
        self.redraw_rect(x1,y1,x2-x1,y2-y1)

    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        self.redraw_rect(r.x,r.y,r.width,r.height)

    def onMotionNotify(self,widget,event):
        (self.newx,self.newy) = (event.x, event.y)

        dummy = widget.window.get_pointer()
        self.redraw_rect(0,0,self.width,self.height)

        dy = int(abs(self.newx - self.x) * float(self.height)/self.width)
        if(self.newy < self.y or (self.newy == self.y and self.newx < self.x)):
            dy = -dy
        self.newy = self.y + dy;

        widget.window.draw_rectangle(
            self.widget.get_style().white_gc,
            gtk.FALSE,
            int(min(self.x,self.newx)),
            int(min(self.y,self.newy)),
            int(abs(self.newx-self.x)),
            int(abs(self.newy-self.y)));

    def onButtonPress(self,widget,event):
        self.x = event.x
        self.y = event.y
        self.newx = self.x
        self.newy = self.y
        
    def onButtonRelease(self,widget,event):
        self.redraw_rect(0,0,self.width,self.height)
        self.freeze()
        if event.button == 1:
            if self.x == self.newx or self.y == self.newy:
                zoom=0.5
                x = self.x
                y = self.y
            else:
                zoom= (1+abs(self.x - self.newx))/float(self.width)
                x = 0.5 + (self.x + self.newx)/2.0;
                y = 0.5 + (self.y + self.newy)/2.0;
            self.recenter(x,y,zoom)
            
        elif event.button == 2:
            (x,y) = (event.x, event.y)
            zoom = 1.0
            self.recenter(x,y,zoom)
            self.flip_to_julia()
            
        else:
            (x,y) = (event.x, event.y)
            zoom = 2.0
            self.recenter(x,y,zoom)

        if self.thaw():
            self.changed()
        
    def recenter(self,x,y,zoom):
        dx = (x - self.width/2.0)/self.width
        dy = (y - self.height/2.0)/self.width                
        self.relocate(dx,dy,zoom)
        
    def redraw_rect(self,x,y,w,h):
        # check to see if part of the rect is out-of-bounds, and clip if so
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x+w > self.width:
            w = self.width-x
        if y+h > self.height:
            h = self.height-y

        if x >= self.width or y >= self.height or w < 1 or h < 1:
            # nothing to do
            return
        
        gc = self.widget.get_style().white_gc

        buf = fract4dc.image_buffer(self.image,x,y)
        if self.widget.window:
            self.widget.window.draw_rgb_image(
                gc,
                x, y,
                min(self.width-x,w),
                min(self.height-y,h),
                gtk.gdk.RGB_DITHER_NONE,
                buf,
                self.width*3)

    def count_colors(self,rect):
        # calculate the number of different colors which appear
        # in the subsection of the image bounded by the rectangle
        (xstart,ystart,xend,yend) = rect
        buf = fract4dc.image_buffer(self.image,0,0)
        colors = {}
        for y in xrange(ystart,yend):
            for x in xrange(xstart,xend):
                offset = (y*self.width+x)*3
                col = buf[offset:offset+3]
                colors[col] = 1 + colors.get(col,0)
        return len(colors)

class SubFract(T):
    def __init__(self,comp,width=640,height=480):
        T.__init__(self,comp,width,height)
        self.master = None
        
    def set_master(self,master):
        self.master = master
        
    def onButtonRelease(self,widget,event):
        self.master.set_fractal(self.copy_f())

# explain our existence to GTK's object system
gobject.type_register(T)