# GUI and backend for user settings

import ConfigParser
import os

import gtk
import gobject

class Preferences(ConfigParser.ConfigParser,gobject.GObject):
    # This class holds the preference data
    __gsignals__ = {
        'preferences-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ())
        }

    def __init__(self, file='~/.gnofract4d'):
        _defaults = {
            "compiler" : {
              "name" : "gcc",
              "options" : "-fPIC -DPIC -D_REENTRANT -O3 -shared -ffast-math"
            },
            "display" : {
              "width" : "640",
              "height" : "480",
              "antialias" : "1",
              "autodeepen" : "1"
            }
        }

        gobject.GObject.__init__(self) # MUST be called before threaded.init

        ConfigParser.ConfigParser.__init__(self)

        self.file = os.path.expanduser(file)
        self.read(self.file)

        # we don't use the normal ConfigParser default stuff because
        # we want sectionized defaults

        for (section,entries) in _defaults.items():
            if not self.has_section(section):
                self.add_section(section)
            for (key,val) in entries.items():
                if not self.has_option(section,key):
                    self.set(section,key,val)

    def set(self,section,key,val):
        if self.has_section(section) and \
           self.has_option(section,key) and \
           self.get(section,key) == val:
            return

        ConfigParser.ConfigParser.set(self,section,key,val)
        self.changed()

    def set_size(self,width,height):
        if self.getint("display","height") == height and \
           self.getint("display","width") == width:
            return
        
        ConfigParser.ConfigParser.set(self,"display","height",str(height))
        ConfigParser.ConfigParser.set(self,"display","width",str(width))
        self.changed()
        
    def changed(self):
        self.emit('preferences-changed')

    def save(self):
        self.write(open(self.file,"w"))
    
# explain our existence to GTK's object system
gobject.type_register(Preferences)

userPrefs = Preferences()
    
_prefs = None

def show_preferences(parent,f):
    global _prefs
    if not _prefs:
        _prefs = PrefsDialog(parent,f)
    _prefs.show_all()

class PrefsDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        global userPrefs
        gtk.Dialog.__init__(
            self,
            "Preferences",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f
        self.notebook = gtk.Notebook()
        self.vbox.add(self.notebook)
        self.prefs = userPrefs
        
        self.create_image_options_page()
        self.create_compiler_options_page()

        self.set_size_request(500,-1)
        self.connect('response',self.onResponse)

    def show_error(self,message):
        d = gtk.MessageDialog(self, gtk.DIALOG_MODAL,
                              gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                              message)
        d.run()
        d.destroy()

    def create_width_entry(self):
        entry = gtk.Entry()
        def set_entry(*args):
            entry.set_text(self.prefs.get("display","width"))

        def set_prefs(*args):
            height = self.f.height
            try:
                width = int(entry.get_text())
            except ValueError:
                gtk.idle_add(
                    self.show_error,
                    "Invalid value for width: '%s'. Must be an integer" % \
                    entry.get_text())
                return False
            
            if self.fix_ratio.get_active():
                height = int(width * float(height)/self.f.width)
            self.prefs.set_size(width, height)
            return False
        
        set_entry()
        self.prefs.connect('preferences-changed', set_entry)
        entry.connect('focus-out-event', set_prefs)
        return entry

    def create_height_entry(self):
        entry = gtk.Entry()
        def set_entry(*args):
            entry.set_text(self.prefs.get("display","height"))

        def set_prefs(*args):
            try:
                height = int(entry.get_text())
            except ValueError:
                gtk.idle_add(
                    self.show_error,
                    "Invalid value for height: '%s'. Must be an integer" % \
                    entry.get_text())
                return False
                
            width = self.f.width
            if self.fix_ratio.get_active():
                width = int(height * float(self.f.width)/self.f.height)
            self.prefs.set_size(width, height)
            return False
        
        set_entry()
        self.prefs.connect('preferences-changed', set_entry)
        entry.connect('focus-out-event', set_prefs)
        return entry

    def create_compiler_entry(self,propname):
        entry = gtk.Entry()
        def set_entry(*args):
            entry.set_text(self.prefs.get("compiler",propname))

        def set_prefs(*args):
            self.prefs.set("compiler",propname,entry.get_text())

        set_entry()
        self.prefs.connect('preferences-changed',set_entry)
        entry.connect('focus-out-event', set_prefs)
        return entry

    def create_compiler_options_page(self):
        table = gtk.Table(5,2,gtk.FALSE)
        self.notebook.append_page(table,gtk.Label("Compiler"))

        table.attach(gtk.Label("Compiler :"),0,1,0,1,0,0,2,2)
        entry = self.create_compiler_entry("name")
        table.attach(entry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        table.attach(gtk.Label("Compiler Options :"),0,1,1,2,0,0,2,2)
        entry = self.create_compiler_entry("options")
        table.attach(entry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)

    def create_auto_deepen_widget(self):
        widget = gtk.CheckButton("Auto Deepen")

        def set_widget(*args):
            widget.set_active(self.prefs.getboolean("display","autodeepen"))

        def set_prefs(*args):
            self.prefs.set("display","autodeepen",str(widget.get_active()))

        set_widget()
        self.prefs.connect('preferences-changed',set_widget)
        widget.connect('toggled',set_prefs)

        return widget

    def create_antialias_menu(self):
        optMenu = gtk.OptionMenu()
        menu = gtk.Menu()
        for item in ["None", "Fast", "Best"]:
            mi = gtk.MenuItem(item)
            menu.append(mi)
        optMenu.set_menu(menu)

        def set_widget(*args):
            optMenu.set_history(self.prefs.getint("display","antialias"))

        def set_prefs(*args):
            index = optMenu.get_history()
            if index != -1:
                self.prefs.set("display","antialias",str(index))

        set_widget()
        self.prefs.connect('preferences-changed',set_widget)
        optMenu.connect('changed',set_prefs)
        return optMenu
    
    def create_image_options_page(self):
        table = gtk.Table(5,2,gtk.FALSE)
        self.notebook.append_page(table,gtk.Label("Image"))

        table.attach(gtk.Label("Width :"),0,1,0,1,0,0,2,2)
        table.attach(gtk.Label("Height :"),0,1,1,2,0,0,2,2)

        wentry = self.create_width_entry()
        table.attach(wentry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        hentry = self.create_height_entry()
        table.attach(hentry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.fix_ratio = gtk.CheckButton("Maintain Aspect Ratio")
        table.attach(self.fix_ratio,0,2,2,3,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        self.fix_ratio.set_active(True)

        # auto deepening
        self.auto_deepen = self.create_auto_deepen_widget()
        table.attach(self.auto_deepen,0,2,3,4,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        # antialiasing
        table.attach(gtk.Label("Antialiasing : "),0,1,4,5,0,0,2,2)
        optMenu = self.create_antialias_menu()
        table.attach(optMenu,1,2,4,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
