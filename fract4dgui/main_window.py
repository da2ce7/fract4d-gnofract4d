# main window

import sys
import os
import copy

import gtk

sys.path.append("..")
from fract4d import fractal,fc,fract4dc


import gtkfractal, model, preferences, autozoom, settings
import colors, undo, browser, fourway, angle, utils

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
        
        self.f = gtkfractal.T(self.compiler,self)
        self.create_subfracts(self.f)
        
        self.set_filename(None)
        
        try:
            # try to make default image more interesting
            self.f.set_cmap(utils.find_resource(
                "basic.map",
                "maps",
                "share/maps/gnofract4d"))
            self.f.saved = True
        except:
            pass
            
        self.model = model.Model(self.f)

        preferences.userPrefs.connect('preferences-changed',
                                      self.on_prefs_changed)

        self.create_menu()
        self.create_toolbar()
        self.create_fractal(self.f)
        self.create_status_bar()
        
        self.window.show_all()

        self.update_subfract_visibility(False)

        self.update_compiler_prefs(preferences.userPrefs)
        self.update_image_prefs(preferences.userPrefs)
        

        self.statuses = [ _("Done"),
                          _("Calculating"),
                          _("Deepening (%d iterations)"),
                          _("Antialiasing"),
                          _("Paused") ]

    def update_subfract_visibility(self,visible):
        if visible:
            for f in self.subfracts:
                f.widget.show()
                self.weirdness.show()
        else:
            for f in self.subfracts:
                f.widget.hide()
                self.weirdness.hide()
                
        self.show_subfracts = visible
        self.update_image_prefs(preferences.userPrefs)
        
    def update_subfracts(self):
        if not self.show_subfracts:
            return
        
        for f in self.subfracts:
            f.interrupt()
            f.set_fractal(self.f.copy_f())
            f.mutate(self.weirdness_adjustment.get_value()/100.0)
            aa = preferences.userPrefs.getint("display","antialias")
            auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
            f.draw_image(aa,auto_deepen)
        
    def create_subfracts(self,f):
        self.subfracts = [ None ] * 12
        for i in xrange(12):
            self.subfracts[i] = gtkfractal.SubFract(
                self.compiler,f.width//4,f.height//4)
            self.subfracts[i].set_master(f)
            
    def attach_subfract(self,i,x,y):
        self.ftable.attach(
            self.subfracts[i].widget,
            x, x+1, y, y+1,
            gtk.EXPAND | gtk.FILL,
            gtk.EXPAND | gtk.FILL,
            1,1)
            
    def create_fractal(self,f):
        window = gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        
        f.connect('parameters-changed', self.on_fractal_change)
        
        window.set_size_request(640+8,480+8)

        self.fixed = gtk.Fixed()
        self.ftable = gtk.Table(4,4,False)
        self.fixed.put(self.ftable,0,0)
        self.ftable.attach(
            f.widget,
            1,3,1,3,
            gtk.EXPAND | gtk.FILL,
            gtk.EXPAND | gtk.FILL,
            1,1)

        self.attach_subfract(0,0,0)
        self.attach_subfract(1,1,0)
        self.attach_subfract(2,2,0)
        self.attach_subfract(3,3,0)
        
        self.attach_subfract(4,0,1)
        self.attach_subfract(5,3,1)
        self.attach_subfract(6,0,2)
        self.attach_subfract(7,3,2)
        
        self.attach_subfract(8,0,3)
        self.attach_subfract(9,1,3)
        self.attach_subfract(10,2,3)
        self.attach_subfract(11,3,3)

        window.add_with_viewport(self.fixed)
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
        if self.show_subfracts:
            w = w //2 ; h = h // 2
            for f in self.subfracts:
                f.set_size(w//2, h//2)
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
        if not self.f.saved:
            title += "*"
            
        self.window.set_title(title)
        
    def on_fractal_change(self,*args):
        self.draw()
        self.set_window_title()
        self.update_subfracts()
        
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
            (_('/_Tools/_Autozoom...'), '<control>A',
             self.autozoom, 0, ''),
            (_('/_Tools/_Explorer'), '<control>E',
             self.toggle_explorer, 0, '<ToggleItem>'),
            
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

        self.explore_menu = item_factory.get_item(_("/Tools/Explorer"))
        
        # need to reference the item factory or the menus
        # later disappear randomly - some sort of bug in pygtk, python, or gtk
        self.save_factory = item_factory
        self.vbox.pack_start(menubar, gtk.FALSE, gtk.TRUE, 0)

    def toggle_explorer(self, action, menuitem):
        self.set_explorer_state(menuitem.get_active())
        
    def create_status_bar(self):
        self.bar = gtk.ProgressBar()
        self.vbox.pack_end(self.bar, expand=gtk.FALSE)

    def update_preview(self,f):
        self.preview.set_fractal(f.copy_f())
        self.draw_preview()

    def draw_preview(self):
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
        self.preview.draw_image(False,auto_deepen)

    def deepen_now(self, widget):
        self.f.double_maxiter()
    
    def create_toolbar(self):
        self.toolbar = gtk.Toolbar()
        self.toolbar.set_tooltips(True)
        self.vbox.pack_start(self.toolbar,expand=gtk.FALSE)

        # preview
        self.preview = gtkfractal.SubFract(self.compiler)
        self.preview.set_size(40,40)
        self.update_preview(self.f)
        self.f.connect('parameters-changed', self.update_preview)
        
        self.toolbar.append_element(
            gtk.TOOLBAR_CHILD_WIDGET,            
            self.preview.widget,
            _("Preview"),
            _("Shows what the next operation would do"),
            None,
            None,
            None,
            None
            )

        # angles
        self.toolbar.append_space()

        self.create_angle_widget(
            _("xy"), _("Angle in the XY plane"), self.f.XYANGLE)

        self.create_angle_widget(
            _("xz"), _("Angle in the XZ plane"), self.f.XZANGLE)

        self.create_angle_widget(
            _("xw"), _("Angle in the XW plane"), self.f.XWANGLE)

        self.create_angle_widget(
            _("yz"), _("Angle in the YZ plane"), self.f.YZANGLE)

        self.create_angle_widget(
            _("yw"), _("Angle in the YW plane"), self.f.YWANGLE)

        self.create_angle_widget(
            _("zw"), _("Angle in the ZW plane"), self.f.ZWANGLE)

        # fourways
        self.toolbar.append_space()
        
        self.add_fourway(_("pan"), _("Pan around the image"), 0)
        self.add_fourway(
            _("wrp"),
            _("Mutate the image by moving along the other 2 axes"), 2)

        image = gtk.Image()
        image.set_from_file(
            utils.find_resource('deepen_now.png',
                                'pixmaps',
                                'share/pixmaps/gnofract4d'))

        self.toolbar.append_element(
            gtk.TOOLBAR_CHILD_BUTTON,
            None,
            _("Deepen"),
            _("Double the maximum number of iterations"),
            None,
            image,
            self.deepen_now,
            None)
        
        # undo/redo
        self.toolbar.append_space()
        
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

        # explorer mode widgets
        self.toolbar.append_space()

        image = gtk.Image()
        image.set_from_file(
            utils.find_resource('explorer_mode.png',
                                'pixmaps',
                                'share/pixmaps/gnofract4d'))
                            
        self.explorer_toggle = gtk.ToggleButton()
        self.toolbar.append_element(
            gtk.TOOLBAR_CHILD_TOGGLEBUTTON,
            None,
            _("Explore"),
            _("Toggle Explorer Mode"),
            None,
            image,
            self.toolbar_toggle_explorer,
            None)

        self.weirdness_adjustment = gtk.Adjustment(
            20.0, 0.0, 100.0, 5.0, 5.0, 0.0)

        self.weirdness = gtk.HScale(self.weirdness_adjustment)
        self.weirdness.set_size_request(80, 40)

        self.weirdness.set_update_policy(
            gtk.UPDATE_DISCONTINUOUS)

        def on_weirdness_changed(adjustment):
            self.update_subfracts()
            
        self.weirdness_adjustment.connect('value-changed',on_weirdness_changed)
        
        self.toolbar.append_element(
            gtk.TOOLBAR_CHILD_WIDGET,            
            self.weirdness,
            _("Weirdness"),
            _("How different to make the random mutant fractals"),
            None,
            None,
            None,
            None
            )

    def toolbar_toggle_explorer(self,widget):
        self.set_explorer_state(widget.get_active())

    def set_explorer_state(self,active):
        #self.explore_menu.set_active(active)
        #self.explorer_toggle.set_active(active)
        self.update_subfract_visibility(active)
        self.update_subfracts()

    def create_angle_widget(self,name,tip,axis):
        my_angle = angle.T(name)
        my_angle.connect('value-slightly-changed',
                         self.on_angle_slightly_changed)
        my_angle.connect('value-changed',
                         self.on_angle_changed)

        self.f.connect('parameters-changed',
                       self.update_angle_widget,my_angle)
        
        my_angle.axis = axis

        self.toolbar.append_element(
            gtk.TOOLBAR_CHILD_WIDGET,            
            my_angle.widget,
            tip,
            tip,
            None,
            None,
            None,
            None
            )

    def update_angle_widget(self,f,widget):
        widget.set_value(f.get_param(widget.axis))
        
    def on_angle_slightly_changed(self,widget,val):
        self.preview.set_param(widget.axis, val)
        self.draw_preview()

    def on_angle_changed(self,widget,val):
        self.f.set_param(widget.axis,val)
        
    def on_drag_fourway(self,widget,dx,dy):
        self.preview.nudge(dx/10.0,dy/10.0, widget.axis)
        self.draw_preview()
    
    def on_release_fourway(self,widget,dx,dy):
        self.f.nudge(dx/10.0, dy/10.0, widget.axis)
    
    def add_fourway(self, name, tip, axis):
        my_fourway = fourway.T(name)
        self.toolbar.append_element(
            gtk.TOOLBAR_CHILD_WIDGET,            
            my_fourway.widget,
            tip,
            None,
            None,
            None,
            None,
            None
            )

        my_fourway.axis = axis
        
        my_fourway.connect('value-slightly-changed', self.on_drag_fourway)
        my_fourway.connect('value-changed', self.on_release_fourway)
        
        
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
        local_dir = "doc/gnofract4d-manual/%s/" % loc
        install_dir = "share/gnome/help/gnofract4d/%s/" % loc

        helpfile = utils.find_resource(base_help_file, local_dir, install_dir)
        abs_file = os.path.abspath(helpfile)
        
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
                return
            
        fs.destroy()
        browser.show(self.window, self.f, browser.FRACTAL)
    
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

    def check_save_fractal(self):
        msg = _("Do you want to save the current parameters before quitting?")
        if not self.f.saved:
            d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_QUESTION,
                                  gtk.BUTTONS_YES_NO,
                                  msg)
            response = d.run()                
            d.destroy()
            if response == gtk.RESPONSE_YES:
                self.save(None,None)
        
            
    def about(self,action,widget):
        self.display_help("about")

    def quit(self,action,widget=None):
        try:
            self.f.interrupt()
            for f in self.subfracts:
                f.interrupt()
            self.check_save_fractal()
            preferences.userPrefs.save()
            self.compiler.clear_cache()
        finally:
            gtk.main_quit()


