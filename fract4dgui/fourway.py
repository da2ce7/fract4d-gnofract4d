# Sort of a widget which controls 2 linear dimensions of the fractal
# I say sort of, because this doesn't actually inherit from gtk.Widget,
# so it's not really a widget. This is because if I attempt to do that
# pygtk crashes. Hence this ungodly hack.

import gtk
import gobject

class T(gobject.GObject):
    __gsignals__ = {
        'value-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT)),
        'value-slightly-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))
        }

    def __init__(self,text):        
        gobject.GObject.__init__(self)
        self.button = 0
        self.radius = 0
        self.last_x = 0
        self.last_y = 0
        self.text=text

        self.widget = gtk.DrawingArea()
        self.widget.set_size_request(32,32)

        self.widget.add_events(gtk.gdk.BUTTON_RELEASE_MASK |
                               gtk.gdk.BUTTON1_MOTION_MASK |
                               gtk.gdk.POINTER_MOTION_HINT_MASK |
                               gtk.gdk.BUTTON_PRESS_MASK
                               )
        
        self.widget.connect('motion_notify_event', self.onMotionNotify)
        self.widget.connect('button_release_event', self.onButtonRelease)
        self.widget.connect('button_press_event', self.onButtonPress)
        self.widget.connect('expose_event',self.onExpose)

    def update_from_mouse(self,x,y):
        dx = self.last_x - x
        dy = self.last_y - y
        if dx or dy:
            self.emit('value-slightly-changed',dx,dy)
            self.last_x = x
            self.last_y = y
        
    def onMotionNotify(self,widget,event):
        dummy = widget.window.get_pointer()
        self.update_from_mouse(event.x, event.y)

    def onButtonRelease(self,widget,event):
        if event.button==1:
            (xc,yc) = (widget.allocation.width//2, widget.allocation.height//2)
            dx = xc - self.last_x
            dy = yc - self.last_y
            if dx or dy:
                self.emit('value-changed',dx,dy)
        
    def onButtonPress(self,widget,event):
        if event.button == 1:
            self.last_x = widget.allocation.width/2
            self.last_y = widget.allocation.height/2
            self.update_from_mouse(event.x, event.y)
        
    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        style = widget.get_style()
        (w,h) = (widget.allocation.width, widget.allocation.height)
        
        style.paint_box(widget.window, widget.state,
                        gtk.SHADOW_IN, r, widget, "",
                        0, 0, w, h)

        xc = w//2
        yc = h//2
        radius = min(w,h)//2

        gc = style.fg_gc[widget.state]
        # Triangle pointing left        
        points = [
            (xc - radius+1, yc),
            (xc - radius+7, yc-5),
            (xc - radius+7, yc+5)]
                
        widget.window.draw_polygon(gc, True, points)

        # pointing right
        points = [
            (xc + radius-2, yc),
            (xc + radius-7, yc-5),
            (xc + radius-7, yc+5)]
        widget.window.draw_polygon(gc, True, points)

        # pointing up
        points = [
            (xc, yc - radius + 1),
            (xc - 5, yc - radius + 7),
            (xc + 5, yc - radius + 7)]
        widget.window.draw_polygon(gc, True, points)
        
        # pointing down
        points = [
            (xc, yc + radius - 2),
            (xc - 5, yc + radius - 7),
            (xc + 5, yc + radius - 7)]
        widget.window.draw_polygon(gc, True, points)

        
# explain our existence to GTK's object system
gobject.type_register(T)
