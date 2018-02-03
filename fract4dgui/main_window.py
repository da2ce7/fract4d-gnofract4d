# main window

import sys
import os
import signal
import copy
import math
import re
import urllib.request, urllib.parse, urllib.error

from gi.repository import Gdk, Gtk

# If we haven't been installed (we're running from the dir we 
# were unpacked in) this is where fract4d is.

from fract4d import fractal,fc,fract4dc,image, fracttypes, fractconfig


from . import gtkfractal, model, preferences, autozoom, settings, toolbar
from . import undo, browser, fourway, angle, utils, hig, ignore_info, painter
from . import icons, renderqueue, director

re_ends_with_num = re.compile(r'\d+\Z')
re_cleanup = re.compile(r'[\s\(\)]+')

class MainWindow:
    def __init__(self, extra_paths=[]):
        self.quit_when_done =False
        self.save_filename = None
        self.compress_saves = True
        self.f = None
        self.use_preview = True

        self.four_d_sensitives = []
        # window widget

        self.set_icon()
        
        self.window = Gtk.Window()
        self.window.set_default_size(900,700)
        self.window.connect('delete-event', self.quit)

        # keyboard handling
        self.keymap = {
            Gdk.KEY_Left : self.on_key_left,
            Gdk.KEY_Right : self.on_key_right,
            Gdk.KEY_Up : self.on_key_up,
            Gdk.KEY_Down : self.on_key_down,
            Gdk.KEY_Escape : self.on_key_escape
            }

        self.accelgroup = Gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)
        self.window.connect('key-release-event', self.on_key_release)

        # create fractal compiler and load standard formula and
        # coloring algorithm files
        self.compiler = fc.instance

        for path in extra_paths:
            self.compiler.add_func_path(path)

        self.recent_files = preferences.userPrefs.get_list("recent_files")
        
        self.vbox = Gtk.VBox()
        self.window.add(self.vbox)
        
        self.f = gtkfractal.T(self.compiler,self)            
        self.f.freeze() # create frozen - main prog will thaw us
        self.create_subfracts(self.f)
        
        self.set_filename(None)
        
        try:
            # try to make default image more interesting
            self.f.set_cmap(fractconfig.instance.find_resource(
                "basic.map",
                "maps",
                "maps"))
        except Exception as ex:
            #print ex
            pass
            
        self.model = model.Model(self.f)

        preferences.userPrefs.connect(
            'image-preferences-changed',
            self.on_prefs_changed)

        browser.update(self.f.forms[0].funcFile, self.f.forms[0].funcName)
            
        self.create_ui()
        self.create_toolbar()
        self.create_fractal(self.f)
        self.create_status_bar()

        # create these properly later to avoid 'end from FAM server connection' messages
        self.saveas_fs = None
        self.saveimage_fs = None
        self.hires_image_fs = None
        self.open_fs = None        
        
        self.window.show_all()

        self.update_subfract_visibility(False)
        self.populate_warpmenu(self.f)
        self.update_recent_file_menu()
        
        self.update_image_prefs(preferences.userPrefs)
        
        self.statuses = [ _("Done"),
                          _("Calculating"),
                          _("Deepening (%d iterations)"),
                          _("Antialiasing"),
                          _("Paused"),
                          _("Reducing Periodicity Tolerance")]

        self.f.set_saved(True)

    def create_rtd_widgets(self):
        table = Gtk.Table(2,3,False)
        table.width = width = Gtk.Entry()
        table.height = height = Gtk.Entry()
        width.set_text("2048")
        height.set_text("1536")
        wlabel = Gtk.Label(label=_("Width:"))
        hlabel = Gtk.Label(label=_("Height:"))
        table.attach(
            wlabel,
            0, 1, 0, 1,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            1,1)
        table.attach(
            hlabel,
            0, 1, 1, 2,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            1,1)
        table.attach(
            width,
            1, 2, 0, 1,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            1,1)
        table.attach(
            height,
            1, 2, 1, 2,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            1,1)        
        return table
    
    def get_file_save_chooser(self, title, parent, patterns=[]):
        chooser = Gtk.FileChooserDialog(
            title, parent, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        filter = Gtk.FileFilter()
        for pattern in patterns:
            filter.add_pattern(pattern)

        chooser.set_filter(filter)

        return chooser

    def get_filter(self,name,patterns):
        filter = Gtk.FileFilter()
        filter.set_name(name)
        for pattern in patterns:
            filter.add_pattern(pattern)
        return filter

    def add_filters(self,chooser):
        param_patterns = [ "*.fct" ]
        param_filter = self.get_filter(
            _("Parameter Files"), param_patterns)

        chooser.add_filter(param_filter)

        formula_patterns = ["*.frm", "*.ufm", "*.ucl", "*.cfrm", "*.uxf"]
        formula_filter = self.get_filter(            
            _("Formula Files"), formula_patterns)
        chooser.add_filter(formula_filter)

        gradient_patterns = ["*.map", "*.ggr", "*.ugr", "*.cs", "*.pal"]
        gradient_filter = self.get_filter(
            _("Gradient Files"), gradient_patterns)
        chooser.add_filter(gradient_filter)

        all_filter = self.get_filter(
            _("All Gnofract 4D Files"), 
            param_patterns + formula_patterns + gradient_patterns)

        chooser.add_filter(all_filter)

        chooser.set_filter(all_filter)

    def get_file_open_chooser(self, parent):
        chooser = Gtk.FileChooserDialog(
            title, parent, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_OK, Gtk.ResponseType.OK, 
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        self.add_filters(chooser)

        return chooser

    def get_save_as_fs(self):
        if self.saveas_fs == None:
            self.saveas_fs = self.get_file_save_chooser(
                _("Save Parameters"),
                self.window,
                ["*.fct"])
        return self.saveas_fs
    
    def get_save_image_as_fs(self):
        if self.saveimage_fs == None:
            self.saveimage_fs = self.get_file_save_chooser(
                _("Save Image"),
                self.window,
                image.file_matches())
        return self.saveimage_fs

    def get_save_hires_image_as_fs(self):
        if self.hires_image_fs == None:
            self.saveimage_fs = self.get_file_save_chooser(
                _("Save High Resolution Image"),
                self.window,
                image.file_matches())

            rtd_widgets = self.create_rtd_widgets()
            self.saveimage_fs.set_extra_widget(rtd_widgets)

        return self.saveimage_fs
        
    def get_open_fs(self):
        if self.open_fs != None:
            return self.open_fs

        self.open_fs = Gtk.FileChooserDialog(
            _("Open File"), self.window, 
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_OK, Gtk.ResponseType.OK, 
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        self.add_filters(self.open_fs)

        self.open_preview = gtkfractal.Preview(self.compiler)

        def on_update_preview(chooser, preview):
            filename = chooser.get_preview_filename()
            try:
                preview.loadFctFile(open(filename))
                preview.draw_image(False, False)
                active=True
            except Exception as err:
                active=False
            chooser.set_preview_widget_active(active)
                
        self.open_fs.set_preview_widget(self.open_preview.widget)
        self.open_fs.connect(
            'update-preview', on_update_preview, self.open_preview)

        return self.open_fs
    
    def set_icon(self):
        return # can't get this to work
        try:
            Gtk.window_set_default_icon_list([icons.logo.pixbuf])
        except Exception as err:
            print(err)
            # not supported in this pyGtk. Oh well...
            pass
        
    def update_subfract_visibility(self,visible):
        if visible:
            for f in self.subfracts:
                f.widget.show()
            self.weirdbox.show_all()
        else:
            for f in self.subfracts:
                f.widget.hide()
            self.weirdbox.hide()

        self.show_subfracts = visible
        self.update_image_prefs(preferences.userPrefs)
        
    def update_subfracts(self):
        if not self.show_subfracts:
            return

        aa = preferences.userPrefs.getint("display","antialias")
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")

        for f in self.subfracts:
            f.interrupt()
            f.freeze()
            f.set_fractal(self.f.copy_f())
            f.mutate(
                self.weirdness_adjustment.get_value()/100.0,
                self.color_weirdness_adjustment.get_value()/100.0)
            f.thaw()
            f.draw_image(aa,auto_deepen)
            
    def create_subfracts(self,f):
        self.subfracts = [ None ] * 12
        for i in range(12):
            self.subfracts[i] = gtkfractal.SubFract(
                self.compiler,f.width//4,f.height//4)
            self.subfracts[i].set_master(f)
            
    def attach_subfract(self,i,x,y):
        self.ftable.attach(
            self.subfracts[i].widget,
            x, x+1, y, y+1,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            1,1)

    def on_formula_change(self, f):
        is4d = f.is4D()
        for widget in self.four_d_sensitives:
            widget.set_sensitive(is4d)
        self.fourd_actiongroup.set_sensitive(is4d)

    def create_fractal(self,f):
        self.swindow = Gtk.ScrolledWindow()
        self.swindow.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        
        f.connect('parameters-changed', self.on_fractal_change)
        f.connect('formula-changed', self.on_formula_change)
        
        #self.swindow.set_size_request(640+8,400+8)

        self.fixed = Gtk.Fixed()
        self.ftable = Gtk.Table(4,4,False)
        self.fixed.put(self.ftable,0,0)
        self.ftable.attach(
            f.widget,
            1,3,1,3,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
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
        self.swindow.get_child().set_shadow_type(Gtk.ShadowType.NONE)
                
        f.connect('progress_changed', self.progress_changed)
        f.connect('status_changed',self.status_changed)
        f.connect('stats-changed', self.stats_changed)

        hbox = Gtk.HBox()
        hbox.pack_start(self.swindow, True, True, 0)
        self.control_box = Gtk.VBox()
        hbox.pack_start(self.control_box, False, False, 0)
        self.vbox.pack_start(hbox, True, True, 0)

    def draw(self):        
        nt = preferences.userPrefs.getint("general","threads") 
        self.f.set_nthreads(nt)

        self.f.draw_image()
        
    def update_compiler_prefs(self,prefs):
        # update compiler
        self.compiler.update_from_prefs(prefs)
        
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
            
        self.f.set_antialias(
            prefs.getint("display","antialias"))
        self.f.set_auto_deepen(
            prefs.getboolean("display","autodeepen"))
        self.f.set_auto_tolerance(
            prefs.getboolean("display","autotolerance"))

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

    def base_filename(self, extension):
        if self.filename == None:
            base_name = self.f.get_func_name()
            base_name = re_cleanup.sub("_", base_name) + extension
        else:
            base_name = self.filename
        return base_name
    
    def default_save_filename(self,extension=".fct"):
        base_name = self.base_filename(extension)

        # need to gather a filename
        (base,ext) = os.path.splitext(base_name)
        base = re_ends_with_num.sub("",base)

        save_filename = base + extension
        i = 2
        while True:
            if not os.path.exists(save_filename):
                break
            save_filename = base + ("%03d" % i) + extension
            i += 1
        return save_filename

    def default_image_filename(self,extension=".png"):
        base_name = self.base_filename(extension)

        return self.image_save_filename(base_name)
    
    def image_save_filename(self,fctname,extension=".png"):
        (base,ext) = os.path.splitext(fctname)
        return base + extension
    
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
        if state & Gdk.ModifierType.SHIFT_MASK:
            axis = 2
        if state & Gdk.ModifierType.CONTROL_MASK:
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
        if isinstance(current_widget, Gtk.Entry) or isinstance(current_widget,Gtk.TextView):
            # otherwise we steal cursor motion through entry
            return
        fn = self.keymap.get(event.keyval)
        if fn:
            fn(event.get_state())
        elif not self.menubar.get_property("visible"):
            self.menubar.emit("key-release-event",event)
            
    def progress_changed(self,f,progress):
        self.bar.set_fraction(progress/100.0)

    def stats_changed(self, f, stats):
        self.bar.set_tooltip_text(stats.show())

    def status_changed(self,f,status):
        if status == 2:
            # deepening
            text = self.statuses[status] % self.f.maxiter
        elif status == 0:
            # done
            text = self.statuses[status] 
            if self.save_filename:
                self.save_image_file(self.save_filename)
            if self.quit_when_done:
                self.f.set_saved(True)
                self.quit(None,None)

        else:
            text = self.statuses[status]

        self.bar.set_text(text)

    def get_hires_dimensions(self,fs):
        table = fs.get_extra_widget()
        width = int(table.width.get_text())
        height = int(table.height.get_text())
        return (width, height)
    
    def save_hires_image(self, action):
        """Add the current fractal to the render queue."""
        save_filename = self.default_image_filename(".png")

        fs = self.get_save_hires_image_as_fs()
        utils.set_file_chooser_filename(fs,save_filename)
        fs.show_all()
        
        name = None
        while True:
            result = fs.run()
            if result == Gtk.ResponseType.OK:
                name = fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                (w,h) = self.get_hires_dimensions(fs)
                self.add_to_queue(name,w,h)
                break
        fs.hide()
    
    def get_all_actions(self):
        return self.get_toggle_actions() + \
            self.get_main_actions() + \
            self.get_fourd_actions()

    def get_toggle_actions(self):
        return [
            ('ToolsExplorerAction', icons.explorer.stock_name, _('_Explorer'),
             '<control>E', _('Create random fractals similar to this one'), 
             self.toggle_explorer)
            ]
            
    def get_main_actions(self):
        return [
            ('FileMenuAction', None, _('_File')),
            ('FileOpenAction', Gtk.STOCK_OPEN, _('_Open...'), 
             None, _('Open a Parameter or Formula File'), self.open),
            ('FileSaveAction', Gtk.STOCK_SAVE, None, 
             None, _("Save current parameters"), self.save),
            ('FileSaveAsAction', Gtk.STOCK_SAVE_AS, None,
             '<control><shift>S', _("Save current parameters in a new location"), self.saveas),
            ('FileSaveImageAction', None, _('Save Current _Image'),
             '<control>I', _('Save the current image'), self.save_image),
            ('FileSaveHighResImageAction', None, _('Save _High-Res Image...'),
             '<control><shift>I', _('Save a higher-resolution version of the current image'), 
             self.save_hires_image),

            # FIXME: UI merging would seem to be better, but it's a bit bloody complicated
            # There's a special widget in pygtk 2.10 for this but that's too new, not all
            # interesting distributions have it
            ('FileRecent1Action', None, _('_1'), None, None, 
             lambda *args : self.load_recent_file(1)),
            ('FileRecent2Action', None, _('_2'), None, None, 
             lambda *args : self.load_recent_file(2)),
            ('FileRecent3Action', None, _('_3'), None, None, 
             lambda *args : self.load_recent_file(3)),
            ('FileRecent4Action', None, _('_4'), None, None, 
             lambda *args : self.load_recent_file(4)),

            ('FileQuitAction', Gtk.STOCK_QUIT, None, 
             None, _('Quit'), self.quit),

            ('EditMenuAction', None, _('_Edit')),                
            ('EditFractalSettingsAction', Gtk.STOCK_PROPERTIES, _('_Fractal Settings...'),
             '<control>F', _('Edit the fractal\'s settings'), self.settings),
            ('EditPreferencesAction', Gtk.STOCK_PREFERENCES, None,
             None, _('Edit user preferences'), self.preferences),
            ('EditUndoAction', Gtk.STOCK_UNDO, None,
             '<control>Z', _('Undo the last command'), self.undo),
            ('EditRedoAction', Gtk.STOCK_REDO, None,
             '<control><shift>Z', _('Redo the last undone command'), self.redo),
            ('EditResetAction', Gtk.STOCK_HOME,_('_Reset'),
             'Home', _('Reset all parameters to defaults'), self.reset),
            ('EditResetZoomAction', Gtk.STOCK_ZOOM_100, _('Re_set Zoom'),
             '<control>Home', _('Reset magnification'), self.reset_zoom),

            ('ViewMenuAction', None, _('_View')),
            ('ViewFullScreenAction', Gtk.STOCK_FULLSCREEN, _('_Full Screen'),
             'F11', _('Full Screen (press Esc to finish)'), self.full_screen),

            ('ToolsMenuAction', None, _('_Tools')),
            ('ToolsAutozoomAction', icons.autozoom.stock_name, _('_Autozoom'),
             '<control>A', _('Automatically zoom in to interesting regions'), self.autozoom),
            # explorer is a toggle, see above
            ('ToolsBrowserAction', None, _('Formula _Browser'),
             '<control>B', _('Browse available formulas'), self.browser),
            ('ToolsDirectorAction', None, _('_Director'),
             '<control>D', _('Create animations'), self.director),
            ('ToolsRandomizeAction', icons.randomize.stock_name, _('_Randomize Colors'),
             '<control>R', _('Apply a new random color scheme'), self.randomize_colors),
            ('ToolsPainterAction', icons.draw_brush.stock_name, _('_Painter'),
             None, _('Change colors interactively'), self.painter),

            ('HelpMenuAction', None, _('_Help')),
            ('HelpContentsAction', Gtk.STOCK_HELP, _('_Contents'),
             'F1', _('Display manual'), self.contents),
            ('HelpCommandReferenceAction', None, _('Command _Reference'),
             None, _('A list of keyboard and mouse shortcuts'), self.command_reference),
            ('HelpFormulaReferenceAction', None, _('_Formula Reference'),
             None, _('Reference for functions and objects in the formula compiler'), 
             self.formula_reference),
            ('HelpReportBugAction', icons.face_sad.stock_name, _('_Report a Bug'),
             '', _('Report a bug you\'ve found'), self.report_bug),
            ('HelpAboutAction', Gtk.STOCK_ABOUT, _('_About'), 
             None, _('About Gnofract 4D'), self.about)
            ]

    def get_fourd_actions(self):
        return [
            ('PlanesMenuAction', None, _('Planes')),
            ('PlanesXYAction', None, _('_XY (Mandelbrot)'),
             '<control>1', None, self.set_xy_plane),
            ('PlanesZWAction', None, _('_ZW (Julia)'),
             '<control>2', None, self.set_zw_plane),
            ('PlanesXZAction', None, _('_XZ (Oblate)'),
             '<control>3', None, self.set_xz_plane),
            ('PlanesXWAction', None, _('_XW (Parabolic)'),
             '<control>4', None, self.set_xw_plane),
            ('PlanesYZAction', None, _('_ZY (Elliptic)'),
             '<control>5', None, self.set_yz_plane),
            ('PlanesWYAction', None, _('_WY (Rectangular)'),
             '<control>6', None, self.set_wy_plane)
            ]

    def create_ui(self):
        self.manager = Gtk.UIManager()
        accelgroup = self.manager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        main_actiongroup = Gtk.ActionGroup('Gnofract4D')
        self.main_actiongroup = main_actiongroup

        main_actiongroup.add_toggle_actions(self.get_toggle_actions())

        main_actiongroup.add_actions(self.get_main_actions())

        self.manager.insert_action_group(main_actiongroup, 0)

        # actions which are only available if we're in 4D mode
        self.fourd_actiongroup = Gtk.ActionGroup('4D-sensitive widgets')

        self.fourd_actiongroup.add_actions(self.get_fourd_actions())

        self.manager.insert_action_group(self.fourd_actiongroup, 1)

        this_path = os.path.dirname(sys.modules[__name__].__file__)
        ui_location = os.path.join(this_path,"ui.xml")
        self.manager.add_ui_from_file(ui_location)

        self.menubar = self.manager.get_widget('/MenuBar')
        self.vbox.pack_start(self.menubar, False, True, 0)
        
        # this could be done with an actiongroup, but since it already works...
        undo = self.manager.get_widget(_("/MenuBar/EditMenu/EditUndo"))
        self.model.seq.make_undo_sensitive(undo)
        redo = self.manager.get_widget(_("/MenuBar/EditMenu/EditRedo"))
        self.model.seq.make_redo_sensitive(redo)

        self.recent_menuitems = [
            self.manager.get_widget("/MenuBar/FileMenu/Recent1"),
            self.manager.get_widget("/MenuBar/FileMenu/Recent2"),
            self.manager.get_widget("/MenuBar/FileMenu/Recent3"),
            self.manager.get_widget("/MenuBar/FileMenu/Recent4")]


    def director(self,*args):
        """Display the Director (animation) window."""
        director.show(self.window,self.control_box, self.f, True)
        
    def browser(self,*args):
        """Display formula browser."""
        browser.show(self.window,self.f)

    def randomize_colors(self,*args):
        """Create a new random color scheme."""
        self.f.make_random_colors(8)

    def painter(self,*args):
        painter.show(self.window,self.f)

    def add_to_queue(self,name,w,h):
        renderqueue.show(self.window,None,self.f)
        renderqueue.instance.add(self.f.f,name,w,h)
        renderqueue.instance.start()
        
    def toggle_explorer(self, action):
        """Enter (or leave) Explorer mode."""
        self.set_explorer_state(action.get_active())

    def full_screen(self, *args):
        """Show main window full-screen."""
        self.set_full_screen(True)

    def on_key_escape(self, state):
        self.set_full_screen(False)
        
    def set_full_screen(self, is_full):
        if not hasattr(self.window, "fullscreen"):
            self.show_warning(
                _("Sorry, your version of PyGTK does not support full screen display"))
            return
        
        if is_full:
            self.window.fullscreen()
            self.window.set_decorated(False)
            self.menubar.hide()
            self.toolbar.hide()
            self.bar.hide()
            self.swindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
            self.window.move(0, 0)

            screen = self.window.get_screen()
            preferences.userPrefs.set_size(
                screen.get_width(),
                screen.get_height())
            
            # TODO: may be useful for 'desktop mode' one day
            #self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
            #self.window.set_keep_below(True)
        else:
            self.window.set_decorated(True)
            self.swindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            self.menubar.show()
            self.toolbar.show()
            self.bar.show()
            self.window.unfullscreen()
            
    def create_status_bar(self):
        self.bar = Gtk.ProgressBar()
        self.bar.set_show_text(True)
        self.vbox.pack_end(self.bar, False, True, 0)

    def update_preview(self,f,flip2julia=False):
        if self.use_preview:
            self.preview.set_fractal(f.copy_f())
            self.draw_preview()

    def update_preview_on_pointer(self,f,button, x,y):
        if self.use_preview and button == 2:
            self.preview.set_fractal(f.copy_f())
            self.preview.relocate(x,y,1.0)
            self.preview.flip_to_julia()
            self.draw_preview()
        
    def draw_preview(self):
        auto_deepen = preferences.userPrefs.getboolean("display","autodeepen")
        self.preview.draw_image(False,auto_deepen)

    def improve_now(self, widget):
        self.f.improve_quality()

    def create_toolbar(self):
        self.toolbar = toolbar.T()
        self.vbox.pack_start(self.toolbar, expand=False, fill=False, padding=0)
        
        # preview
        self.toolbar.add_space()
        
        self.preview = gtkfractal.Preview(self.compiler)
        self.preview.set_size(48,48)
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
        
        self.add_fourway(
            _("pan"),
            _("Pan around the image"), 0, True)
        self.add_fourway(
            _("warp"),
            _("Mutate the image by moving along the other 2 axes"), 2, True)

        self.add_warpmenu(_("Which parameter is being warped"))
            
        # deepen/resize
        self.toolbar.add_space()
        
        self.toolbar.add_stock(
            icons.improve_now.stock_name,
            _("Double the maximum number of iterations and tighten periodicity. This will fill in some black areas but increase drawing time"),
            self.improve_now)

        res_menu = self.create_resolution_menu()

        self.toolbar.add_widget(
            res_menu,
            _("Resolution"),
            _("Change fractal's resolution"))            

        # undo/redo
        self.toolbar.add_space()

        self.toolbar.add_stock(
            Gtk.STOCK_UNDO,
            _("Undo the last change"),
            self.undo)

        self.model.seq.make_undo_sensitive(self.toolbar.get_children()[-1])
        
        self.toolbar.add_stock(
            Gtk.STOCK_REDO,
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
        
        self.weirdness_adjustment = Gtk.Adjustment(
            20.0, 0.0, 100.0, 5.0, 5.0, 0.0)

        self.weirdness = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, self.weirdness_adjustment)
        self.weirdness.set_size_request(100, 20)
        self.weirdness.set_property("value-pos",Gtk.PositionType.RIGHT)

        self.weirdbox = Gtk.VBox()
        shapebox = Gtk.HBox(False,2)
        shape_label = Gtk.Label(label=_("Shape:"))
        shapebox.pack_start(shape_label, True, True, 0)
        shapebox.pack_start(self.weirdness, True, True, 0)

        self.weirdbox.pack_start(shapebox, True, True, 0)
        
        self.toolbar.add_widget(
            self.weirdbox,
            _("Weirdness"),
            _("How different to make the random mutant fractals"))

        self.color_weirdness_adjustment = Gtk.Adjustment(
            20.0, 0.0, 100.0, 5.0, 5.0, 0.0)

        self.color_weirdness = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, self.color_weirdness_adjustment)
        self.color_weirdness.set_size_request(100, 20)
        self.color_weirdness.set_property("value-pos",Gtk.PositionType.RIGHT)

        colorbox = Gtk.HBox(False,2)
        color_label = Gtk.Label(label=_("Color:"))
        colorbox.pack_start(color_label, True, True, 0)
        colorbox.pack_start(self.color_weirdness, True, True, 0)
        self.weirdbox.pack_start(colorbox, True, True, 0)

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
            (1280, 800), (1280, 960), (1280,1024), 
            (1400, 1050), (1440, 900),
            (1600,1200), (1680, 1050), 
            (1920, 1200), (2560, 1600)]

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
        try:
            self.preview.nudge_param(order, param_type, dx, dy)
        except Exception as err:
            print(param_type)
            print(err)
            raise
        self.draw_preview()
                
    def on_release_fourway(self,widget,dx,dy):
        self.f.nudge(dx/10.0, dy/10.0, widget.axis)


    def populate_warpmenu(self,f):
        params = f.forms[0].params_of_type(fracttypes.Complex, True)
        if params == []:
            self.warpmenu.hide()
        else:
            utils.set_menu_from_list(self.warpmenu, ["None"] + params)
            p = f.warp_param
            if p == None: p = "None"
            utils.set_selected_value(self.warpmenu, p)
            self.warpmenu.show()                

    def add_warpmenu(self,tip):
        self.warpmenu = utils.create_option_menu(["None"])
        
        def update_warp_param(menu, f):
            param = utils.get_selected_value(menu)
            if param == "None":
                param = None

            f.set_warp_param(param)                
            self.on_formula_change(f)
            
        #self.populate_warpmenu(self.f,warpmenu)

        self.f.connect('formula-changed', self.populate_warpmenu)

        self.warpmenu.connect("changed", update_warp_param, self.f)
        
        self.toolbar.add_widget(
            self.warpmenu,
            tip,
            None)
        
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

    def update_recent_files(self, file):
        self.recent_files = preferences.userPrefs.update_list("recent_files",file,4)
        self.update_recent_file_menu()
        
    def update_recent_file_menu(self):
        i = 1
        for menuitem in self.recent_menuitems:
            if i > len(self.recent_files):
                menuitem.hide()
            else:
                filename = self.recent_files[i-1]
                display_name = os.path.basename(filename).replace("_","__")
                menuitem.get_child().set_label("_%d %s" % (i, display_name))
                menuitem.show()
            i += 1

    def load_recent_file(self, file_num, *args):
        self.load(self.recent_files[file_num-1])
        
    def save_file(self,file):
        try:
            comp = preferences.userPrefs.getboolean("general","compress_fct")
            self.f.save(open(file,'w'),compress=comp)
            self.set_filename(file)
            self.update_recent_files(file)
            return True
        except Exception as err:
            self.show_error_message(
                _("Error saving to file %s") % file, err)
            return False

    def save(self,action):
        """Save the current parameters."""
        if self.filename == None:
            self.saveas(action)
        else:
            self.save_file(self.filename)
        
    def saveas(self,action):
        """Save the current parameters into a new file."""
        fs = self.get_save_as_fs()
        save_filename = self.default_save_filename()

        utils.set_file_chooser_filename(fs, save_filename)
        fs.show_all()

        name = None
        while True:
            result = fs.run()
            if result == Gtk.ResponseType.OK:
                name = fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                if self.save_file(name):
                    break

        fs.hide()

    def confirm(self,name):
        'if this file exists, check with user before overwriting it'
        if os.path.exists(name):
            msg = _("File %s already exists. Overwrite?") % name
            d = hig.ConfirmationAlert(
                primary=msg,
                parent=self.window,
                proceed_button=_("Overwrite"))

            response = d.run()                
            d.destroy()
            return response == Gtk.ResponseType.ACCEPT
        else:
            return True

    def show_warning(self,message):
        d = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.WARNING, Gtk.ButtonsType.OK,
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

        d = hig.ErrorAlert(
            primary=message,
            secondary=secondary_message,
            parent=self.window)
        d.run()
        d.destroy()

    def save_image(self,*args):
        """Save the current image to a file."""
        save_filename = self.default_image_filename(".png")

        fs = self.get_save_image_as_fs()
        utils.set_file_chooser_filename(fs,save_filename)
        fs.show_all()
        
        name = None
        while True:
            result = fs.run()
            if result == Gtk.ResponseType.OK:
                name = fs.get_filename()
            else:
                break
            
            if name and self.confirm(name):
                try:
                    self.save_image_file(name)
                    break
                except Exception as err:
                    self.show_error_message(
                        _("Error saving image %s") % name, err)
        fs.hide()

    def save_image_file(self,filename):
        try:
            self.f.save_image(filename)
            return True
        except Exception as err:
            self.show_error_message(
                _("Error saving image to file %s") % filename, err)
            return False
        
    def settings(self,*args):
        """Show fractal settings controls."""
        settings.show_settings(self.window, self.control_box, self.f, False)
        
    def preferences(self,*args):
        """Change current preferences."""
        preferences.show_preferences(self.window, self.f)
        
    def undo(self,*args):
        """Undo the last operation."""
        self.model.undo()
        
    def redo(self,*args):
        """Redo an operation after undoing it."""
        self.model.redo()
        
    def reset(self,*args):
        """Reset all numeric parameters to their defaults."""
        self.f.reset()

    def reset_zoom(self,*args):
        """Reset zoom to default level."""
        self.f.reset_zoom()

    def set_xy_plane(self,*args):
        """Reset rotation to show the XY (Mandelbrot) plane."""
        # left = +x, down = +y
        self.f.set_plane(None,None)

    def set_xz_plane(self,*args):
        """Reset rotation to show the XZ (Oblate) plane."""
        # left = +x, down = +z
        self.f.set_plane(None, self.f.YZANGLE)

    def set_xw_plane(self,*args):
        """Reset rotation to show the XW (Parabolic) plane."""
        # left =+x, down = +w
        self.f.set_plane(None,self.f.YWANGLE)

    def set_zw_plane(self,*args):
        """Reset rotation to show the ZW (Julia) plane."""
        # left = +z, down = +w
        self.f.set_plane(self.f.XZANGLE, self.f.YWANGLE)
        
    def set_yz_plane(self,*args):
        """Reset rotation to show the YZ (Elliptic) plane."""
        # left = +z, down = +y
        self.f.set_plane(self.f.XZANGLE, None)

    def set_wy_plane(self,*args):
        """Reset rotation to show the WY (Rectangular) plane."""
        # left =+w, down = +y
        self.f.set_plane(self.f.XWANGLE, None)

    def autozoom(self,*args):
        """Display AutoZoom dialog."""
        autozoom.show_autozoom(self.window, self.f)

    def contents(self,*args):
        """Show help file contents page."""
        self.display_help()

    def command_reference(self, *args):
        self.display_help("cmdref")

    def formula_reference(self, *args):
        self.display_help("formref")

    def report_bug(self, *args):
        url="https://github.com/edyoung/gnofract4d/issues"
        utils.launch_browser(
            preferences.userPrefs,
            url,
            self.window)
        
    def display_help(self,section=None):
        # if yelp is available use docbook XML; otherwise fall back to HTML
        yelp_path = utils.find_in_path("yelp")
        if yelp_path:
            base_help_file = "gnofract4d-manual.xml"
        else:
            base_help_file = "gnofract4d-manual.html"
            
        loc = "C" # FIXME

        # look locally first to support run-before-install
        local_dir = "doc/gnofract4d-manual/%s/" % loc
        install_dir = "../../share/gnome/help/gnofract4d/%s/" % loc

        helpfile = fractconfig.instance.find_resource(
            base_help_file, local_dir, install_dir)
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
        
        if yelp_path:
            os.system("yelp ghelp://%s%s >/dev/null 2>&1 &" % (abs_file, anchor))
        else:
            url="file://%s%s" % (abs_file, anchor)
            utils.launch_browser(
                preferences.userPrefs,
                url,
                self.window)
            
        
    def open(self,action):
        """Open a parameter or formula file."""
        fs = self.get_open_fs()
        fs.show_all()
        
        while True:
            result = fs.run()            
            if result == Gtk.ResponseType.OK:
                if self.load(fs.get_filename()):
                    break
            else:
                break
            
        fs.hide()

    def load(self,file):
        try:
            if fc.FormulaTypes.isFormula(file):
                self.load_formula(file)
                return True
            self.f.loadFctFile(open(file))
            self.update_recent_files(file)
            self.set_filename(file)
            browser.update(self.f.forms[0].funcFile, self.f.forms[0].funcName)
            return True
        except Exception as err:
            self.show_error_message(_("Error opening %s") % file,err)
            return False

    def load_formula(self,file):
        try:
            self.compiler.load_formula_file(file)
            type = browser.guess_type(file)
            browser.set_type(type)
            browser.update(file)
            browser.show(self.window, self.f, type)

            return True
        except Exception as err:
            self.show_error_message(_("Error opening %s") % file, err)
            return False

    def check_save_fractal(self):
        "Prompt user to save if necessary. Return whether to quit"        
        while not self.f.is_saved():
            d = hig.SaveConfirmationAlert(
                document_name=self.display_filename(),
                parent=self.window)

            response = d.run()                
            d.destroy()
            if response == Gtk.ResponseType.ACCEPT:
                self.save(None)
            elif response == Gtk.ResponseType.CANCEL:
                return False
            elif response == hig.SaveConfirmationAlert.NOSAVE:
                break

        while not renderqueue.instance.empty():
            d = hig.ConfirmationAlert(
                primary=_("Render queue still processing."),
                secondary=_("If you proceed, queued images will not be saved"),
                proceed_button=_("Close anyway"))
                
            response = d.run()                
            d.destroy()
            if response == Gtk.ResponseType.ACCEPT:
                break
            elif response == Gtk.ResponseType.CANCEL:
                return False
            else:
                break
        return True
    
    def about(self,*args):
        self.display_help("about")

    def quit(self,action,widget=None):
        """Quit Gnofract 4D."""
        self.f.interrupt()
        for f in self.subfracts:
            f.interrupt()
        if not self.check_save_fractal():
            # user doesn't want to quit after all
            return True
        
        try:
            preferences.userPrefs.save()
            del self.f
            for f in self.subfracts:
                del f
            self.compiler.clear_cache()
        finally:
            Gtk.main_quit()
            if 'win' == sys.platform[:3]:
                exit(0);
#            return False

    def apply_options(self,opts):
        "Deal with opts gathered from cmd-line"
        width = opts.width or preferences.userPrefs.getint("display","width")
        height = opts.height or preferences.userPrefs.getint("display","height")

        self.quit_when_done = opts.quit_when_done
        self.save_filename = opts.save_filename
        self.use_preview = opts.preview

        for path in opts.extra_paths:
            self.compiler.add_func_path(path)

        if len(opts.args) > 0:
            self.load(opts.args[0])

        self.f.apply_options(opts)
        self.update_preview(self.f)

        if opts.trace:
            self.f.set_compiler_option("trace", opts.trace)
            self.f.compile()

        if opts.tracez:
            self.f.set_compiler_option("tracez", opts.tracez)
            self.f.compile()

        if opts.explore:
            self.set_explorer_state(True)

        self.f.set_size(width,height)
