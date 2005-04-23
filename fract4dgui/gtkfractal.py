#!/usr/bin/env python

# Subclass of fract4d.fractal.T which works with a GUI

import sys
import os
import struct
import math
import copy
import random

import gtk
import gobject

# so we can run without installing.
# FIXME is there a better way?
sys.path.append("..")

from fract4d import fractal,fract4dc,fracttypes
import fract4dguic

import utils

class T(gobject.GObject):
    __gsignals__ = {
        'parameters-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'iters-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT,)),
        'formula-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'status-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT,)),
        'progress-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
        'pointer-moved' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT,
                            gobject.TYPE_FLOAT, gobject.TYPE_FLOAT))
        }

    def __init__(self,comp,parent=None,width=640,height=480):
        gobject.GObject.__init__(self) # MUST be called before threaded.init

        (self.readfd,self.writefd) = os.pipe()
        self.nthreads = 1        

        self.parent = parent
        self.compiler = comp

        self.paint_mode = False
        
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

        self.site = fract4dc.fdsite_create(self.writefd)
        self.f = None
        self.try_init_fractal()
            
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

        c = utils.get_rgb_colormap()
        
        drawing_area.set_colormap(c)        
        drawing_area.set_size_request(self.width,self.height)

        self.widget = drawing_area

    def try_init_fractal(self):
        try:
            f = fractal.T(self.compiler,self.site)
            self.set_fractal(f)
            self.f.compile()
            return True
        except IOError, err:
            self.error(_("Can't load default fractal"), err)
            return False
            
    def update_formula(self):
        if self.f != None:
            self.f.dirtyFormula = True
        
    def freeze(self):
        self.frozen = True

    def thaw(self):
        if self.f == None:
            return False
        
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

    def set_formula(self, fname, formula):
        ok = True
        if self.f == None:
            ok = self.try_init_fractal()
        if ok:
            self.f.set_formula(fname, formula)
        
    def draw(self,image,width,height,nthreads):
        self.cmap = fract4dc.cmap_create_gradient(self.get_gradient().segments)
        (r,g,b,a) = self.f.solids[0]
        fract4dc.cmap_set_solid(self.cmap,0,r,g,b,a)
        (r,g,b,a) = self.f.solids[1]
        fract4dc.cmap_set_solid(self.cmap,1,r,g,b,a)

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
        try:
            fract4dc.async_calc(self.f.params,self.f.antialias,self.f.maxiter,
                                self.f.yflip,nthreads,
                                self.f.pfunc,self.cmap,
                                self.f.auto_deepen, self.f.periodicity,
                                image,self.site, self.f.clear_image)
        except MemoryError:
            pass
        
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

    def make_numeric_widget(
        self, table, i, name, part, param, order, formula, param_type):
    
        label = gtk.Label(self.param_display_name(name,param)+part)
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        if param.type == fracttypes.Int:
            fmt = "%d"
        else:
            fmt = "%.17f"

        widget = gtk.Entry()
        widget.set_activates_default(True)

        def set_entry(*args):
            new_value = fmt % self.f.get_initparam(order,param_type)
            if widget.get_text() != new_value:
                widget.set_text(new_value)

        def set_fractal(entry,event,f,order,param_type):
            try:
                gtk.idle_add(f.set_initparam,order,
                             entry.get_text(),param_type)
            except Exception, err:
                # FIXME: produces too many errors
                msg = "Invalid value '%s': must be a number" % \
                      entry.get_text()
                #gtk.idle_add(f.warn,msg)
            return False

        set_entry(self)

        widget.set_data("update_function", set_entry)

        widget.f = self
        widget.connect('focus-out-event',
                       set_fractal,self,order,param_type)

        label.set_mnemonic_widget(widget)
        return widget

    def make_bool_widget(
        self, name, param, order, formula, param_type):

        widget = gtk.CheckButton(self.param_display_name(name,param))

        def set_toggle(*args):
            is_set = self.f.get_initparam(order,param_type)
            widget.set_active(is_set)
            if widget.get_active() != is_set:
                widget.set_active(is_set)

        def set_fractal(entry,f,order,param_type):
            try:
                gtk.idle_add(f.set_initparam,order,
                             entry.get_active(),param_type)
            except Exception, err:
                msg = "error setting bool param: %s" % str(err)
                print msg
                gtk.idle_add(f.warn,msg)

            return False

        set_toggle(self)

        widget.set_data("update_function", set_toggle)
        widget.f = self
        widget.connect('toggled', set_fractal, self, order, param_type)
        return widget

    def make_color_widget(
        self, table, i, name, param, order, formula, param_type):

        label = gtk.Label(self.param_display_name(name,param))
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        def set_fractal(r, g, b, is_left):
            self.freeze()
            self.f.set_initparam(order, r, param_type)
            self.f.set_initparam(order+1, g, param_type)
            self.f.set_initparam(order+2, b, param_type)
            if self.thaw():
                self.changed()
                

        rgba = []
        for j in xrange(4):
            rgba.append(self.f.get_initparam(order+j,param_type))

        # do we need to keep this ref?
        color_button = utils.ColorButton(rgba, set_fractal, False)

        def set_selected_value(*args):
            rgba = []
            for j in xrange(4):
                rgba.append(self.f.get_initparam(order+j,param_type))
            color_button.set_color(rgba)
            
        set_selected_value()
        
        color_button.widget.set_data("update_function", set_selected_value)

        return color_button.widget

    def make_enumerated_widget(
        self, table, i, name, part, param, order, formula, param_type):

        label = gtk.Label(self.param_display_name(name,param))
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        widget = gtk.OptionMenu()
        menu = self.construct_enum_menu(param.enum)
        widget.set_menu(menu)

        def set_selected_value(*args):
            try:
                index = self.f.get_initparam(order,param_type)
            except ValueError, err:
                print err
                return

            widget.set_history(index)
            
        def set_fractal(entry,f,order,param_type):
            new_value = widget.get_history()
            f.set_initparam(order, new_value,param_type)
            
        set_selected_value(self)

        widget.set_data("update_function", set_selected_value)

        widget.f = self
        widget.connect('changed',
                       set_fractal,self,order,param_type)

        label.set_mnemonic_widget(widget)
        return widget

    def add_formula_setting(
        self,table,i,name,part,param,order,formula,param_type):
        
        if param.type == fracttypes.Int:
            if hasattr(param,"enum"):
                widget = self.make_enumerated_widget(
                    table, i,name,part,param,order,formula,param_type)
            else:
                widget = self.make_numeric_widget(
                    table, i,name,part,param,order,formula,param_type)
                
        elif param.type == fracttypes.Float or \
             param.type == fracttypes.Complex or \
             param.type == fracttypes.Hyper:

            widget = self.make_numeric_widget(
                table, i,name,part,param,order,formula,param_type)
        elif param.type == fracttypes.Bool:
            widget = self.make_bool_widget(
                name,param,order,formula,param_type)
        elif param.type == fracttypes.Color:
            widget = self.make_color_widget(
                table,i,name,param,order,formula,param_type)
        else:
            raise "Unsupported parameter type"

        table.attach(widget,1,2,i,i+1,gtk.EXPAND | gtk.FILL ,0,2,2)
            
    def construct_function_menu(self,param,formula):
        funclist = formula.symbols.available_param_functions(
            param.ret,param.args)
        funclist.sort()

        menu = gtk.Menu()
        for func in funclist:
            mi = gtk.MenuItem(func)
            menu.append(mi)

        return (menu,funclist)

    def construct_enum_menu(self,enum):
        menu = gtk.Menu()
        for val in enum.value:
            mi = gtk.MenuItem(val)
            menu.append(mi)

        return menu

    def set_nthreads(self, n):
        if self.nthreads != n:
            self.nthreads = n
            self.changed()
    
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

    def error(self,msg,err):
        if self.parent:
            self.parent.show_error_message(msg, err)
        else:
            print "Error: %s %s" % (msg,err)
        
    def warn(self,msg):
        if self.parent:
            self.parent.show_warning(msg)
        else:
            print "Warning: ", msg

    def set_saved(self,val):
        if self.f != None:
            self.f.saved = val
        
    def changed(self,clear_image=True):
        if self.f == None:
            return
        self.f.dirty=True
        self.f.clear_image = clear_image
        self.set_saved(False)
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
                #print "finding value of %s", name
                selected_func_name = self.f.get_func_value(name,formula)
                #print "selected", selected_func_name
                #print "name %s formula %s" % (name, formula)
                index = funclist.index(selected_func_name)
            except ValueError, err:
                # func.cname not in list
                #print "bad cname"
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
        label = gtk.Label("_Max Iterations :")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_use_underline(True)
        table.attach(label,0,1,i,i+1,0,0,2,2)

        widget = gtk.Entry()
        widget.set_activates_default(True)
        
        def set_entry(*args):
            widget.set_text("%d" % self.f.maxiter)

        def set_fractal(*args):
            try:
                i = int(widget.get_text())
                self.set_maxiter(i)
            except ValueError, err:
                msg = "Invalid value '%s': must be a number" % \
                      widget.get_text()
                gtk.idle_add(self.warn, msg)
                
            return False

        set_entry(self)

        self.connect('parameters-changed', set_entry)
        self.connect('iters-changed', set_entry)
        widget.connect('focus-out-event',set_fractal)

        label.set_mnemonic_widget(widget)
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
                elif param.type == fracttypes.Hyper:
                    suffixes = [" (re)", " (i)", " (j)", " (k)"]
                    for j in xrange(4):
                        self.add_formula_setting(
                            table,i+j,name,suffixes[j],
                            param,op[name]+j,formula,param_type)
                    i += 3
                elif param.type == fracttypes.Color:
                    self.add_formula_setting(
                        table,i,name,"",
                        param,op[name],formula,param_type)
                    i += 3
                elif param.type == fracttypes.Gradient:
                    # FIXME
                    pass
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

        try:
            self.width = new_width
            self.height = new_height

            fract4dc.image_resize(self.image, new_width, new_height)

            self.widget.set_size_request(new_width,new_height)

            gtk.idle_add(self.changed)
        except MemoryError, err:
            gtk.idle_add(self.warn,str(err))
            

        
    def reset(self):
        self.f.reset()
        self.changed()

    def loadFctFile(self,file):
        new_f = fractal.T(self.compiler,self.site)
        new_f.warn = self.warn
        new_f.loadFctFile(file)
        self.set_fractal(new_f)
        self.set_saved(True)

    def is_saved(self):
        if self.f == None:
            return True
        return self.f.saved
    
    def save_image(self,filename):
        fract4dguic.image_save(self.image,filename)
        
    def draw_image(self,aa,auto_deepen):
        if self.f == None:
            return
        self.interrupt()
        try:
            self.f.compile()
        except fracttypes.TranslationError, err:
            advice = _("\nCheck that your compiler settings and formula file are correct.")
            gtk.idle_add(self.error,
                         _("Error compiling fractal:"),
                         err.msg + advice)
            return
        
        self.f.antialias = aa
        self.f.auto_deepen = auto_deepen
        self.draw(self.image,self.width,self.height,self.nthreads)
        return gtk.FALSE

    def progress_changed(self,progress):
        self.emit('progress-changed',progress)
        
    def status_changed(self,status):
        self.emit('status-changed',status)
        
    def iters_changed(self,n):
        self.f.maxiter = n
        # don't emit a parameters-changed here to avoid deadlock
        self.emit('iters-changed',n)
        
    def image_changed(self,x1,y1,x2,y2):
        self.redraw_rect(x1,y1,x2-x1,y2-y1)

    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        self.redraw_rect(r.x,r.y,r.width,r.height)

    def onMotionNotify(self,widget,event):
        self.redraw_rect(0,0,self.width,self.height)
        (self.newx,self.newy) = (event.x, event.y)

        dummy = widget.window.get_pointer()

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

        (x,y) = self.float_coords(self.newx,self.newy)
        self.emit('pointer-moved', self.button, x, y)

    def onButtonPress(self,widget,event):
        self.x = event.x
        self.y = event.y
        self.newx = self.x
        self.newy = self.y
        self.button = event.button

    def set_paint_mode(self,isEnabled, colorsel):
        self.paint_mode = isEnabled
        self.paint_color_sel = colorsel
        
    def get_paint_color(self):
        color = self.paint_color_sel.get_current_color() 
        return (color.red/65535.0, color.green/65535.0, color.blue/65535.0)
    
    def onPaint(self,x,y):
        # obtain index
        index = fract4dc.image_get_color_index(self.image, x, y)
        
        # obtain a color
        (r,g,b) = self.get_paint_color()
        
        # update colormap
        g = self.f.get_gradient()
        i = g.get_index_at(index)
        if index > g.segments[i].mid:
            alpha = g.segments[i].right_color[3]
            g.segments[i].right_color = [r, g, b, alpha]
        else:
            alpha = g.segments[i].left_color[3]
            g.segments[i].left_color = [r, g, b, alpha]
            
        self.changed(False)

    def filterPaintModeRelease(self,event):
        if self.paint_mode:
            if event.button == 1:
                if self.x == self.newx or self.y == self.newy:
                    self.onPaint(self.newx, self.newy)
                    return True
        
        return False
    
    def onButtonRelease(self,widget,event):
        self.redraw_rect(0,0,self.width,self.height)
        if self.filterPaintModeRelease(event):
            return
        
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

            # with shift held, don't zoom
            if hasattr(event,"state") and event.state & gtk.gdk.SHIFT_MASK:
                zoom = 1.0
            self.recenter(x,y,zoom)
            
        elif event.button == 2:
            (x,y) = (event.x, event.y)
            zoom = 1.0
            self.recenter(x,y,zoom)
            if self.f.formula.is4D():
                self.flip_to_julia()
            
        else:
            (x,y) = (event.x, event.y)
            zoom = 2.0
            self.recenter(x,y,zoom)

        if self.thaw():
            self.changed()

    def float_coords(self,x,y):
        return ((x - self.width/2.0)/self.width,
                (y - self.height/2.0)/self.width)
    
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

        try:
            buf = fract4dc.image_buffer(self.image,x,y)
        except MemoryError, err:
            # suppress these errors
            return
        
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

    def get_func_name(self):
        if self.f == None:
            return _("No fractal loaded")
        return self.f.get_func_name()

    def get_saved(self):
        if self.f == None:
            return True
        return self.f.get_saved()

    def serialize(self):
        if self.f == None:
            return None
        return self.f.serialize()

class SubFract(T):
    def __init__(self,comp,width=640,height=480):
        T.__init__(self,comp,None,width,height)
        self.master = None
        
    def set_master(self,master):
        self.master = master
        
    def onButtonRelease(self,widget,event):
        self.master.set_fractal(self.copy_f())
        
# explain our existence to GTK's object system
gobject.type_register(T)
