# main window

import sys
import os
import signal
import copy
import math
import re

import gtk

sys.path.append("..")
from fract4d import fractal,fc,fract4dc

import gtkfractal, model, preferences, autozoom, settings, toolbar
import colors, undo, browser, fourway, angle, utils, hig, painter
import icons

re_ends_with_num = re.compile(r'\d+\Z')
re_cleanup = re.compile(r'[\s\(\)]+')

class MainWindow:
    def __init__(self, extra_paths=[]):
        self.quit_when_done =False
        self.save_filename = None
        self.f = None
        
        # window widget

        self.set_icon()
        
        self.window = gtk.Window()
        self.window.connect('destroy', self.quit)

        # keyboard handling
        self.keymap = {
            gtk.keysyms.Left : self.on_key_left,
            gtk.keysyms.Right : self.on_key_right,
            gtk.keysyms.Up : self.on_key_up,
            gtk.keysyms.Down : self.on_key_down,
            gtk.keysyms.Escape : self.on_key_escape
            }

        self.accelgroup = gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)
        self.window.connect('key-release-event', self.on_key_release)

        # create fractal compiler and load standard formula and
        # coloring algorithm files
        self.compiler = fc.Compiler()

        self.update_compiler_prefs(preferences.userPrefs)
        self.compiler.file_path += extra_paths
                
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        
        self.f = gtkfractal.T(self.compiler,self)
        self.f.freeze() # create frozen - main prog will thaw us
        self.create_subfracts(self.f)
        
        self.set_filename(None)
        
        try:
            # try to make default image more interesting
            self.f.set_cmap(utils.find_resource(
                "basic.map",
                "maps",
                "share/maps/gnofract4d"))
        except:
            pass
            
        self.model = model.Model(self.f)

        preferences.userPrefs.connect('preferences-changed',
                                      self.on_prefs_changed)

        self.create_menu()
        self.create_toolbar()
        self.create_fractal(self.f)
        self.create_status_bar()
        self.create_filechoosers()
        
        self.window.show_all()

        self.update_subfract_visibility(False)

        self.update_image_prefs(preferences.userPrefs)
        
        self.statuses = [ _("Done"),
                          _("Calculating"),
                          _("Deepening (%d iterations)"),
                          _("Antialiasing"),
                          _("Paused") ]

        self.f.set_saved(True)

    def create_filechoosers(self):
        self.saveas_fs = utils.get_file_save_chooser(
            _("Save Parameters"),
            self.window,
            ["*.fct"])

        self.saveimage_fs = utils.get_file_save_chooser(
            _("Save Image"),
            self.window,
            ["*.png","*.jpg","*.jpeg"])

        self.open_formula_fs = utils.get_file_open_chooser(
            _("Open Formula File"),
            self.window,
            ["*.frm", "*.cfrm", "*.ucl", "*.ufm"])

        self.open_fs = utils.get_file_open_chooser(
            _("Open Parameter File"),
            self.window,
            ["*.fct"])

    def set_icon(self):
        try:
            gtk.window_set_default_icon_list([icons.logo.pixbuf])
        except Exception,err:
            # not supported in this pygtk. Oh well...
            pass
        
    def update_subfract_visibility(self,visible):
        if visible:
            for f in self.subfracts:
                f.widget.show()
            self.weirdbox.show_all()
        else:
            for f in self.subfracts:
                f.widget.hide()
            self.weirdbox.hide_all()

        self.show_subfracts = visible
        self.update_image_prefs(preferences.userPrefs)
        
    def update_subfracts(self):
        if not self.show_subfracts:
            return

        aa = preferences.userPrefs.getint("display","antialias")
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
        maps = colors.maps().values()

        for f in self.subfracts:
            f.interrupt()
            f.freeze()
            f.set_fractal(self.f.copy_f())
            f.mutate(
                self.weirdness_adjustment.get_value()/100.0,
                self.color_weirdness_adjustment.get_value()/100.0,
                maps)
            f.thaw()
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

    def on_formula_change(self, f):
        is4d = f.formula.is4D()
        for widget in self.four_d_sensitives:
            widget.set_sensitive(is4d)
        
    def create_fractal(self,f):
        self.swindow = gtk.ScrolledWindow()
        self.swindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        
        f.connect('parameters-changed', self.on_fractal_change)
        f.connect('formula-changed', self.on_formula_change)
        
        self.swindow.set_size_request(640+8,400+8)

        self.fixed = gtk.Fixed()
        self.ftable = gtk.Table(4,4,False)
        self.fixed.put(self.ftable,0,0)
        self.ftable.attach(
            f.widget,
            1,3,1,3,
            gtk.EXPAND | gtk.FILL,
            gtk.EXPAND | gtk.FILL,
            0,0) #1,1)

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

        self.swindow.add_with_viewport(self.fixed)
        self.swindow.get_child().set_shadow_type(gtk.SHADOW_NONE)
                
        f.connect('progress_changed', self.progress_changed)
        f.connect('status_changed',self.status_changed)

        hbox = gtk.HBox()
        hbox.pack_start(self.swindow)
        self.control_box = gtk.VBox()
        hbox.pack_start(self.control_box,False,False)
        self.vbox.pack_start(hbox)

    def draw(self):
        aa = preferences.userPrefs.getint("display","antialias")
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
        self.f.draw_image(aa,auto_deepen)
        
    def update_compiler_prefs(self,prefs):
        # update compiler
        self.compiler.compiler_name = prefs.get("compiler","name")
        self.compiler.flags = prefs.get("compiler","options")
        self.compiler.file_path = prefs.get_list("formula_path")

        if self.f:
            self.f.update_formula()

    def update_image_prefs(self,prefs):
        (w,h) = (prefs.getint("display","width"),
                 prefs.getint("display","height"))
        if self.show_subfracts:
            w = w //2 ; h = h // 2
            for f in self.subfracts:
                f.set_size(w//2, h//2)
            w += 2; h += 2
        self.f.set_size(w,h)
        self.f.set_nthreads(prefs.getint("general","threads"))
                            
    def deferred_prefs_changed(self,prefs):
        gtk.idle_add(self.on_prefs_changed, prefs)

    def on_prefs_changed(self,prefs):
        self.f.freeze()
        self.update_compiler_prefs(prefs)
        self.update_image_prefs(prefs)
        if self.f.thaw():
            self.draw()

    def display_filename(self):
        if self.filename == None:
            return _("(Untitled %s)") % self.f.get_func_name()
        else:
            return self.filename

    def default_save_filename(self,extension=".fct"):
        global re_ends_with_num, re_cleanup        
        if self.filename == None:
            base_name = self.f.get_func_name()
            base_name = re_cleanup.sub("_", base_name) + extension
        else:
            base_name = self.filename

        # need to gather a filename
        (base,ext) = os.path.splitext(base_name)
        base = re_ends_with_num.sub("",base)

        save_filename = base + extension
        i = 1
        while True:
            if not os.path.exists(save_filename):
                break
            save_filename = base + ("%03d" % i) + extension
            i += 1
        return save_filename
    
    def set_window_title(self):
        title = self.display_filename()
        if not self.f.get_saved():
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
        current_widget = self.window.get_focus()
        if isinstance(current_widget, gtk.Entry):
            # otherwise we steal cursor motion through entry
            return
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

        if status == 0:
            # done
            if self.save_filename:
                self.f.save_image(self.save_filename)
            if self.quit_when_done:
                self.f.set_saved(True)
                self.quit(None,None)
            
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
            (_('/Edit/_Gradient...'), '<control>G',
             self.colors, 0, ''),
            (_('/Edit/_Preferences...'), '<control>P',
             self.preferences, 0, '<StockItem>', gtk.STOCK_PREFERENCES),
            (_('/Edit/sep1'), None,
             None, 0, '<Separator>'),
            (_('/Edit/_Undo'), '<control>Z',
             self.undo, 0, ''),
            (_('/Edit/_Redo'), '<control><shift>Z',
             self.redo, 0, ''),
            (_('/Edit/sep2'), None,
             None, 0, '<Separator>'),
            (_('/Edit/R_eset'), 'Home',
             self.reset, 0, '<StockItem>', gtk.STOCK_HOME),
            (_('/Edit/Re_set Zoom'), '<control>Home',
             self.reset_zoom, 0, ''),

            (_('/_View'), None,
             None, 0, '<Branch>'),
            (_('/_View/_Full Screen'), 'F11',
             self.menu_full_screen, 0, ''),
            
            (_('/_Tools'), None,
             None, 0, '<Branch>'),
            (_('/_Tools/_Autozoom...'), '<control>A',
             self.autozoom, 0, ''),
            (_('/_Tools/_Explorer'), '<control>E',
             self.toggle_explorer, 0, '<ToggleItem>'),
            (_('/_Tools/Formula _Browser...'), '<control>B',
             self.browser, 0, ''),
            (_('/_Tools/_Randomize Colors'), '<control>R',
             self.randomize_colors, 0, ''),
            
            (_('/_Tools/_Painter...'), None,
             self.painter, 0, ''),
            
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
        self.menubar = menubar

    def browser(self,action,menuitem):
        browser.show(self.window,self.f,browser.FRACTAL)

    def randomize_colors(self,action,menuitem):
        self.f.make_random_colors(8)

    def painter(self,action,menuitem):
        painter.show(self.window,self.f)
            
    def toggle_explorer(self, action, menuitem):
        self.set_explorer_state(menuitem.get_active())

    def menu_full_screen(self, action, menuitem):
        self.set_full_screen(True)

    def on_key_escape(self, state):
        self.set_full_screen(False)
        
    def set_full_screen(self, is_full):
        if is_full:
            self.window.fullscreen()
            self.window.set_decorated(False)
            self.menubar.hide()
            self.toolbar.hide()
            self.bar.hide()
            self.swindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)

            screen = self.window.get_screen()
            preferences.userPrefs.set_size(
                screen.get_width(),
                screen.get_height())

        else:
            self.window.set_decorated(True)
            self.swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.menubar.show()
            self.toolbar.show()
            self.bar.show()
            self.window.unfullscreen()
            
    def create_status_bar(self):
        self.bar = gtk.ProgressBar()
        self.vbox.pack_end(self.bar, expand=gtk.FALSE)

    def update_preview(self,f,flip2julia=False):
        self.preview.set_fractal(f.copy_f())
        self.draw_preview()

    def update_preview_on_pointer(self,f,button, x,y):
        if button == 2:
            self.preview.set_fractal(f.copy_f())
            self.preview.relocate(x,y,1.0)
            self.preview.flip_to_julia()
            self.draw_preview()
        
    def draw_preview(self):
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
        self.preview.draw_image(False,auto_deepen)

    def deepen_now(self, widget):
        self.f.double_maxiter()
    
    def create_toolbar(self):
        self.toolbar = toolbar.T()
        self.vbox.pack_start(self.toolbar,expand=gtk.FALSE)

        self.four_d_sensitives = []
        
        # preview
        self.toolbar.add_space()
        
        self.preview = gtkfractal.SubFract(self.compiler)
        self.preview.set_size(48,48)
        self.update_preview(self.f)
        self.f.connect('parameters-changed', self.update_preview)
        self.f.connect('pointer-moved', self.update_preview_on_pointer)
        
        self.toolbar.add_widget(
            self.preview.widget,
            _("Preview"),
            _("Shows what the next operation would do"))

        # angles
        self.toolbar.add_space()

        self.create_angle_widget(
            _("xy"), _("Angle in the XY plane"), fractal.T.XYANGLE, False)

        self.create_angle_widget(
            _("xz"), _("Angle in the XZ plane"), fractal.T.XZANGLE, True)

        self.create_angle_widget(
            _("xw"), _("Angle in the XW plane"), fractal.T.XWANGLE, True)

        self.create_angle_widget(
            _("yz"), _("Angle in the YZ plane"), fractal.T.YZANGLE, True)

        self.create_angle_widget(
            _("yw"), _("Angle in the YW plane"), fractal.T.YWANGLE, True)

        self.create_angle_widget(
            _("zw"), _("Angle in the ZW plane"), fractal.T.ZWANGLE, True)

        # fourways
        self.toolbar.add_space()
        
        self.add_fourway(_("pan"), _("Pan around the image"), 0, False)
        self.add_fourway(
            _("wrp"),
            _("Mutate the image by moving along the other 2 axes"), 2, True)

        # deepen/resize
        self.toolbar.add_space()
        
        self.toolbar.add_stock(
            icons.deepen_now.stock_name,
            _("Double the maximum number of iterations"),
            self.deepen_now)

        res_menu = self.create_resolution_menu()

        self.toolbar.add_widget(
            res_menu,
            _("Resolution"),
            _("Change fractal's resolution"))            

        # undo/redo
        self.toolbar.add_space()

        self.toolbar.add_stock(
            gtk.STOCK_UNDO,
            _("Undo the last change"),
            self.undo)

        self.model.seq.make_undo_sensitive(self.toolbar.get_children()[-1])
        
        self.toolbar.add_stock(
            gtk.STOCK_REDO,
            _("Redo the last undone change"),
            self.redo)
        
        self.model.seq.make_redo_sensitive(self.toolbar.get_children()[-1])

        # explorer mode widgets
        self.toolbar.add_space()

        self.toolbar.add_toggle(
            icons.explorer.stock_name,
            icons.explorer.title,
            _("Toggle Explorer Mode"),
            self.toolbar_toggle_explorer)
        
        self.weirdness_adjustment = gtk.Adjustment(
            20.0, 0.0, 100.0, 5.0, 5.0, 0.0)

        self.weirdness = gtk.HScale(self.weirdness_adjustment)
        self.weirdness.set_size_request(100, 20)
        self.weirdness.set_property("value-pos",gtk.POS_RIGHT)
        
        self.weirdness.set_update_policy(
            gtk.UPDATE_DISCONTINUOUS)

        self.weirdbox = gtk.VBox()
        shapebox = gtk.HBox(False,2)
        shape_label = gtk.Label(_("Shape:"))
        shapebox.pack_start(shape_label)
        shapebox.pack_start(self.weirdness)

        self.weirdbox.pack_start(shapebox)
        
        self.toolbar.add_widget(
            self.weirdbox,
            _("Weirdness"),
            _("How different to make the random mutant fractals"))

        self.color_weirdness_adjustment = gtk.Adjustment(
            20.0, 0.0, 100.0, 5.0, 5.0, 0.0)

        self.color_weirdness = gtk.HScale(self.color_weirdness_adjustment)
        self.color_weirdness.set_size_request(100, 20)
        self.color_weirdness.set_property("value-pos",gtk.POS_RIGHT)

        colorbox = gtk.HBox(False,2)
        color_label = gtk.Label(_("Color:"))
        colorbox.pack_start(color_label)
        colorbox.pack_start(self.color_weirdness)
        self.weirdbox.pack_start(colorbox)
        
        self.color_weirdness.set_update_policy(
            gtk.UPDATE_DISCONTINUOUS)

        def on_weirdness_changed(adjustment):
            self.update_subfracts()
            
        self.weirdness_adjustment.connect(
            'value-changed',on_weirdness_changed)
        self.color_weirdness_adjustment.connect(
            'value-changed',on_weirdness_changed)

    def create_resolution_menu(self):
        self.resolutions = [
            (320,240), (640,480),
            (800,600), (1024, 768),
            (1280,1024), (1600,1200)]

        res_names= [ "%dx%d" % (w,h) for (w,h) in self.resolutions]
        
        res_menu = utils.create_option_menu(res_names)

        def set_selected_resolution(prefs):
            res = (w,h) = (prefs.getint("display","width"),
                           prefs.getint("display","height"))

            try:
                index = self.resolutions.index(res)
            except ValueError:
                # not found
                self.resolutions.append(res)
                item = "%dx%d" % (w,h)
                utils.add_menu_item(res_menu, item)
                index = len(self.resolutions)-1

            utils.set_selected(res_menu, index)

        def set_resolution(*args):
            index = utils.get_selected(res_menu)
            if index != -1:
                (w,h) = self.resolutions[index]
                preferences.userPrefs.set_size(w,h)
                self.update_subfracts()
                
        set_selected_resolution(preferences.userPrefs)
        res_menu.connect('changed', set_resolution)

        preferences.userPrefs.connect('preferences-changed',
                                      set_selected_resolution)

        return res_menu
    
    def toolbar_toggle_explorer(self,widget):
        self.set_explorer_state(widget.get_active())

    def set_explorer_state(self,active):
        #self.explore_menu.set_active(active)
        #self.explorer_toggle.set_active(active)
        self.update_subfract_visibility(active)

    def create_angle_widget(self,name,tip,axis, is4dsensitive):
        my_angle = angle.T(name)
        my_angle.connect('value-slightly-changed',
                         self.on_angle_slightly_changed)
        my_angle.connect('value-changed',
                         self.on_angle_changed)

        self.f.connect('parameters-changed',
                       self.update_angle_widget,my_angle)
        
        my_angle.axis = axis

        self.toolbar.add_widget(
            my_angle.widget,
            tip,
            tip)

        if is4dsensitive:
            self.four_d_sensitives.append(my_angle.widget)
        
    def update_angle_widget(self,f,widget):
        widget.set_value(f.get_param(widget.axis))
        
    def on_angle_slightly_changed(self,widget,val):
        self.preview.set_param(widget.axis, val)
        angle_in_degrees = "%.2f" % (float(val)*180.0/math.pi)
        self.bar.set_text(angle_in_degrees)
        self.draw_preview()

    def on_angle_changed(self,widget,val):
        self.f.set_param(widget.axis,val)
        
    def on_drag_fourway(self,widget,dx,dy):
        self.preview.nudge(dx/10.0,dy/10.0, widget.axis)
        self.draw_preview()

    def on_drag_param_fourway(self, widget, dx, dy, order, param_type):
        self.preview.nudge_param(order, param_type, dx, dy)
        self.draw_preview()
                
    def on_release_fourway(self,widget,dx,dy):
        self.f.nudge(dx/10.0, dy/10.0, widget.axis)
    
    def add_fourway(self, name, tip, axis, is4dsensitive):
        my_fourway = fourway.T(name)
        self.toolbar.add_widget(
            my_fourway.widget,
            tip,
            None)

        my_fourway.axis = axis
        
        my_fourway.connect('value-slightly-changed', self.on_drag_fourway)
        my_fourway.connect('value-changed', self.on_release_fourway)

        if is4dsensitive:
            self.four_d_sensitives.append(my_fourway.widget)
        
    def save_file(self,file):
        try:
            self.f.save(open(file,'w'))
            self.set_filename(file)
            return True
        except Exception, err:
            self.show_error_message(
                _("Error saving to file %s") % file, err)
            return False

    def save(self,action,widget):
        if self.filename == None:
            self.saveas(action,widget)
        else:
            self.save_file(self.filename)
        

    def saveas(self,action,widget):
        save_filename = self.default_save_filename()

        utils.set_file_chooser_filename(self.saveas_fs, save_filename)
        self.saveas_fs.show_all()

        name = None
        while True:
            result = self.saveas_fs.run()
            if result == gtk.RESPONSE_OK:
                name = self.saveas_fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                if self.save_file(name):
                    break

        self.saveas_fs.hide()

    def confirm(self,name):
        'if this file exists, check with user before overwriting it'
        if os.path.exists(name):
            msg = _("File %s already exists. Overwrite?") % name
            d = hig.ConfirmationAlert(msg,None,self.window,_("Overwrite"))

            response = d.run()                
            d.destroy()
            return response == gtk.RESPONSE_ACCEPT
        else:
            return True

    def show_warning(self,message):
        d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                              gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                              message)
        d.run()
        d.destroy()
        
    def show_error_message(self,message,exception=None):
        if exception == None:
            secondary_message = ""
        else:
            if isinstance(exception,EnvironmentError):
                secondary_message = exception.strerror or str(exception) or ""
            else:
                secondary_message = str(exception)

        d = hig.ErrorAlert(message, secondary_message,self.window)
        d.run()
        d.destroy()

    def save_image(self,action,widget):
        save_filename = self.default_save_filename(".png")

        utils.set_file_chooser_filename(self.saveimage_fs,save_filename)
        self.saveimage_fs.show_all()
        
        name = None
        while True:
            result = self.saveimage_fs.run()
            if result == gtk.RESPONSE_OK:
                name = self.saveimage_fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                try:
                    self.f.save_image(name)
                    break
                except Exception, err:
                    self.show_error_message(
                        _("Error saving image %s") % name, err)
        self.saveimage_fs.hide()
                
    def settings(self,action,widget):
        settings.show_settings(self.window, self.control_box, self.f, False)
        
    def colors(self,action,widget):
        colors.show_colors(self.window, self.control_box, self.f, True)
        
    def preferences(self,action,widget):
        preferences.show_preferences(self.window, self.f)
        
    def undo(self,*args):
        self.model.undo()
        
    def redo(self,*args):
        self.model.redo()
        
    def reset(self,action,widget):
        self.f.reset()

    def reset_zoom(self,action,widget):
        self.f.reset_zoom()
        
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
            self.show_error_message(
                _("Can't display help"),
                _("Can't find help file '%s'") % abs_file)
            return
        
        if section == None:
            anchor = ""
        else:
            anchor = "#" + section

        yelp_path = utils.find_in_path("yelp")
        if not yelp_path:
            return
        
        os.system("yelp ghelp://%s%s >/dev/null 2>&1 &" % (abs_file, anchor))
        
    def open_formula(self,action,widget):        
        self.open_formula_fs.show_all()
        filename = ""
        
        while True:
            result = self.open_formula_fs.run()            
            if result == gtk.RESPONSE_OK:
                filename = self.open_formula_fs.get_filename()
                if self.load_formula(filename):
                    break
            else:
                self.open_formula_fs.hide()
                return
            
        self.open_formula_fs.hide()
        if fc.Compiler.isCFRM.search(filename):
            browser.show(self.window, self.f, browser.OUTER)
        else:
            browser.show(self.window, self.f, browser.FRACTAL)
        
    def open(self,action,widget):        
        self.open_fs.show_all()
        
        while True:
            result = self.open_fs.run()            
            if result == gtk.RESPONSE_OK:
                if self.load(self.open_fs.get_filename()):
                    break
            else:
                break
            
        self.open_fs.hide()

    def load(self,file):
        try:
            self.f.loadFctFile(open(file))
            self.set_filename(file)
            browser.update(self.f.funcFile, self.f.funcName)
            return True
        except Exception, err:
            self.show_error_message(_("Error opening %s") % file,err)
            return False

    def load_formula(self,file):
        try:
            self.compiler.load_formula_file(file)
            browser.update(file)
            return True
        except Exception, err:
            self.show_error_message(_("Error opening %s") % file, err)
            return False

    def check_save_fractal(self):
        "Prompt user to save if necessary. Return whether to quit"
        while not self.f.is_saved():
            d = hig.SaveConfirmationAlert(
                self.display_filename(),-1,self.window)
            
            response = d.run()                
            d.destroy()
            if response == gtk.RESPONSE_ACCEPT:
                self.save(None,None)
            elif response == gtk.RESPONSE_CANCEL:
                return False
            elif response == hig.SaveConfirmationAlert.NOSAVE:
                break
        return True
    
    def about(self,action,widget):
        self.display_help("about")

    def quit(self,action,widget=None):
        self.f.interrupt()
        for f in self.subfracts:
            f.interrupt()
        if not self.check_save_fractal():
            # user doesn't want to quit after all
            return
        
        try:
            preferences.userPrefs.save()
            self.compiler.clear_cache()
        finally:
            gtk.main_quit()


