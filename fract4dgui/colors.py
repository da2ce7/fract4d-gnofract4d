# GUI and backend for colormaps

import os
import sys

import gtk
import gobject

import dialog
import gtkfractal
import preferences

_color_model = None

def show_colors(parent,f):
    ColorDialog.show(parent,f)

def _get_model():
    global _color_model
    if not _color_model:
        _color_model = ColorModel()
    return _color_model

def maps():
    return _get_model().maps

class ColorModel:
    def __init__(self):
        self.maps = {}
        self.populate_file_list()
        
    def add_directory(self,dirname):
        if not os.path.isdir(dirname):
            return

        files = os.listdir(dirname)
        for f in files:
            absfile = os.path.join(dirname,f)
            (name,ext) = os.path.splitext(absfile)
            if ext.lower() == ".map":
                if self.maps.get(f):
                    continue # avoid duplicates
                self.maps[f] = absfile
                
    def populate_file_list(self):
        self.add_directory("maps")
        self.add_directory(
            os.path.join(sys.exec_prefix,"share/maps/gnofract4d"))
        
def stricmp(a,b):
    return cmp(a.lower(),b.lower())

class ColorDialog(dialog.T):
    RESPONSE_REFRESH = 2
    def __init__(self,main_window,f):
        global userPrefs
        dialog.T.__init__(
            self,
            _("Color Maps"),
            main_window.window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_REFRESH, ColorDialog.RESPONSE_REFRESH,
             gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
             gtk.STOCK_OK, gtk.RESPONSE_OK,
             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        #self.set_size_request(200,350)
        self.main_f = f
        self.f = f.copy_f()
        self.model = _get_model()
        maplist = self.create_map_file_list()

        hbox = gtk.HBox(False, 2)
        hbox.add(maplist)
        self.vbox.add(hbox)
        
        self.preview = gtkfractal.SubFract(main_window.compiler)
        self.preview.set_size(96,96)
        self.preview.set_fractal(self.f)
        self.update_preview()
        
        hbox.add(self.preview.widget)
        self.treeview.get_selection().unselect_all()

    def update_preview(self):
        self.draw_preview()

    def draw_preview(self):
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
        self.preview.draw_image(False,auto_deepen)

    def show(parent, f):
        dialog.T.reveal(ColorDialog,parent,f)

    show = staticmethod(show)

    def file_selection_changed(self,selection):
        (model,iter) = selection.get_selected()

        if iter == None:
            return
        
        mapfile = model.get_value(iter,0)
        self.f.set_cmap(self.model.maps[mapfile])
        self.update_preview()
        
    def create_map_file_list(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.map_list = gtk.ListStore(
            gobject.TYPE_STRING,
            )

        self.treeview = gtk.TreeView (self.map_list)
        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_('Color Map'), renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.unselect_all()
        selection.connect('changed',self.file_selection_changed)

        self.update_list()
        return sw

    def onApply(self):
        self.main_f.copy_colors(self.f)

    def onRefresh(self):
        self.f = self.main_f.copy_f()
        self.f.changed()
        self.update_preview()
        
    def update_list(self):
        self.map_list.clear()
        keys = self.model.maps.keys()
        keys.sort(stricmp)
        for k in keys:
            iter = self.map_list.append ()
            self.map_list.set (iter, 0, k)

    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        elif id == ColorDialog.RESPONSE_REFRESH:
            self.onRefresh()
        elif id == gtk.RESPONSE_APPLY:
            self.onApply()
        elif id == gtk.RESPONSE_OK:
            self.onApply()
            self.hide()
