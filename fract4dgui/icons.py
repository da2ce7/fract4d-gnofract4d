# our 'quasi-stock' icons

import gtk
import utils

_iconfactory = gtk.IconFactory()
_iconfactory.add_default()
    
class StockThing:
    def __init__(self, file, stock_name, title, key):
        global _iconfactory
        self.stock_name = stock_name
        self.title = title
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(
            utils.find_resource(file,
                                'pixmaps',
                                'share/pixmaps/gnofract4d'))

        self.iconset = gtk.IconSet(self.pixbuf)
        _iconfactory.add(stock_name, self.iconset)

        gtk.stock_add(
            [(stock_name, title, gtk.gdk.CONTROL_MASK, key, "c")])

explorer = StockThing('explorer_mode.png', 'explore', _('Explorer'), ord('e'))

deepen_now = StockThing('deepen_now.png', 'deepen', _('Deepen'), ord('d'))

logo = StockThing('gnofract4d-logo.png', 'logo', _('Logo'), 0)


