# GUI and backend for colormaps

import os

import gtk
import gobject

_colors = None

def show_colors(parent,f):
    global _colors
    if not _colors:
        _colors = ColorDialog(parent,f)
    _colors.show_all()

class ColorDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        global userPrefs
        gtk.Dialog.__init__(
            self,
            "Color Maps",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f

        sw = self.create_map_file_list()
        self.vbox.add(sw)
        self.connect('response',self.onResponse)

    def add_directory(self,dirname):
        if not os.path.isdir(dirname):
            return

        files = os.listdir(dirname)
        for f in files:
            absfile = os.path.join(dirname,f)
            (name,ext) = os.path.splitext(absfile)
            if ext.lower() == ".map":
                iter = self.map_list.append ()
                self.map_list.set (iter, 0, f)
                self.map_list.set (iter, 1, absfile)
                
    def populate_file_list(self):
        self.add_directory("../maps")

    def file_selection_changed(self,selection):
        (model,iter) = selection.get_selected()

        if iter == None:
            return
        
        fname = model.get_value(iter,1)
        self.f.set_cmap(fname)
    
    def create_map_file_list(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.map_list = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING
            )

        self.treeview = gtk.TreeView (self.map_list)
        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn ('Color Map', renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.connect('changed',self.file_selection_changed)

        self.populate_file_list()
        return sw

    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
