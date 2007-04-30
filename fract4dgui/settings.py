# GUI for modifying the fractal's settings

import gtk, gobject

import dialog
import browser
import utils
import copy

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
        self.tables = [None,None,None,None]
        self.selected_transform = None
        
        self.create_formula_parameters_page()
        self.create_outer_page()
        self.create_inner_page()
        self.create_transforms_page()
        self.create_general_page()
        self.create_location_page()
        self.create_colors_page()

    def gradarea_mousedown(self, widget, event):
        pass

    def gradarea_clicked(self, widget, event):
        pos = float(event.x) / widget.allocation.width
        i = self.f.get_gradient().get_index_at(pos)
        self.select_segment(i)
        self.redraw()

    def gradarea_mousemoved(self, widget, event):
        pass
    
    def gradarea_realized(self, widget):
        self.gradgc = widget.window.new_gc(fill=gtk.gdk.SOLID)
        return True
        
    def gradarea_expose(self, widget, event):
        #Draw the gradient itself
        r = event.area
        self.redraw_rect(widget, r.x, r.y, r.width, r.height)

    def redraw_rect(self, widget, x, y, w, h):
        # draw the color preview bar
        wwidth = float(widget.allocation.width)
        colorband_height = widget.allocation.height - self.grad_handle_height
        
        colormap = widget.get_colormap()
        grad = self.f.get_gradient()
        for i in xrange(x, x+w):
            pos_in_gradient = float(i)/wwidth
            col = grad.get_color_at(pos_in_gradient)
            gtkcol = colormap.alloc_color(
                int(col[0]*65535),
                int(col[1]*65535),
                int(col[2]*65535),
                True, True)
            
            self.gradgc.set_foreground(gtkcol)
            widget.window.draw_line(
                self.gradgc, i, y, i, min(y+h, colorband_height))

    def redraw(self,*args):
        if self.gradarea.window:
            self.gradarea.window.invalidate_rect(
                gtk.gdk.Rectangle(0, 0,
                                  self.gradarea.allocation.width,
                                  self.gradarea.allocation.height))

        self.inner_solid_button.set_color(
            utils.floatColorFrom256(self.f.solids[1]))
        self.outer_solid_button.set_color(
            utils.floatColorFrom256(self.f.solids[0]))


    def create_colors_table(self):
        gradbox = gtk.VBox()

        browse_button = gtk.Button(_("_Browse..."))

        browse_button.connect("clicked", self.show_browser, browser.GRADIENT)
            
        gradbox.pack_start(browse_button, False, False, 1)
        
        # gradient viewer
        self.grad_handle_height = 8
        
        self.gradarea=gtk.DrawingArea()
        c = utils.get_rgb_colormap()
        self.gradarea.set_colormap(c)        

        self.gradarea.add_events(
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.BUTTON1_MOTION_MASK |
            gtk.gdk.POINTER_MOTION_HINT_MASK |
            gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.KEY_PRESS_MASK |
            gtk.gdk.KEY_RELEASE_MASK
            )

        self.gradarea.set_size_request(256, 96)
        self.gradarea.connect('realize', self.gradarea_realized)
        self.gradarea.connect('expose_event', self.gradarea_expose)
        self.gradarea.connect('button-press-event', self.gradarea_mousedown)
        self.gradarea.connect('button-release-event', self.gradarea_clicked)
        self.gradarea.connect('motion-notify-event', self.gradarea_mousemoved)

        self.f.connect('parameters-changed', self.redraw)
        gradbox.pack_start(self.gradarea, False, False, 1)

        table = gtk.Table(4,4, True)
        table.set_property("column-spacing",2)

        grad = self.f.get_gradient()
        self.left_color_button = utils.ColorButton(
            grad.segments[0].left_color, self.color_changed, True)
        self.tooltips.set_tip(
            self.left_color_button.widget,
            _("Color of segment's left end"))
        
        self.right_color_button = utils.ColorButton(
            grad.segments[0].right_color, self.color_changed, False)
        self.tooltips.set_tip(
            self.right_color_button.widget,
            _("Color of segment's right end"))

        table.attach(gtk.Label("Left Color:"),
                     0,1,0,1)
        table.attach(self.left_color_button.widget,
                     1,2,0,1, gtk.EXPAND | gtk.FILL, gtk.EXPAND)
        table.attach(gtk.Label("Right Color:"),
                     2,3,0,1)
        table.attach(self.right_color_button.widget,
                     3,4,0,1, gtk.EXPAND | gtk.FILL, gtk.EXPAND)

        self.split_button = gtk.Button(_("Split"))
        self.split_button.connect('clicked', self.split)
        table.attach(self.split_button,
                     0,1,1,2, gtk.EXPAND | gtk.FILL, gtk.EXPAND)

        self.remove_button = gtk.Button(_("Remove"))
        self.remove_button.connect('clicked', self.remove)
        table.attach(self.remove_button,
                     1,2,1,2, gtk.EXPAND | gtk.FILL, gtk.EXPAND)

        self.copy_left_button = gtk.Button(_("<Copy"))
        self.copy_left_button.connect('clicked', self.copy_left)
        table.attach(self.copy_left_button,
                     2,3,1,2, gtk.EXPAND | gtk.FILL, gtk.EXPAND)
        
        self.copy_right_button = gtk.Button(_("Copy>"))
        self.copy_right_button.connect('clicked', self.copy_right)
        table.attach(self.copy_right_button,
                     3,4,1,2, gtk.EXPAND | gtk.FILL, gtk.EXPAND)        

        self.inner_solid_button = utils.ColorButton(
            utils.floatColorFrom256(self.f.solids[1]),
            self.solid_color_changed, 1)

        self.outer_solid_button = utils.ColorButton(
            utils.floatColorFrom256(self.f.solids[0]),
            self.solid_color_changed, 0)

        table.attach(gtk.Label("Inner Color:"),
                     0,1,2,3)
        table.attach(self.inner_solid_button.widget,
                     1,2,2,3, gtk.EXPAND | gtk.FILL, gtk.EXPAND)
        table.attach(gtk.Label("Outer Color:"),
                     2,3,2,3)
        table.attach(self.outer_solid_button.widget,
                     3,4,2,3, gtk.EXPAND | gtk.FILL, gtk.EXPAND)

        gradbox.add(table)

        return gradbox

    def copy_left(self,widget):
        i = self.selected_segment
        if i == -1 or i == 0:
            return

        segments = self.f.get_gradient().segments
        segments[i-1].right_color = copy.copy(segments[i].left_color)
        self.f.changed()
        
    def copy_right(self,widget):
        i = self.selected_segment
        if i == -1 or i == len(self.grad.segments)-1:
            return

        segments = self.f.get_gradient().segments
        segments[i+1].left_color = copy.copy(segments[i].right_color)
        self.f.changed()

    def split(self, widget):
        i = self.selected_segment
        if i == -1:
            return
        self.f.get_gradient().add(i)
        self.f.changed()

    def remove(self, widget):
        i = self.selected_segment
        grad = self.f.get_gradient()
        if i == -1 or len(grad.segments)==1:
            return
        grad.remove(i, True)
        if self.selected_segment > 0:
            self.selected_segment -= 1
        self.f.changed()
        
    def solid_color_changed(self, r, g, b, index):
        self.f.set_solid(
            index,
            utils.color256FromFloat(r,g,b, self.f.solids[index]))
        
    def color_changed(self,r,g,b, is_left):
        #print "color changed", r, g, b, is_left
        self.f.get_gradient().set_color(
            self.selected_segment,
            is_left,
            r,g,b)

        self.redraw()

    def select_segment(self,i):
        self.selected_segment = i
        
        if i == -1:
            self.left_color_button.set_color([0.5,0.5,0.5,1])
            self.right_color_button.set_color([0.5,0.5,0.5,1])
        else:
            grad = self.f.get_gradient()
            self.left_color_button.set_color(grad.segments[i].left_color)
            self.right_color_button.set_color(grad.segments[i].right_color)
        # buttons should be sensitive if selection is good
        self.left_color_button.set_sensitive(i!= -1)
        self.right_color_button.set_sensitive(i!= -1)
        self.split_button.set_sensitive(i != -1)
        self.remove_button.set_sensitive(i != -1)
        self.copy_right_button.set_sensitive(i != -1)
        self.copy_left_button.set_sensitive(i != -1)

    def create_colors_page(self):
        table = self.create_colors_table()
        label = gtk.Label(_("_Colors"))
        label.set_use_underline(True)
        self.notebook.append_page(table,label)
        self.select_segment(-1)

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
        self.create_param_entry(table,5,_("XY (_1):"), self.f.XYANGLE)
        self.create_param_entry(table,6,_("XZ (_2):"), self.f.XZANGLE)
        self.create_param_entry(table,7,_("XW (_3):"), self.f.XWANGLE)
        self.create_param_entry(table,8,_("YZ (_4):"), self.f.YZANGLE)
        self.create_param_entry(table,9,_("YW (_5):"), self.f.YWANGLE)
        self.create_param_entry(table,10,_("ZW (_6):"), self.f.ZWANGLE)
        
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

    def add_notebook_page(self,page,text):
        label = gtk.Label(text)
        label.set_use_underline(True)
        self.notebook.append_page(page,label)
        
    def create_outer_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,False)
        vbox.pack_start(table)

        self.create_formula_widget_table(vbox,1)

        self.add_notebook_page(vbox,_("_Outer"))

        cflabel = gtk.Label(_("Colorfunc :"))
        table.attach(cflabel, 0,1,0,1,0,0,2,2)
        label = gtk.Label(self.f.forms[1].funcName)

        def set_label(*args):
            label.set_text(self.f.forms[1].funcName)
            
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

        self.add_notebook_page(vbox, _("_Inner"))

        table.attach(gtk.Label(_("Colorfunc :")), 0,1,0,1,0,0,2,2)
        label = gtk.Label(self.f.forms[2].funcName)

        def set_label(*args):
            label.set_text(self.f.forms[2].funcName)
            
        self.f.connect('parameters-changed',set_label)

        hbox = gtk.HBox(False,1)
        hbox.pack_start(label)
        button = gtk.Button(_("_Browse..."))
        button.set_use_underline(True)
        self.tooltips.set_tip(button,_("Browse available coloring functions"))
        button.connect('clicked', self.show_browser, browser.INNER)
        hbox.pack_start(button)
        table.attach(hbox, 1,2,0,1,gtk.EXPAND | gtk.FILL ,0,2,2) 

    def remove_transform(self,*args):
        if self.selected_transform == None:
            return

        self.f.remove_transform(self.selected_transform)
        
    def create_transforms_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,False)
        vbox.pack_start(table)

        self.transform_store = gtk.ListStore(gobject.TYPE_STRING, object)
        def set_store(*args):
            self.transform_store.clear()
            for transform in self.f.transforms:
                self.transform_store.append((transform.funcName,transform))

        set_store()

        self.f.connect('formula-changed', set_store)

        self.transform_view = gtk.TreeView(self.transform_store)
        self.transform_view.set_headers_visible(False)
        self.transform_view.set_size_request(150,250)
        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn ('_Transforms', renderer, text=0)
        
        self.transform_view.append_column (column)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.transform_view)
        sw.set_shadow_type(gtk.SHADOW_IN)
        table.attach(
            sw, 0, 1, 0, 4,
            0, 0, 2, 2)

        add_button = gtk.Button(None,gtk.STOCK_ADD)
        add_button.connect(
            'clicked', self.show_browser, browser.TRANSFORM)

        table.attach(
            add_button, 1,2,0,1, gtk.EXPAND | gtk.FILL, 0, 2, 2)

        remove_button = gtk.Button(None,gtk.STOCK_REMOVE)
        remove_button.connect(
            'clicked', self.remove_transform)

        table.attach(
            remove_button, 1,2,1,2, gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        selection = self.transform_view.get_selection()
        selection.connect('changed',self.transform_selection_changed,vbox)

        self.add_notebook_page(vbox,_("T_ransforms"))

        self.create_transform_widget_table(vbox)

    def transform_selection_changed(self,selection, parent):
        (model,iter) = selection.get_selected()
        if iter == None:
            self.selected_transform = None
        else:        
            transform = model.get_value(iter,1)
            # this is bogus. How do I get the index into the list in a less
            # stupid way?
            i = 0
            for t in self.f.transforms:
                if t == transform:
                    self.selected_transform = i
                    break
                i += 1

        self.update_transform_parameters(parent)
            
    def create_formula_parameters_page(self):
        vbox = gtk.VBox()
        table = gtk.Table(5,2,False)
        vbox.pack_start(table)

        self.create_formula_widget_table(vbox,0)

        self.add_notebook_page(vbox, _("_Formula"))

        table.attach(gtk.Label(_("Formula :")), 0,1,0,1,0,0,2,2)
        hbox = gtk.HBox(False,1)
        label = gtk.Label(self.f.forms[0].funcName)

        def set_label(*args):
            label.set_text(self.f.forms[0].funcName)
            
        self.f.connect('parameters-changed',set_label)
        
        hbox.pack_start(label)
        button = gtk.Button(_("_Browse..."))
        button.set_use_underline(True)
        self.tooltips.set_tip(button,_("Browse available fractal functions"))
        button.connect('clicked', self.show_browser, browser.FRACTAL)
        hbox.pack_start(button)
        table.attach(hbox, 1,2,0,1,gtk.EXPAND | gtk.FILL ,0,2,2)

    def update_transform_parameters(self, parent, *args):
        widget = self.tables[3] 
        if widget != None and widget.parent != None:
            parent.remove(self.tables[3])

        if self.selected_transform != None:
            self.tables[3] = \
                self.f.populate_formula_settings(
                    self.selected_transform+3,self.tooltips)

            self.tables[3].show_all()
            parent.pack_start(self.tables[3])

    def create_transform_widget_table(self,parent):
        self.tables[3] = None
                    
        self.update_transform_parameters(parent)

        def update_all_widgets(*args):
            if not self.tables[3]:
                return
            for widget in self.tables[3].get_children():
                update_function = widget.get_data("update_function")
                if update_function != None:
                    update_function()
                    
        self.f.connect(
            'formula-changed', self.update_transform_parameters, parent)
        self.f.connect('parameters-changed', update_all_widgets)
        
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
        
