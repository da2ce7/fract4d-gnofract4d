# GUI for user settings

import gtk

_prefs = None

def show_preferences(parent,f):
    global _prefs
    if not _prefs:
        _prefs = PrefsDialog(parent,f)
    _prefs.show_all()

class PrefsDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        gtk.Dialog.__init__(
            self,
            "Preferences",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f
        self.notebook = gtk.Notebook()
        self.vbox.add(self.notebook)
        
        self.create_image_size_page()
        
        self.connect('response',self.onResponse)

    def create_width_entry(self):
        entry = gtk.Entry()
        def set_entry(f):
            entry.set_text("%d" % f.width)

        def set_fractal(*args):
            height = self.f.height
            width = int(entry.get_text())
            if self.fix_ratio.get_active():
                height = int(width * float(height)/self.f.width)
            self.f.set_size(width, height)

        set_entry(self.f)
        self.f.connect('parameters-changed', set_entry)
        entry.connect('focus-out-event', set_fractal)
        return entry

    def create_height_entry(self):
        entry = gtk.Entry()
        def set_entry(f):
            entry.set_text("%d" % f.height)

        def set_fractal(*args):
            height = int(entry.get_text())
            width = self.f.width
            if self.fix_ratio.get_active():
                width = int(height * float(self.f.width)/self.f.height)
            self.f.set_size(width, height)

        set_entry(self.f)
        self.f.connect('parameters-changed', set_entry)
        entry.connect('focus-out-event', set_fractal)
        return entry

    def create_image_size_page(self):
        table = gtk.Table(5,2,gtk.FALSE)
        self.notebook.append_page(table,gtk.Label("Image Size"))

        table.attach(gtk.Label("Width"),0,1,0,1,0,0,2,2)
        table.attach(gtk.Label("Height"),0,1,1,2,0,0,2,2)

        wentry = self.create_width_entry()
        table.attach(wentry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        hentry = self.create_height_entry()
        table.attach(hentry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.fix_ratio = gtk.CheckButton("Maintain Aspect Ratio")
        table.attach(self.fix_ratio,0,2,2,3,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        self.fix_ratio.set_active(True)
        
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
