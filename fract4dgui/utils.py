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

def get_file_save_chooser(title, parent):
    try:
        return gtk.FileChooserDialog(
            title, parent, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    except:
        return gtk.FileSelection(title)

def get_file_open_chooser(title, parent):
    try:
        return gtk.FileChooserDialog(
            title, parent, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    except:
        return gtk.FileSelection(title)

def create_option_menu(items, cb):
    try:
        widget = gtk.combo_box_new_text()
        for item in items:
            widget.append_text(item)
        
    except:
        widget = gtk.OptionMenu()
        menu = gtk.Menu()
        for item in items:
            mi = gtk.MenuItem(val)
            menu.append(mi)
        widget.set_menu(menu)
        
    return widget

def create_color(r,g,b):
    try:
        return gtk.gdk.color(r*256,g*256,b*256)
    except:
        return gtk.gdk.color_parse("#%4x%4x%4x" % (r*256,g*256,b*256))


class ColorButton:
    def __init__(self,rgb, changed_cb, *args):
        color = create_color(rgb[0], rgb[0], rgb[0])
        self.changed_cb = changed_cb
        self.cb_args = args
        try:
            self.widget = gtk.ColorButton(color)

            def color_set(widget):
                color = widget.get_color()
                self.color_changed(color)
                
            self.widget.connect('color-set', self.color_changed)
        except:
            # This GTK is too old to support ColorButton directly, fake one
            self.widget = gtk.Button("Color") # FIXME use drawable widget

            self.csel_dialog = gtk.ColorSelectionDialog(_("Select a Color"))
            self.csel_dialog.colorsel.set_current_color(color)

            self.widget.connect('clicked', self.run_colorsel)

    def run_colorsel(self, widget):
        dlg = self.csel_dialog
        result = dlg.run()
        if result == gtk.RESPONSE_OK:
            color = dlg.colorsel.get_current_color()
            self.color_changed(color)
        self.csel_dialog.hide()
        
    def color_changed(self,color):
        self.changed_cb(
            color.red/65535.0,
            color.green/65535.0,
            color.blue/65535.0,
            self.cb_args)

        
