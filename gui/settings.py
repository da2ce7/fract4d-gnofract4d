# GUI for modifying the fractal's settings

import gtk

import browser

_settings = None

def show_settings(parent,f):
    global _settings
    if not _settings:
        _settings = SettingsDialog(parent,f)
    _settings.show_all()
    #_settings.window.raise()

class SettingsDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        gtk.Dialog.__init__(
            self,
            "Fractal Settings",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f

        self.notebook = gtk.Notebook()
        self.vbox.add(self.notebook)

        self.create_formula_parameters_page()
        self.create_location_page()
        self.create_angle_page()

        self.connect('response',self.onResponse)

    def create_location_page(self):
        table = gtk.Table(5,2,gtk.FALSE)
        self.notebook.append_page(table,gtk.Label("Location"))
        self.create_param_entry(table,0,"X (Re) :", self.f.XCENTER)
        self.create_param_entry(table,1,"Y (Im) :", self.f.YCENTER)
        self.create_param_entry(table,2,"Z (Re) :", self.f.ZCENTER)
        self.create_param_entry(table,3,"W (Im) :", self.f.WCENTER)
        self.create_param_entry(table,4,"Size :", self.f.MAGNITUDE)

    def create_angle_page(self):
        table = gtk.Table(5,2,gtk.FALSE)
        self.notebook.append_page(table,gtk.Label("Angles"))
        self.create_param_entry(table,0,"XY :", self.f.XYANGLE)
        self.create_param_entry(table,1,"XZ :", self.f.XZANGLE)
        self.create_param_entry(table,2,"XW :", self.f.XWANGLE)
        self.create_param_entry(table,3,"YZ :", self.f.YZANGLE)
        self.create_param_entry(table,4,"YW :", self.f.YWANGLE)
        self.create_param_entry(table,5,"ZW :", self.f.ZWANGLE)

    def create_formula_parameters_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,gtk.FALSE)
        vbox.pack_start(table)
        
        self.table2 = None
        def add_current_formula_parameters(*args):
            if self.table2 != None:
                self.table2.destroy()
                
            self.table2 = self.f.populate_formula_settings()
            self.table2.show_all()
            vbox.pack_start(self.table2)

        add_current_formula_parameters()

        self.f.connect('parameters-changed',add_current_formula_parameters)
        
        self.notebook.append_page(vbox,gtk.Label("Formula"))

        table.attach(gtk.Label("Formula :"), 0,1,0,1,0,0,2,2)
        hbox = gtk.HBox(False,1)
        label = gtk.Label(self.f.funcName)

        def set_label(*args):
            label.set_text(self.f.funcName)
            
        self.f.connect('parameters-changed',set_label)
        
        hbox.pack_start(label)
        button = gtk.Button("Browse...")
        button.connect('clicked', self.show_browser)
        hbox.pack_start(button)
        table.attach(hbox, 1,2,0,1,gtk.EXPAND | gtk.FILL ,0,2,2)                
        
    def show_browser(self,*args):
        browser.show(self, self.f)
        
    def create_param_entry(self,table, row, text, param):
        label = gtk.Label(text)
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,row,row+1,0,0,2,2)
        
        entry = gtk.Entry()
        table.attach(entry,1,2,row,row+1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        def set_entry(f):
            entry.set_text("%.17f" % f.get_param(param))

        def set_fractal(*args):
            self.f.set_param(param,entry.get_text())
            return False
        
        set_entry(self.f)
        self.f.connect('parameters-changed', set_entry)
        entry.connect('focus-out-event', set_fractal)
        
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        else:
            print "unexpected response %d" % id
