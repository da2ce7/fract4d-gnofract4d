import os
import sys
import inspect

import gtk

def find_resource(name, local_dir, installed_dir):
    'try and find a file either locally or installed'
    local_name = os.path.join(local_dir,name)
    if os.path.exists(local_name):
        return local_name

    return os.path.join(sys.exec_prefix, installed_dir, name)

def find_in_path(exe):
    # find an executable along PATH env var
    pathstring = os.environ["PATH"]
    if pathstring == None or pathstring == "":
        return None
    paths = pathstring.split(":")
    for path in paths:
        full_path = os.path.join(path,exe)
        if os.path.exists(full_path):
            return full_path
    return None
    
def stack_trace():
    stack = inspect.stack()
    str = ""
    for frame in stack[1:]:
        (frame_obj, filename, line, funcname, context, context_index) = frame
        try:
            args = inspect.formatargvalues(*inspect.getargvalues(frame_obj))
        except Exception:
            args = "<unavailable>"
        
        frame_desc = "%s(%s)\t\t%s(%s)\n" % (filename, line, funcname, args)
        str += frame_desc
    return str
    
def get_rgb_colormap():
    # work around a difference between pygtk versions
    if hasattr(gtk.gdk,'rgb_get_colormap'):
        c = gtk.gdk.rgb_get_colormap()
    else:
        c = gtk.gdk.rgb_get_cmap()
    return c

def get_file_save_chooser(title, parent, patterns=[]):
    try:
        chooser = gtk.FileChooserDialog(
            title, parent, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        filter = gtk.FileFilter()
        for pattern in patterns:
            filter.add_pattern(pattern)

        chooser.set_filter(filter)
        
        return chooser
    except:
        return gtk.FileSelection(title)

def set_file_chooser_filename(chooser,name):
    try:
        if name:
            chooser.set_current_name(name)
    except:
        pass
    
def get_file_open_chooser(title, parent, patterns=[]):
    try:
        chooser = gtk.FileChooserDialog(
            title, parent, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        filter = gtk.FileFilter()
        for pattern in patterns:
            filter.add_pattern(pattern)

        chooser.set_filter(filter)

        return chooser
    except:
        return gtk.FileSelection(title)

def create_option_menu(items):
    try:
        widget = gtk.combo_box_new_text()
        for item in items:
            widget.append_text(item)
        
    except Exception, exn:
        print exn
        widget = gtk.OptionMenu()
        menu = gtk.Menu()
        for item in items:
            mi = gtk.MenuItem(item)
            menu.append(mi)
        widget.set_menu(menu)
        
    return widget

def add_menu_item(menu, item):
    try:
        menu.append_text(item)
    except:
        menu.get_menu().append(gtk.MenuItem(item))

def set_selected(menu, i):
    try:
        menu.set_active(i)
    except:
        menu.set_history(i)
        
def get_selected(menu):
    try:
        return menu.get_active()
    except:
        return res_menu.get_history()
        
def create_color(r,g,b):
    # multiply up to match range expected by gtk
    try:
        return gtk.gdk.color(r*65535,g*65535,b*65535)
    except:
        # old gtk doesn't have direct color constructor
        return gtk.gdk.color_parse("#%04X%04X%04X" % (r*65535,g*65535,b*65535))

def floatColorFrom256(rgba):
    return [ rgba[0]/255.0, rgba[1]/255.0, rgba[2]/255.0, rgba[3]/255.0]

def updateColor256FromFloat(r,g,b,color):
    return (int(r*255), int(g*255), int(b*255), color[3])

class ColorButton:
    def __init__(self,rgb, changed_cb, is_left):
        self.area = None
        self.set_color(rgb)
        self.changed_cb = changed_cb
        self.is_left = is_left
        try:
            self.widget = gtk.ColorButton(self.color)

            def color_set(widget):
                color = widget.get_color()
                self.color_changed(color)

            self.widget.connect('color-set', self.on_color_set)
        except:
            # This GTK is too old to support ColorButton directly, fake one
            self.widget = gtk.Button()
            self.area = gtk.DrawingArea()
            self.area.set_size_request(16,10)
            self.widget.add(self.area)
            self.area.connect('expose_event', self.on_expose_event)
            self.csel_dialog = gtk.ColorSelectionDialog(_("Select a Color"))

            self.widget.connect('clicked', self.run_colorsel)

    def on_color_set(self, widget):
	self.color_changed(widget.get_color())

    def set_color(self, rgb):
        self.color = create_color(rgb[0], rgb[1], rgb[2])
	
	try:
            self.widget.set_color(self.color)
	except:
            #print "sc", self.area, rgb
            if self.area:
                self.area_expose(
                    self.area,
                    0,0,
                    self.area.allocation.width,self.area.allocation.height)

    def on_expose_event(self, widget, event):
        r = event.area
        self.area_expose(widget, r.x, r.y, r.width, r.height)
        
    def area_expose(self, widget, x, y, w, h):
        if not widget.window:
            return
        gc = widget.window.new_gc(fill=gtk.gdk.SOLID)
        self.color = widget.get_colormap().alloc_color(
            self.color.red, self.color.green, self.color.blue)
        gc.set_foreground(self.color)
        widget.window.draw_rectangle(gc, True, x, y, w, h)

    def run_colorsel(self, widget):
        dlg = self.csel_dialog
        dlg.colorsel.set_current_color(self.color)
        result = dlg.run()
        if result == gtk.RESPONSE_OK:
            self.color = dlg.colorsel.get_current_color()
            self.color_changed(self.color)
        self.csel_dialog.hide()

    def set_sensitive(self,x):
        self.widget.set_sensitive(x)
        
    def color_changed(self,color):
        self.color = color     
        self.changed_cb(
            color.red/65535.0,
            color.green/65535.0,
            color.blue/65535.0,
            self.is_left)

        
