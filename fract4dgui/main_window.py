# main window

import sys
import os

import gtk

sys.path.append("..")
from fract4d import fractal,fc,fract4dc


import gtkfractal, model, preferences, autozoom, settings
import colors, undo, browser

class MainWindow:
    def __init__(self):
        # window widget
        self.window = gtk.Window()
        self.window.connect('destroy', self.quit)

        # keyboard handling
        self.keymap = {
            gtk.keysyms.Left : self.on_key_left,
            gtk.keysyms.Right : self.on_key_right,
            gtk.keysyms.Up : self.on_key_up,
            gtk.keysyms.Down : self.on_key_down
            }

        self.accelgroup = gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)
        self.window.connect('key-release-event', self.on_key_release)

        # create fractal compiler and load standard formula and
        # coloring algorithm files
        self.compiler = fc.Compiler()
        self.compiler.file_path.append("formulas")
        self.compiler.file_path.append(
            os.path.join(sys.exec_prefix, "share/formulas/gnofract4d"))
                
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        
        self.f = gtkfractal.T(self.compiler)
        
        self.set_filename(None)
        
        try:
            # try to make default image more interesting
            self.f.set_cmap(os.path.join(
                sys.exec_prefix,
                "share/maps/gnofract4d",
                "basic.map"))
        except:
            pass
            
        self.model = model.Model(self.f)

        preferences.userPrefs.connect('preferences-changed',
                                      self.on_prefs_changed)

        self.update_compiler_prefs(preferences.userPrefs)
        self.update_image_prefs(preferences.userPrefs)
        
        self.create_menu()
        self.create_toolbar()
        self.create_fractal(self.f)
        self.create_status_bar()
        
        self.window.show_all()

        self.statuses = [ _("Done"),
                          _("Calculating"),
                          _("Deepening (%d iterations)"),
                          _("Antialiasing"),
                          _("Paused") ]

    def create_fractal(self,f):
        window = gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        
        f.connect('parameters-changed', self.on_fractal_change)

        self.draw()
        
        window.set_size_request(640+2,480+2)
        window.add_with_viewport(self.f.widget)
        f.connect('progress_changed', self.progress_changed)
        f.connect('status_changed',self.status_changed)
        
        self.vbox.pack_start(window)

    def draw(self):
        aa = preferences.userPrefs.getint("display","antialias")
        auto_deepen = preferences.userPrefs.getint("display","autodeepen")
        self.f.draw_image(aa,auto_deepen)
        
    def update_compiler_prefs(self,prefs):
        # update compiler
        self.compiler.compiler_name = prefs.get("compiler","name")
        self.compiler.flags = prefs.get("compiler","options")
        self.f.update_formula()

    def update_image_prefs(self,prefs):
        (w,h) = (prefs.getint("display","width"),
                 prefs.getint("display","height"))
        self.f.set_size(w,h)

    def on_prefs_changed(self,prefs):
        self.f.freeze()
        self.update_compiler_prefs(prefs)
        self.update_image_prefs(prefs)
        if self.f.thaw():
            self.draw()

    def set_window_title(self):
        if self.filename == None:
            title = _("(Untitled %s)") % self.f.funcName
        else:
            title = self.filename
        self.window.set_title(title)
        
    def on_fractal_change(self,object):
        self.draw()
        self.set_window_title()
        
    def set_filename(self,name):
        self.filename = name
        self.set_window_title()

    def nudge(self,x,y,state):
        axis = 0
        if state & gtk.gdk.SHIFT_MASK:
            axis = 2
        if state & gtk.gdk.CONTROL_MASK:
            x *= 10.0
            y *= 10.0
        self.f.nudge(x,y,axis)
        
    def on_key_left(self,state):
        self.nudge(-1, 0,state)

    def on_key_right(self,state):
        self.nudge(1, 0,state)

    def on_key_up(self,state):
        self.nudge(0, -1,state)

    def on_key_down(self,state):
        self.nudge(0, 1,state)
        
    def on_key_release(self, widget, event):
        fn = self.keymap.get(event.keyval)
        if fn:
            fn(event.state)
                    
    def progress_changed(self,f,progress):
        self.bar.set_fraction(progress/100.0)

    def status_changed(self,f,status):
        if status == 2:
            # deepening
            text = self.statuses[status] % self.f.maxiter
        else:
            text = self.statuses[status]
            
        self.bar.set_text(text)
        
    def create_menu(self):
        menu_items = (
            (_('/_File'), None, None, 0, '<Branch>' ),
            (_('/File/_Open Parameter File...'), '<control>O',
             self.open, 0, '<StockItem>', gtk.STOCK_OPEN),
            (_('/File/Open _Formula File...'), '<control><shift>O',
             self.open_formula, 0, ''),
            (_('/File/_Save'), '<control>S',
             self.save, 0, '<StockItem>', gtk.STOCK_SAVE),
            (_('/File/Save _As...'), '<control><shift>S',
             self.saveas, 0, '<StockItem>', gtk.STOCK_SAVE_AS),
            (_('/File/Save _Image'), '<control>I',
             self.save_image, 0, ''),
            (_('/File/sep1'), None,
             None, 0, '<Separator>'),
            (_('/File/_Quit'), '<control>Q',
             self.quit, 0, '<StockItem>', gtk.STOCK_QUIT),   

            (_('/_Edit'), None,
             None, 0, '<Branch>'),
            (_('/Edit/_Fractal Settings...'),'<control>F',
             self.settings, 0, ''),
            (_('/Edit/_Colors...'), '<control>L',
             self.colors, 0, ''),
            (_('/Edit/_Preferences...'), '<control>P',
             self.preferences, 0, '<StockItem>', gtk.STOCK_PREFERENCES),
            (_('/Edit/_Undo'), '<control>Z',
             self.undo, 0, ''),
            (_('/Edit/_Redo'), '<control>Y',
             self.redo, 0, ''),
            (_('/Edit/R_eset'), 'Home',
             self.reset, 0, '<StockItem>', gtk.STOCK_HOME),

            (_('/_Tools'), None,
             None, 0, '<Branch>'),
            (_('/_Tools/_Autozoom'), '<control>A',
             self.autozoom, 0, ''),

            (_('/_Help'), None,
             None, 0, '<Branch>'),
            (_('/_Help/_Contents'), 'F1',
             self.contents, 0, ''),
            (_('/Help/_About'), None,
             self.about, 0, ''),
            )
    
        item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>', self.accelgroup)
        item_factory.create_items(menu_items)

        menubar = item_factory.get_widget('<main>')

        undo = item_factory.get_item(_("/Edit/Undo"))
        self.model.seq.make_undo_sensitive(undo)
        redo = item_factory.get_item(_("/Edit/Redo"))
        self.model.seq.make_redo_sensitive(redo)

        # need to reference the item factory or the menus
        # later disappear randomly - some sort of bug in pygtk, python, or gtk
        self.save_factory = item_factory
        self.vbox.pack_start(menubar, gtk.FALSE, gtk.TRUE, 0)
        
    def create_status_bar(self):
        self.bar = gtk.ProgressBar()
        self.vbox.pack_end(self.bar, expand=gtk.FALSE)

    def create_toolbar(self):
        self.toolbar = gtk.Toolbar()
        self.toolbar.insert_stock(
            gtk.STOCK_UNDO,
            _("Undo the last change"),
            _("Undo the last change"),
            self.undo,
            None,
            -1)

        self.model.seq.make_undo_sensitive(self.toolbar.get_children()[-1])
        
        self.toolbar.insert_stock(
            gtk.STOCK_REDO,
            _("Redo the last undone change"),
            _("Redo the last undone change"),
            self.redo,
            None,
            -1)

        self.model.seq.make_redo_sensitive(self.toolbar.get_children()[-1])

        self.vbox.pack_start(self.toolbar,expand=gtk.FALSE)

    def save_file(self,file):
        try:
            self.f.save(open(file,'w'))
            self.set_filename(file)
            return True
        except Exception, err:
            self.show_error_message(_("Error saving to file %s: '%s'") %
                                    (file, err))
            return False

    def save(self,action,widget):
        if self.filename == None:
            self.saveas(action,widget)
        else:
            self.save_file(self.filename)
        

    def saveas(self,action,widget):
        # need to gather a filename
        fs = gtk.FileSelection(_("Save Parameters"))
        fs.show_all()

        name = None
        while True:
            result = fs.run()
            if result == gtk.RESPONSE_OK:
                name = fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                if self.save_file(name):
                    break

        fs.destroy()

    def confirm(self,name):
        'if this file exists, check with user before overwriting it'
        if os.path.exists(name):
            d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_QUESTION,
                                  gtk.BUTTONS_YES_NO,
                                  _("File %s already exists. Overwrite?") % name)
            response = d.run()                
            d.destroy()
            return response == gtk.RESPONSE_YES
        else:
            return True

    def show_warning(self,message):
        d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                              gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                              message)
        d.run()
        d.destroy()
        
    def show_error_message(self,message):
        d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                              gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                              message)
        d.run()
        d.destroy()

    def save_image(self,action,widget):
        fs = gtk.FileSelection("Save Image")
        fs.show_all()
        
        name = None
        while True:
            result = fs.run()
            if result == gtk.RESPONSE_OK:
                name = fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                try:
                    self.f.save_image(name)
                    break
                except Exception, err:
                    self.show_error_message(_("Error saving %s:\n%s") % (name, err))
        fs.destroy()
                
    def settings(self,action,widget):
        settings.show_settings(self.window,self.f)
        
    def colors(self,action,widget):
        colors.show_colors(self.window,self.f)
        
    def preferences(self,action,widget):
        preferences.show_preferences(self.window, self.f)
        
    def undo(self,*args):
        self.model.undo()
        
    def redo(self,*args):
        self.model.redo()
        
    def reset(self,action,widget):
        self.f.reset()

    def autozoom(self,action,widget):
        autozoom.show_autozoom(self.window, self.f)
        
    def contents(self,action,widget):
        self.display_help()

    def display_help(self,section=None):
        base_help_file = "gnofract4d-manual.xml"
        loc = "C" # FIXME

        # look locally first to support run-before-install
        build_dir = "doc/gnofract4d-manual/%s/" % loc
        helpfile = os.path.join(build_dir,base_help_file)
        abs_file = os.path.abspath(helpfile)
        
        if not os.path.isfile(abs_file):
            # otherwise try where the installer should have put it
            dir = "share/gnome/help/gnofract4d/%s/" % loc
            abs_file = os.path.join(sys.exec_prefix, dir, base_help_file)

        if not os.path.isfile(abs_file):
            self.show_error_message(_("Can't find help file %s") % abs_file)
            return
        
        if section == None:
            anchor = ""
        else:
            anchor = "#" + section

        os.system("yelp ghelp://%s%s 2>/dev/null &" % (abs_file, anchor))

    def open_formula(self,action,widget):
        fs = gtk.FileSelection(_("Open Formula File"))
        fs.show_all()
        
        while True:
            result = fs.run()            
            if result == gtk.RESPONSE_OK:
                if self.load_formula(fs.get_filename()):
                    break
            else:
                break
            
        fs.destroy()
        
    
    def open(self,action,widget):
        fs = gtk.FileSelection(_("Open Parameter File"))
        fs.show_all()
        
        while True:
            result = fs.run()            
            if result == gtk.RESPONSE_OK:
                if self.load(fs.get_filename()):
                    break
            else:
                break
            
        fs.destroy()

    def load(self,file):
        try:
            self.f.loadFctFile(open(file))
            self.set_filename(file)
            return True
        except Exception, err:
            self.show_error_message(_("Error opening %s: '%s'") % (file, err))
            return False

    def load_formula(self,file):
        try:
            self.compiler.load_formula_file(file)
            browser.update()
            return True
        except Exception, err:
            self.show_error_message(_("Error opening %s: '%s'") % (file, err))
            return False

    def about(self,action,widget):
        self.display_help("about")

    def quit(self,action,widget=None):
        try:
            preferences.userPrefs.save()
            self.compiler.clear_cache()
        finally:
            gtk.main_quit()


