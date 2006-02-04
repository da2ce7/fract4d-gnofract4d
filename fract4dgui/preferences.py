# GUI and backend for user settings

import ConfigParser
import os
import sys

import gtk
import gobject

import dialog
import utils

import fract4dguic

def _get_default_mailer():
    try:
        mailer = fract4dguic.get_gconf_string("/desktop/gnome/url-handlers/mailto/command")
    except:
        # oh well, something went wrong
        mailer = "evolution %s"
    return mailer

def _get_default_browser():
    try:
        browser = fract4dguic.get_gconf_string("/desktop/gnome/url-handlers/http/command")
    except:
        # oh well, something went wrong
        browser = "mozilla %s"
    return browser

class Preferences(ConfigParser.ConfigParser,gobject.GObject):
    # This class holds the preference data
    __gsignals__ = {
        'preferences-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'image-preferences-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        
        }

    def __init__(self, file='~/.gnofract4d'):
        _defaults = {
            "compiler" : {
              "name" : "gcc",
              "options" : "-fPIC -DPIC -D_REENTRANT -O2 -shared -ffast-math"
            },
            "display" : {
              "width" : "640",
              "height" : "480",
              "antialias" : "1",
              "autodeepen" : "1"
            },
            "helpers" : {
              "editor" : "emacs",
              "mailer" : _get_default_mailer(),
              "browser" : _get_default_browser()
            },
            "general" : {
              "threads" : "1"
            },
            "user_info" : {
              "name" : "",
              "flickr_token" : "",
              "nsid" : ""
            },
            "blogs" : {
            },
            "formula_path" : {
              "0" : "formulas",
              "1" : os.path.join(sys.exec_prefix, "share/formulas/gnofract4d"),
              "2" : os.path.expandvars("${HOME}/formulas")
            },
            "map_path" : {
              "0" : "maps",
              "1" : os.path.join(sys.exec_prefix, "share/maps/gnofract4d"),
              "2" : os.path.expandvars("${HOME}/maps")
            },
            "recent_files" : {
            },
            "ignored" : {
            }
        }

        self.image_changed_sections = {
            "display" : True,
            "compiler" : True
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
        self.changed(section)

    def set_size(self,width,height):
        if self.getint("display","height") == height and \
           self.getint("display","width") == width:
            return
        
        ConfigParser.ConfigParser.set(self,"display","height",str(height))
        ConfigParser.ConfigParser.set(self,"display","width",str(width))
        self.changed("display")

    def get_list(self, name):
        i = 0
        list = []
        while(True):
            try:
                key = "%d" % i
                val = self.get(name,key)
                list.append(val)
                i += 1
            except ConfigParser.NoOptionError:
                return list

    def remove_all_in_list_section(self,name):
        i = 0
        items_left = True
        while items_left:            
            items_left = self.remove_option(name,"%d" % i)
            i += 1
        
    def set_list(self, name, list):
        self.remove_all_in_list_section(name)

        i = 0        
        for item in list:
            ConfigParser.ConfigParser.set(self, name,"%d" % i, item)
            i += 1

        self.changed("name")

    def update_list(self,name,new_entry,maxsize):
        list = self.get_list(name)
        if list.count(new_entry) == 0:
            list.insert(0,new_entry)
            list = list[:maxsize]
            self.set_list(name,list)

        return list
    
    def changed(self, section):
        self.emit('preferences-changed')
        if self.image_changed_sections.get(section, False):
            self.emit('image-preferences-changed')
            
    def save(self):
        self.write(open(self.file,"w"))
    
# explain our existence to GTK's object system
gobject.type_register(Preferences)

userPrefs = Preferences()
    
def show_preferences(parent,f):
    PrefsDialog.show(parent,f)
    
class PrefsDialog(dialog.T):
    def __init__(self,main_window,f):
        global userPrefs
        dialog.T.__init__(
            self,
            _("Gnofract 4D Preferences"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.dirchooser = utils.get_directory_chooser(
            _("Select a Formula Directory"),
            main_window)
        
        self.set_default_response(gtk.RESPONSE_CLOSE)
        self.f = f
        self.notebook = gtk.Notebook()
        self.vbox.add(self.notebook)
        self.prefs = userPrefs
        self.tips = gtk.Tooltips()
        self.create_image_options_page()
        self.create_compiler_options_page()
        self.create_general_page()
        self.create_helper_options_page()
        self.create_flickr_page()
        
        self.set_size_request(500,-1)

    def show(parent, f):
        dialog.T.reveal(PrefsDialog, True, parent, None, f)

    show = staticmethod(show)

    def show_error(self,message):
        d = gtk.MessageDialog(self, gtk.DIALOG_MODAL,
                              gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                              message)
        d.run()
        d.destroy()

    def create_width_entry(self):
        entry = gtk.Entry()
        self.tips.set_tip(entry,"The image's width in pixels")
        entry.set_activates_default(True)
        
        def set_entry(*args):
            entry.set_text(self.prefs.get("display","width"))

        def set_prefs(*args):
            try:
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

                utils.idle_add(self.prefs.set_size,width, height)
            except Exception, exn:
                print exn
            return False
    
        set_entry()
        self.prefs.connect('preferences-changed', set_entry)
        entry.connect('focus-out-event', set_prefs)
        return entry

    def create_height_entry(self):
        entry = gtk.Entry()
        self.tips.set_tip(entry,"The image's height in pixels")
        entry.set_activates_default(True)
        
        def set_entry(*args):
            entry.set_text(self.prefs.get("display","height"))

        def set_prefs(*args):
            try:
                try:
                    height = int(entry.get_text())
                except ValueError:
                    utils.idle_add(
                        self.show_error,
                        "Invalid value for height: '%s'. Must be an integer" % \
                        entry.get_text())
                    return False

                width = self.f.width
                if self.fix_ratio.get_active():
                    width = int(height * float(self.f.width)/self.f.height)
                self.prefs.set_size(width, height)
            except Exception, exn:
                print exn
            return False
        
        set_entry()
        self.prefs.connect('preferences-changed', set_entry)
        entry.connect('focus-out-event', set_prefs)
        return entry

    def create_compiler_entry(self,propname):
        return self.create_option_entry("compiler",propname)
    
    def create_option_entry(self,section,propname):
        entry = gtk.Entry()
        entry.set_activates_default(True)
        
        def set_entry(*args):
            entry.set_text(self.prefs.get(section,propname))

        def set_prefs(*args):
            try:
                self.prefs.set(section,propname,entry.get_text())
            except Exception, err:
                print err
            return False
        
        set_entry()
        self.prefs.connect('preferences-changed',set_entry)
        entry.connect('focus-out-event', set_prefs)
        return entry

    def create_general_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label(_("_General"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)

        entry = self.create_option_entry("general","threads")
        self.tips.set_tip(entry,_("How many threads to use for calculations"))
        table.attach(entry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        name_label = gtk.Label(_("_Number of threads :"))
        name_label.set_use_underline(True)
        name_label.set_mnemonic_widget(entry)
        table.attach(name_label,0,1,0,1,0,0,2,2)

        #entry = self.create_option_entry("user_info","name")
        #self.tips.set_tip(
        #    entry,_("This text is saved in each image and parameter file you create"))
        #
        #table.attach(entry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        #
        #name_label = gtk.Label(_("_User Info :"))
        #name_label.set_use_underline(True)
        #name_label.set_mnemonic_widget(entry)
        #table.attach(name_label,0,1,1,2,0,0,2,2)

    def create_directory_list(self, section_name):
        self.path_list = gtk.ListStore(
            gobject.TYPE_STRING)
        
        path_treeview = gtk.TreeView (self.path_list)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_('_Directory'), renderer, text=0)
        path_treeview.append_column (column)
        path_treeview.set_headers_visible(False)
        
        paths = self.prefs.get_list(section_name)
        for path in paths:
            iter = self.path_list.append()
            self.path_list.set(iter,0,path)

        return path_treeview 

    def update_prefs(self,name, model):
        list = []

        def append_func(m,path,iter,dummy):
            list.append(model.get_value(iter,0))
        
        model.foreach(append_func,None)

        self.prefs.set_list(name,list)
        
    def browse_for_dir(self, widget, name, pathlist):
        self.dirchooser.show_all()
        result = self.dirchooser.run()
        if result == gtk.RESPONSE_OK:
            path = self.dirchooser.get_filename()

            model = pathlist.get_model() 
            iter = model.append()
            
            model.set(iter,0,path)
            self.update_prefs(name, model)
            
        self.dirchooser.hide()

    def remove_dir(self, widget, name, pathlist):
        select = pathlist.get_selection()
        (model, iter) = select.get_selected()

        if iter:
            model.remove(iter)
            self.update_prefs(name, model)
            
    def create_compiler_options_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label(_("_Compiler"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)
                        
        entry = self.create_compiler_entry("name")
        self.tips.set_tip(entry,_("The C compiler to use"))
        table.attach(entry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        name_label = gtk.Label(_("Compi_ler :"))
        name_label.set_use_underline(True)
        name_label.set_mnemonic_widget(entry)
        table.attach(name_label,0,1,0,1,0,0,2,2)
        
        entry = self.create_compiler_entry("options")
        self.tips.set_tip(entry, _("Options to pass to the C compiler"))
        table.attach(entry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        flags_label = gtk.Label(_("Compiler _Flags :"))
        flags_label.set_use_underline(True)
        table.attach(flags_label,0,1,1,2,0,0,2,2)
        flags_label.set_mnemonic_widget(entry)

        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        form_path_section = "formula_path"

        pathlist = self.create_directory_list(form_path_section)
        self.tips.set_tip(pathlist, _("Directories to search for formulas"))

        sw.add(pathlist)

        table.attach(sw,1,2,2,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        pathlist_label = gtk.Label(_("Formula Search _Path :"))
        pathlist_label.set_use_underline(True)
        table.attach(pathlist_label,0,1,2,3,0,0,2,2)
        pathlist_label.set_mnemonic_widget(pathlist)

        add_button = gtk.Button(None,gtk.STOCK_ADD)
        add_button.connect('clicked', self.browse_for_dir, form_path_section, pathlist)
        table.attach(add_button,0,1,3,4,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        remove_button = gtk.Button(None, gtk.STOCK_REMOVE)
        remove_button.connect('clicked', self.remove_dir, form_path_section, pathlist)
        table.attach(remove_button,0,1,4,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        
    def create_helper_options_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label(_("_Helpers"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)
                        
        entry = self.create_option_entry("helpers","editor")
        self.tips.set_tip(entry,_("The text editor to use for changing formulas"))
        table.attach(entry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        name_label = gtk.Label("_Editor :")
        name_label.set_use_underline(True)
        name_label.set_mnemonic_widget(entry)
        table.attach(name_label,0,1,0,1,0,0,2,2)

        entry = self.create_option_entry("helpers","mailer")
        self.tips.set_tip(entry,_("The command to launch an email editor"))
        table.attach(entry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        name_label = gtk.Label("E_mail :")
        name_label.set_use_underline(True)
        name_label.set_mnemonic_widget(entry)
        table.attach(name_label,0,1,1,2,0,0,2,2)

        entry = self.create_option_entry("helpers","browser")
        self.tips.set_tip(entry,_("The command to launch a web browser"))
        table.attach(entry,1,2,2,3,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        name_label = gtk.Label("_Browser :")
        name_label.set_use_underline(True)
        name_label.set_mnemonic_widget(entry)
        table.attach(name_label,0,1,2,3,0,0,2,2)

    def update_id(self,*args):
        token = self.prefs.get("user_info","flickr_token")
        if token=="":
            # not signed in
            self.token_label.set_text(_("Not signed in"))
        else:
            self.token_label.set_text(_("Signed in"))

        self.signoff.set_sensitive(token != "")

    def do_signoff(self,widget):
        self.prefs.set("user_info","flickr_token","")
        self.prefs.set("user_info","nsid","")
        
    def create_flickr_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label(_("_Flickr"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)

        self.signoff = gtk.Button(_("_Sign out from Flickr"))
        self.signoff.connect("clicked",self.do_signoff)

        self.token_label = gtk.Label("")
        table.attach(self.token_label,0,2,0,1,0,0,2,2)

        table.attach(self.signoff,0,1,1,2,0,0,2,2)

        self.prefs.connect('preferences-changed',self.update_id)
        self.update_id()
        
    def create_auto_deepen_widget(self):
        widget = gtk.CheckButton("Auto _Deepen")
        self.tips.set_tip(widget,"Adjust number of iterations automatically")
        widget.set_use_underline(True)
        
        def set_widget(*args):
            widget.set_active(self.prefs.getboolean("display","autodeepen"))

        def set_prefs(*args):
            self.prefs.set("display","autodeepen",str(widget.get_active()))

        set_widget()
        self.prefs.connect('preferences-changed',set_widget)
        widget.connect('toggled',set_prefs)

        return widget

    def create_antialias_menu(self):
        optMenu = utils.create_option_menu(["None", "Fast", "Best"])

        def set_widget(*args):
            utils.set_selected(optMenu, self.prefs.getint("display","antialias"))

        def set_prefs(*args):
            index = utils.get_selected(optMenu)
            if index != -1:
                self.prefs.set("display","antialias",str(index))

        set_widget()
        self.prefs.connect('preferences-changed',set_widget)
        optMenu.connect('changed',set_prefs)
        return optMenu
    
    def create_image_options_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label("_Image")
        label.set_use_underline(True)
        self.notebook.append_page(table,label)

        wentry = self.create_width_entry()
        table.attach(wentry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        wlabel = gtk.Label("_Width :")
        wlabel.set_mnemonic_widget(wentry)
        wlabel.set_use_underline(True)
        table.attach(wlabel,0,1,0,1,0,0,2,2)

        hentry = self.create_height_entry()
        table.attach(hentry,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        hlabel = gtk.Label("_Height :")
        hlabel.set_mnemonic_widget(hentry)
        hlabel.set_use_underline(True)
        table.attach(hlabel,0,1,1,2,0,0,2,2)

        self.fix_ratio = gtk.CheckButton("Maintain Aspect _Ratio")
        self.tips.set_tip(self.fix_ratio,"Keep the image rectangle the same shape when changing its size")
        self.fix_ratio.set_use_underline(True)
        table.attach(self.fix_ratio,0,2,2,3,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        self.fix_ratio.set_active(True)

        # auto deepening
        self.auto_deepen = self.create_auto_deepen_widget()
        table.attach(self.auto_deepen,0,2,3,4,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        # antialiasing
        optMenu = self.create_antialias_menu()
        table.attach(optMenu,1,2,4,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        aalabel = gtk.Label("_Antialiasing : ")
        aalabel.set_use_underline(True)
        aalabel.set_mnemonic_widget(optMenu)
        table.attach(aalabel,0,1,4,5,0,0,2,2)
        
