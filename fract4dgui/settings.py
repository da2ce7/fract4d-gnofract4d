# GUI for modifying the fractal's settings

import gtk

import dialog
import browser
import utils

def show_settings(parent,alt_parent, f,dialog_mode):
    SettingsDialog.show(parent,alt_parent, f,dialog_mode)

class SettingsDialog(dialog.T):
    def show(parent, alt_parent, f,dialog_mode):
        dialog.T.reveal(SettingsDialog,dialog_mode, parent, alt_parent, f)
            
    show = staticmethod(show)
    
    def __init__(self, main_window, f):
        dialog.T.__init__(
            self,
            _("Fractal Settings"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.main_window = main_window
        self.f = f
        self.tooltips = gtk.Tooltips()
        self.notebook = gtk.Notebook()
        self.controls = gtk.VBox()
        self.controls.add(self.notebook)
        self.vbox.add(self.controls)
        self.tables = [None,None,None]
        
        self.create_formula_parameters_page()
        self.create_outer_page()
        self.create_inner_page()
        self.create_general_page()
        self.create_location_page()
        self.create_angle_page()
        
    def create_location_page(self):
        table = self.create_location_table()
        label = gtk.Label(_("_Location"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)
        
    def create_location_table(self):
        table = gtk.Table(5,2,False)
        self.create_param_entry(table,0,_("_X :"), self.f.XCENTER)
        self.create_param_entry(table,1,_("_Y :"), self.f.YCENTER)
        self.create_param_entry(table,2,_("_Z :"), self.f.ZCENTER)
        self.create_param_entry(table,3,_("_W :"), self.f.WCENTER)
        self.create_param_entry(table,4,_("_Size :"), self.f.MAGNITUDE)
        return table
    
    def create_general_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label(_("_General"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)
        yflip_widget = self.create_yflip_widget()
        table.attach(yflip_widget,0,2,0,1, gtk.EXPAND | gtk.FILL, 0, 2, 2)

        periodicity_widget = self.create_periodicity_widget()
        table.attach(periodicity_widget,0,2,1,2,
                     gtk.EXPAND | gtk.FILL, 0, 2, 2)

    def create_angle_page(self):
        table = gtk.Table(5,2,False)
        label = gtk.Label("_Angles")
        label.set_use_underline(True)
        self.notebook.append_page(table,label)
        self.create_param_entry(table,0,_("XY (_1):"), self.f.XYANGLE)
        self.create_param_entry(table,1,_("XZ (_2):"), self.f.XZANGLE)
        self.create_param_entry(table,2,_("XW (_3):"), self.f.XWANGLE)
        self.create_param_entry(table,3,_("YZ (_4):"), self.f.YZANGLE)
        self.create_param_entry(table,4,_("YW (_5):"), self.f.YWANGLE)
        self.create_param_entry(table,5,_("ZW (_6):"), self.f.ZWANGLE)

    def create_yflip_widget(self):
        widget = gtk.CheckButton(_("Flip Y Axis"))
        widget.set_use_underline(True)
        self.tooltips.set_tip(
            widget,
            _("If set, Y axis increases down the screen, otherwise up the screen"))
        
        def set_widget(*args):
            widget.set_active(self.f.yflip)

        def set_fractal(*args):
            self.f.set_yflip(widget.get_active())

        set_widget()
        self.f.connect('parameters-changed',set_widget)
        widget.connect('toggled',set_fractal)

        return widget

    def create_periodicity_widget(self):
        widget = gtk.CheckButton(_("Periodicity Checking"))
        widget.set_use_underline(True)
        self.tooltips.set_tip(
            widget,
            _("Try to speed up calculations by looking for loops. Can cause incorrect images with some functions, though."))
        
        def set_widget(*args):
            widget.set_active(self.f.periodicity)

        def set_fractal(*args):
            self.f.set_periodicity(widget.get_active())

        set_widget()
        self.f.connect('parameters-changed',set_widget)
        widget.connect('toggled',set_fractal)

        return widget

    def create_outer_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,False)
        vbox.pack_start(table)

        self.create_formula_widget_table(vbox,1)
        
        label = gtk.Label("_Outer")
        label.set_use_underline(True)
        self.notebook.append_page(vbox,label)

        cflabel = gtk.Label(_("Colorfunc :"))
        table.attach(cflabel, 0,1,0,1,0,0,2,2)
        label = gtk.Label(self.f.cfunc_names[0])

        def set_label(*args):
            label.set_text(self.f.cfunc_names[0])
            
        self.f.connect('parameters-changed',set_label)

        hbox = gtk.HBox(False,1)
        hbox.pack_start(label)
        button = gtk.Button(_("_Browse..."))
        self.tooltips.set_tip(button,_("Browse available coloring functions"))
        button.set_use_underline(True)
        button.connect('clicked', self.show_browser, browser.OUTER)
        hbox.pack_start(button)
        table.attach(hbox, 1,2,0,1,gtk.EXPAND | gtk.FILL ,0,2,2)
        
    def create_inner_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,False)
        vbox.pack_start(table)

        self.create_formula_widget_table(vbox,2)
        
        label = gtk.Label(_("_Inner"))
        label.set_use_underline(True)
        self.notebook.append_page(vbox,label)

        table.attach(gtk.Label(_("Colorfunc :")), 0,1,0,1,0,0,2,2)
        label = gtk.Label(self.f.cfunc_names[1])

        def set_label(*args):
            label.set_text(self.f.cfunc_names[1])
            
        self.f.connect('parameters-changed',set_label)

        hbox = gtk.HBox(False,1)
        hbox.pack_start(label)
        button = gtk.Button(_("_Browse..."))
        button.set_use_underline(True)
        self.tooltips.set_tip(button,_("Browse available coloring functions"))
        button.connect('clicked', self.show_browser, browser.INNER)
        hbox.pack_start(button)
        table.attach(hbox, 1,2,0,1,gtk.EXPAND | gtk.FILL ,0,2,2) 

    def create_formula_parameters_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,False)
        vbox.pack_start(table)

        self.create_formula_widget_table(vbox,0)
        
        pagelabel = gtk.Label(_("_Formula"))
        pagelabel.set_use_underline(True)
        self.notebook.append_page(vbox,pagelabel)

        table.attach(gtk.Label(_("Formula :")), 0,1,0,1,0,0,2,2)
        hbox = gtk.HBox(False,1)
        label = gtk.Label(self.f.funcName)

        def set_label(*args):
            label.set_text(self.f.funcName)
            
        self.f.connect('parameters-changed',set_label)
        
        hbox.pack_start(label)
        button = gtk.Button(_("_Browse..."))
        button.set_use_underline(True)
        self.tooltips.set_tip(button,_("Browse available fractal functions"))
        button.connect('clicked', self.show_browser, browser.FRACTAL)
        hbox.pack_start(button)
        table.attach(hbox, 1,2,0,1,gtk.EXPAND | gtk.FILL ,0,2,2)

    def create_formula_widget_table(self,parent,param_type): 
        self.tables[param_type] = None
        
        def update_formula_parameters(*args):
            widget = self.tables[param_type] 
            if widget != None and widget.parent != None:
                parent.remove(self.tables[param_type])

            self.tables[param_type] = \
                self.f.populate_formula_settings(param_type,self.tooltips)
            
            self.tables[param_type].show_all()
            parent.pack_start(self.tables[param_type])
            
        update_formula_parameters()

        # weird hack. We need to change the set of widgets when
        # the formula changes and change the values of the widgets
        # when the parameters change. When I connected the widgets
        # directly to the fractal's parameters-changed signal they
        # would still get signalled even after they were obsolete.
        # This works around that problem
        def update_all_widgets(*args):
            for widget in self.tables[param_type].get_children():
                update_function = widget.get_data("update_function")
                if update_function != None:
                    update_function()
                    
        self.f.connect('formula-changed', update_formula_parameters)
        self.f.connect('parameters-changed', update_all_widgets)
        
    def show_browser(self,button,type):
        browser.show(self.main_window, self.f, type)
        
    def create_param_entry(self,table, row, text, param):
        label = gtk.Label(text)
        label.set_use_underline(True)
        
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label,0,1,row,row+1,0,0,2,2)
        
        entry = gtk.Entry()
        entry.set_activates_default(True)
        table.attach(entry,1,2,row,row+1,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        label.set_mnemonic_widget(entry)
        
        def set_entry(f):
            try:
                current = float(entry.get_text())
                if current != f.get_param(param):
                    entry.set_text("%.17f" % f.get_param(param))
            except ValueError, err:
                # current was set to something that isn't a float
                entry.set_text("%.17f" % f.get_param(param))

        def set_fractal(*args):
            try:
                self.f.set_param(param,entry.get_text())
            except Exception, exn:
                print exn
            return False
        
        set_entry(self.f)
        self.f.connect('parameters-changed', set_entry)
        entry.connect('focus-out-event', set_fractal)
        
