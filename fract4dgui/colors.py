# GUI and backend for colormaps

import os
import sys

import gtk
import gobject

import dialog

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
    def __init__(self,main_window,f):
        global userPrefs
        dialog.T.__init__(
            self,
            _("Color Maps"),
            main_window.window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.set_size_request(200,500)
        
        self.f = f
        self.model = _get_model()
        sw = self.create_map_file_list()

        self.vbox.add(sw)
        self.treeview.get_selection().unselect_all()

    def show(parent, f):
        dialog.T.reveal(ColorDialog,parent,f)

    show = staticmethod(show)

    def file_selection_changed(self,selection):
        (model,iter) = selection.get_selected()

        if iter == None:
            return
        
        mapfile = model.get_value(iter,0)
        self.f.set_cmap(self.model.maps[mapfile])
    
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
