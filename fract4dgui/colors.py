# GUI and backend for colormaps

import os
import sys
import copy

import gtk
import gobject

import dialog
import utils
import hig

from fract4d import gradient, fractal

_color_model = None

def show_colors(parent,f):
    ColorDialog.show(parent,f)

def _get_model():
    global _color_model
    if not _color_model:
        _color_model = ColorModel()
    return _color_model

def maps():
    return _get_model().maps

class ColorModel:
    def __init__(self):
        self.maps = {}
        self.populate_file_list()
        
    def add_directory(self,dirname):
        if not os.path.isdir(dirname):
            return

        files = os.listdir(dirname)
        for f in files:
            if not os.path.isfile:
                continue
            absfile = os.path.join(dirname,f)
            (name,ext) = os.path.splitext(absfile)
            if self.maps.get(f):
                continue # avoid duplicates
            self.maps[f] = absfile
                
    def populate_file_list(self):
        self.add_directory("maps")
        self.add_directory(
            os.path.join(sys.exec_prefix,"share/maps/gnofract4d"))

        # find gimp gradient files
        gimp_dir = os.path.join(sys.exec_prefix,"share/gimp/")
        if os.path.isdir(gimp_dir):
            for gimp_ver in os.listdir(gimp_dir):
                self.add_directory(
                    os.path.join(gimp_dir, gimp_ver, "gradients"))
                    
def stricmp(a,b):
    return cmp(a.lower(),b.lower())

class ColorDialog(dialog.T):
    RESPONSE_REFRESH = 1
    def __init__(self,main_window,f):
        global userPrefs
        dialog.T.__init__(
            self,
            _("Gradient Editor"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_REFRESH, ColorDialog.RESPONSE_REFRESH,
             gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
             gtk.STOCK_OK, gtk.RESPONSE_OK,
             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.set_size_request(500,300)
        
        self.f = f
        self.fudge_factor = 3
        self.update_gradient()
        
        self.model = _get_model()
        sw = self.create_map_file_list()
        gradbox = self.create_editor()
        self.select_segment(-1)
                
        hbox = gtk.HBox()
        hbox.pack_start(sw)
        hbox.pack_start(gradbox)
        self.vbox.add(hbox)
        self.treeview.get_selection().unselect_all()

    def update_gradient(self):
        self.grad= copy.copy(self.f.gradient)
        self.solids = copy.copy(self.f.solids)
        
    def copy_left(self,widget):
        i = self.selected_segment
        if i == -1 or i == 0:
            return

        self.grad.segments[i-1].right_color = copy.copy(self.grad.segments[i].left_color)
        self.redraw()
        
    def copy_right(self,widget):
        i = self.selected_segment
        if i == -1 or i == len(self.grad.segments)-1:
            return

        self.grad.segments[i+1].left_color = copy.copy(self.grad.segments[i].right_color)
        self.redraw()

    def split(self, widget):
        i = self.selected_segment
        if i == -1:
            return
        self.grad.add(i)
        self.redraw()

    def remove(self, widget):
        i = self.selected_segment
        if i == -1 or len(self.grad.segments)==1:
            return
        self.grad.remove(i, True)
        if self.selected_segment > 0:
            self.selected_segment -= 1
        self.redraw()
        
    def create_editor(self):
        # a bunch of widgets to edit the current gradient
        gradbox = gtk.VBox()
        #gradient preview
        self.grad_handle_height = 8
        
        self.gradarea=gtk.DrawingArea()
        c = utils.get_rgb_colormap()
        self.gradarea.set_colormap(c)        

        self.tooltips = gtk.Tooltips()
        self.gradarea.add_events(
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.BUTTON1_MOTION_MASK |
            gtk.gdk.POINTER_MOTION_HINT_MASK |
            gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.KEY_PRESS_MASK |
            gtk.gdk.KEY_RELEASE_MASK
            )

        self.gradarea.set_size_request(256, 64)
        self.gradarea.connect('realize', self.gradarea_realized)
        self.gradarea.connect('expose_event', self.gradarea_expose)
        self.gradarea.connect('button-press-event', self.gradarea_mousedown)
        self.gradarea.connect('button-release-event', self.gradarea_clicked)
        self.gradarea.connect('motion-notify-event', self.gradarea_mousemoved)

        gradbox.add(self.gradarea)

        table = gtk.Table(4,4, True)
        table.set_property("column-spacing",2)
        
        self.left_color_button = utils.ColorButton(
            self.grad.segments[0].left_color, self.color_changed, True)
        self.tooltips.set_tip(
            self.left_color_button.widget,
            _("Color of segment's left end"))
        
        self.right_color_button = utils.ColorButton(
            self.grad.segments[0].right_color, self.color_changed, False)
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
            utils.floatColorFrom256(self.solids[1]),
            self.solid_color_changed, 1)

        self.outer_solid_button = utils.ColorButton(
            utils.floatColorFrom256(self.solids[0]),
            self.solid_color_changed, 0)

        table.attach(gtk.Label("Inner Color:"),
                     0,1,2,3)
        table.attach(self.inner_solid_button.widget,
                     1,2,2,3, gtk.EXPAND | gtk.FILL, gtk.EXPAND)
        table.attach(gtk.Label("Outer Color:"),
                     2,3,2,3)
        table.attach(self.outer_solid_button.widget,
                     3,4,2,3, gtk.EXPAND | gtk.FILL, gtk.EXPAND)

        table.attach(gtk.Label("Simplify by:"),
                     0,1,3,4)

        self.fudge_spinbutton = gtk.SpinButton()
        self.fudge_spinbutton.set_range(0,20)
        self.fudge_spinbutton.set_value(self.fudge_factor)
        self.fudge_spinbutton.set_increments(0.5,5)
        table.attach(self.fudge_spinbutton,
                     1,2,3,4)

        self.fudge_spinbutton.connect("value-changed", self.fudge_changed)
        gradbox.add(table)

        return gradbox

    def fudge_changed(self, widget):
        self.fudge_factor = self.fudge_spinbutton.get_value()
        
    def solid_color_changed(self, r, g, b, index):
        self.solids[index] = \
            utils.updateColor256FromFloat(r,g,b, self.solids[index])
        
    def color_changed(self,r,g,b, is_left):
        #print "color changed", r, g, b, is_left
        if self.selected_segment == -1:
            return

        seg = self.grad.segments[self.selected_segment]
        if is_left:
            seg.left_color = [r,g,b, seg.left_color[3]]
        else:
            seg.right_color = [r,g,b, seg.right_color[3]]
        self.redraw()

    def select_segment(self,i):
        self.selected_segment = i
        if i == -1:
            self.left_color_button.set_color([0.5,0.5,0.5,1])
            self.right_color_button.set_color([0.5,0.5,0.5,1])
        else:
            self.left_color_button.set_color(self.grad.segments[i].left_color)
            self.right_color_button.set_color(self.grad.segments[i].right_color)
        # buttons should be sensitive if selection is good
        self.left_color_button.set_sensitive(i!= -1)
        self.right_color_button.set_sensitive(i!= -1)
        self.split_button.set_sensitive(i != -1)
        self.remove_button.set_sensitive(i != -1)
        self.copy_right_button.set_sensitive(i != -1)
        self.copy_left_button.set_sensitive(i != -1)
    def gradarea_mousedown(self, widget, event):
        pass

    def gradarea_clicked(self, widget, event):
        pos = float(event.x) / widget.allocation.width
        i = self.grad.get_index_at(pos)
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

    def draw_handle(self, widget, midpoint, fill):
        # draw a triangle pointing up, centered on midpoint
        total_height = widget.allocation.height
        colorband_height = total_height - self.grad_handle_height
        points = [
            (midpoint, colorband_height),
            (midpoint - 5, total_height),
            (midpoint + 5, total_height)]

        widget.window.draw_polygon(
            widget.style.black_gc, fill, points)

    def redraw_rect(self, widget, x, y, w, h):

        # draw the color preview bar
        wwidth = float(widget.allocation.width)
        colorband_height = widget.allocation.height - self.grad_handle_height
        
        colormap = widget.get_colormap()
        for i in xrange(x, x+w):
            pos_in_gradient = float(i)/wwidth
            col = self.grad.get_color_at(pos_in_gradient)
            gtkcol = colormap.alloc_color(
                int(col[0]*65535),
                int(col[1]*65535),
                int(col[2]*65535),
                True, True)
            
            self.gradgc.set_foreground(gtkcol)
            widget.window.draw_line(
                self.gradgc, i, y, i, min(y+h, colorband_height))
            
        #Draw the handles
        wgc=widget.style.white_gc
        bgc=widget.style.black_gc

        style = widget.get_style()
        widget.window.draw_rectangle(
            style.bg_gc[gtk.STATE_NORMAL], True,
            x, colorband_height, w, self.grad_handle_height)

        for i in xrange(len(self.grad.segments)):
            seg = self.grad.segments[i]
            
            left = int(seg.left * wwidth)
            mid = int(seg.mid * wwidth)
            right = int(seg.right * wwidth)

            if i == self.selected_segment:
                # draw this chunk selected
                widget.window.draw_rectangle(
                    style.bg_gc[gtk.STATE_SELECTED], True,
                    left, colorband_height,
                    right-left, self.grad_handle_height)

            self.draw_handle(widget, left, True)
            self.draw_handle(widget, mid, False)

        # draw last handle on the right
        self.draw_handle(widget, int(wwidth), True)
        
        if 0:
            index=self.grad.segments.index(seg)
            
            #A vast ugliness that should draw the selected handle with a white centre.
            #The problem is that each handle is really two handles - the second handle
            #of the left-hand segment and the first of the right.
            #The first two branches deal with handles in the middle, whilst the second
            #two deal with those at the edges. The other is a case for where neither
            #of the handles in a segment should be highlighted.            
            if self.grad.cur/2.0 == index or (self.grad.cur+1)/2.0 == index:
                self.draw_handle(widget.window, int(s_lpos), wgc, bgc)
                self.draw_handle(widget.window, int(s_rpos), bgc, bgc)
            elif (self.grad.cur-1)/2.0 == index:
                self.draw_handle(widget.window, int(s_lpos), bgc, bgc)
                self.draw_handle(widget.window, int(s_rpos), wgc, bgc)
            elif (self.grad.cur-1)/2.0 == len(self.grad.segments)-1.0 and index == 0:
                self.draw_handle(widget.window, int(s_lpos), wgc, bgc)
                self.draw_handle(widget.window, int(s_rpos), bgc, bgc)
            elif self.grad.cur == 0 and index == len(self.grad.segments)/2.0:
                self.draw_handle(widget.window, int(s_lpos), bgc, bgc)
                self.draw_handle(widget.window, int(s_rpos), wgc, bgc)
            else:
                self.draw_handle(widget.window, int(s_lpos), bgc, bgc)
                self.draw_handle(widget.window, int(s_rpos), bgc, bgc)
            
        return False

    def show(parent, f):
        dialog.T.reveal(ColorDialog,parent,f)

    show = staticmethod(show)

    def file_selection_changed(self,selection):
        (model,iter) = selection.get_selected()

        if iter == None:
            return
        
        mapfile = model.get_value(iter,0)
        self.set_map_file(self.model.maps[mapfile])

    def warn(self, msg):
        d = hig.ErrorAlert(msg,"",None)
        d.run()
        d.destroy()

    def set_map_file(self, name):
        c = fractal.Colorizer(self)
        file = open(name)
        c.parse_map_file(file, self.fudge_factor)
        self.grad = c.gradient
        if not self.grad.name:
            self.grad.name = name

        self.select_segment(-1)
        self.redraw()
        
    def redraw(self):
        allocation = self.gradarea.allocation
        self.redraw_rect(self.gradarea,
                         0,0,allocation.width, allocation.height)
        
        self.inner_solid_button.set_color(
            utils.floatColorFrom256(self.solids[1]))
        self.outer_solid_button.set_color(
            utils.floatColorFrom256(self.solids[0]))
            
    def create_map_file_list(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.map_list = gtk.ListStore(
            gobject.TYPE_STRING,
            )

        self.treeview = gtk.TreeView (self.map_list)
        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_('Gradient'), renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.unselect_all()
        
        selection.connect(
            'changed', self.file_selection_changed)

        self.update_list()
        return sw

    def update_list(self):
        self.map_list.clear()
        keys = self.model.maps.keys()
        keys.sort(stricmp)
        for k in keys:
            iter = self.map_list.append ()
            self.map_list.set (iter, 0, k)

    def onRefresh(self):
        self.update_gradient()
        self.redraw()

    def onApply(self):
        self.f.freeze()
        self.f.set_gradient(copy.copy(self.grad))
        self.f.set_solids(copy.copy(self.solids))
        if self.f.thaw():
            self.f.changed(False)
        
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        elif id == gtk.RESPONSE_APPLY:
            self.onApply()
        elif id == gtk.RESPONSE_OK:
            self.onApply()
            self.hide()
        elif id == ColorDialog.RESPONSE_REFRESH:
            self.onRefresh()
        else:
            print "unexpected response %d" % id
