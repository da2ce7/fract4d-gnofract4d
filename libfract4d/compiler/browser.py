#!/usr/bin/env python

# an interactive browser to examine and debug fractal functions

import gobject
import gtk

import fractparser
import fractlexer

class MainWindow:
    def __init__(self):

        self.parser = fractparser.parser
        self.lexer = fractlexer.lexer

        self.formula_list = gtk.ListStore(gobject.TYPE_STRING)
        self.formulas = {}
        
        self.window = gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(640,400)
        self.window.set_title('formula browser')
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

        self.accelgroup = gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)

        self.create_menu()
        self.create_panes()
        
        self.window.show_all()

    def create_menu(self):
        menu_items = (
            ('/_File', None, None, 0, '<Branch>' ),
            ('/File/_Open', '<control>O', self.open, 0, ''),
            ('/File/sep1', None, None, 0, '<Separator>'),
            ('/File/_Quit', '<control>Q', self.quit, 0, ''),   
            ('/_Preferences', None, None, 0, '<Branch>'),
            ('/_Help', None, None, 0, '<Branch>'),
            ('/Help/_About', None, self.about, 0, ''),
            )
    
        item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>', self.accelgroup)
        item_factory.create_items(menu_items)

        menubar = item_factory.get_widget('<main>')

        self.vbox.pack_start(menubar, expand=gtk.FALSE)

    def create_panes(self):
        panes = gtk.HPaned()
        self.vbox.pack_start(panes, gtk.TRUE, gtk.TRUE)
        panes.set_border_width(5)

        # left-hand pane displays formula list
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.treeview = gtk.TreeView (self.formula_list)
        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn ('Formula', renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.connect('changed',self.selection_changed)
        
        panes.add1(sw)

        # right-hand pane is details of current formula
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        self.text = gtk.TextView()
        sw.add(self.text)
        
        panes.add2(sw)

    def selection_changed(self,selection):
        (model,iter) = selection.get_selected()
        title = model.get_value(iter,0)
        formula = self.formulas[title]
        buffer = self.text.get_buffer()
        buffer.set_text(formula.pretty(),-1)
        
    def quit(self,action,widget=None):
        gtk.main_quit()
        
    def open(self,action,widget):
        print "open"

    def load(self,file):
        s = open(file,"r").read() # read in a whole file
        self.lexer.lineno = 1
        result = self.parser.parse(s)

        for formula in result.children:
            iter = self.formula_list.append ()
            self.formula_list.set (iter, 0, formula.leaf)
            self.formulas[formula.leaf] = formula
        
    def about(self,action,widget):
        print "about"
        
def main():
    mainWindow = MainWindow()
    mainWindow.load('fractint.frm')
    gtk.main()

    
    
if __name__ =='__main__': main()
