# toolbar code. Some to cover up the differences between
# pygtk 2.0 and 2.4 - 2.0 doesn't have the 2.4 API, and 2.4
# spews deprecationwarnings if the 2.0 api is used. Sigh.

import gtk

class T(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)

        self.set_tooltips(True)
        self.set_border_width(1)

    def add_space(self):
        try:
            self.insert(gtk.SeparatorToolItem(), -1)
        except:
            self.append_space()

    def add_widget(self, widget, tip_text, private_text):
        try:
            toolitem = gtk.ToolItem()
            toolitem.add(widget)
            toolitem.set_expand(False)
            toolitem.set_homogeneous(False)
            toolitem.set_tooltip(gtk.Tooltips(), tip_text, private_text)
            self.insert(toolitem,-1)
        except Exception, exn:
            print exn
            self.append_element(
                gtk.TOOLBAR_CHILD_WIDGET,            
                widget,
                tip_text,
                private_text,
                None,
                None,
                None,
                None)

    def add_button(self, title, tip_text, image, cb):
        try:
            toolitem = gtk.ToolButton(image,title)
            self.insert(toolitem,-1)
        except:
            self.append_element(
                gtk.TOOLBAR_CHILD_BUTTON,
                None,
                title,
                tip_text,
                None,
                image,
                cb,
                None)

    def add_stock(self, stock_id, tip_text, cb):
        try:
            toolitem = gtk.ToolButton(stock_id)
            toolitem.connect('clicked', cb)
            toolitem.set_tooltip(gtk.Tooltips(), tip_text, tip_text)
            self.insert(toolitem,-1)
        except:
            self.insert_stock(
                stock_id,
                tip_text,
                tip_text,
                cb,
                None,
                -1)

    def add_toggle(self, stock_id, title, tip_text, cb):
        try:
            toolitem = gtk.ToggleToolButton(stock_id)
            toolitem.connect('toggled', cb)
            toolitem.set_tooltip(gtk.Tooltips(), tip_text, tip_text)
            self.insert(toolitem,-1)
        except:
            pixbuf = self.render_icon(
                stock_id, gtk.ICON_SIZE_LARGE_TOOLBAR, "toolbar")
            if pixbuf == None:
                pixbuf = self.render_icon(
                    gtk.STOCK_MISSING_IMAGE,
                    gtk.ICON_SIZE_LARGE_TOOLBAR, "toolbar")
                
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            self.append_element(
                gtk.TOOLBAR_CHILD_TOGGLEBUTTON,
                None,
                title,
                tip_text,
                None,
                image,
                cb,
                None)
