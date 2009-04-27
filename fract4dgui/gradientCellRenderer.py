
from fract4d import gradient

import gtk, gobject

class GradientCellRenderer(gtk.GenericCellRenderer):
    __gproperties__ = {
        'text': (gobject.TYPE_STRING,
                 'Text to be displayed',
                 'Text to be displayed',
                 '',
                 gobject.PARAM_READWRITE
                 ),
        'gradient': (gobject.TYPE_PYOBJECT,
                 'Gradient to display',
                 'Gradient to display',
                 gobject.PARAM_READWRITE
                 )
        }

    def __init__(self,model,compiler):
        gtk.GenericCellRenderer.__init__(self)
        self.model = model
        self.compiler = compiler
        self.__properties = {}

    def do_set_property(self, key, value):
        #print "set", key, value
        self.__properties[key.name] = value
	
    def do_get_property(self, key):
        return self.__properties[key.name]

    def on_get_size(self, widget, cell_area):
        if cell_area == None:
            return (0,0,0,0)
        x = cell_area.x
        y = cell_area.x
        w = cell_area.width
        h = cell_area.height

        return (x,y,w,h)

    def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
        style = widget.get_style()
        (w,h) = (cell_area.width, cell_area.height)
        #style.paint_box(
        #    window, widget.state,
        #    gtk.SHADOW_IN, expose_area, widget, "",
        #    cell_area.x, cell_area.y, w-1, h-1)

        formname = self.__properties["text"]
        filename = self.model.current.fname

        grad = self.compiler.get_gradient(filename, formname)

        wwidth = float(cell_area.width)+1
        colorband_height = cell_area.height
        
        colormap = widget.get_colormap()
        gradgc = widget.window.new_gc(fill=gtk.gdk.SOLID)

        for i in xrange(cell_area.x, cell_area.x + cell_area.width):
            pos_in_gradient = float(i-cell_area.x)/wwidth
            col = grad.get_color_at(pos_in_gradient)
            gtkcol = colormap.alloc_color(
                int(col[0]*65535),
                int(col[1]*65535),
                int(col[2]*65535),
                True, True)
            
            gradgc.set_foreground(gtkcol)
            window.draw_line(
                gradgc, i, cell_area.y, i, cell_area.y + cell_area.height)


    def on_activate(self, event, widget, path, background_area, cell_area, flags):
        print "on_activate, ", locals()
        pass

    def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
        print "on_activate, ", locals()
        pass
