#!/usr/bin/env python

# an interactive browser to examine and debug fractal functions
import string

import gobject
import gtk


import fc

class MainWindow:
    def __init__(self):
        self.formula_list = gtk.ListStore(
            gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        self.compiler = fc.Compiler()
        
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
        notebook = gtk.Notebook()

        # source
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        self.sourcetext = gtk.TextView()
        sw.add(self.sourcetext)
        notebook.append_page(sw, gtk.Label('Source'))
        
        # parse tree
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        self.text = gtk.TextView()
        sw.add(self.text)
        notebook.append_page(sw, gtk.Label('Parse Tree'))

        # translated tree
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        self.transtext = gtk.TextView()
        sw.add(self.transtext)
        notebook.append_page(sw, gtk.Label('IR Tree'))

        # messages
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        self.msgtext = gtk.TextView()
        sw.add(self.msgtext)
        notebook.append_page(sw, gtk.Label('Messages'))

        # asm
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        self.asmtext = gtk.TextView()
        sw.add(self.asmtext)
        notebook.append_page(sw, gtk.Label('Generated Code'))
        
        panes.add2(notebook)

    def selection_changed(self,selection):
        (model,iter) = selection.get_selected()
        title = model.get_value(iter,0)
        file = model.get_value(iter,1)
        formula = self.compiler.get_formula(file,title)

        # update parse tree
        #buffer = self.text.get_buffer()
        #buffer.set_text(formula.pretty(),-1)

        #update location of source buffer
        #sourcebuffer = self.sourcetext.get_buffer()
        #iter = sourcebuffer.get_iter_at_line(formula.pos-1)
        #self.sourcetext.scroll_to_iter(iter,0.0,gtk.TRUE,0.0,0.0)

        # update IR tree
        self.ir = formula
        irbuffer = self.transtext.get_buffer()
        irbuffer.set_text(self.ir.pretty(),-1)
        
        # update messages
        buffer = self.msgtext.get_buffer()
        msg = ""
        if self.ir.errors != []:
            msg += "Errors:\n" + string.join(self.ir.errors,"\n") + "\n"
        if self.ir.warnings != []:
            msg += "Warnings:\n" + string.join(self.ir.warnings,"\n")
        if msg == "":
            msg = "No messages"
            
        buffer.set_text(msg,-1)

        self.compiler.generate_code(formula,"browser-tmp.c")
        
        buffer = self.asmtext.get_buffer()
        buffer.set_text(self.compiler.c_code,-1)
        
    def quit(self,action,widget=None):
        gtk.main_quit()
        
    def open(self,action,widget):
        fs = gtk.FileSelection("Open Formula File")
        result = fs.run()
        
        if result == gtk.RESPONSE_OK:
            self.load(fs.get_filename())
        fs.destroy()

    def load(self,file):
        ff = self.compiler.load_formula_file(file)

        for formula in ff.formulas:
            iter = self.formula_list.append ()
            self.formula_list.set (iter, 0, formula)
            self.formula_list.set (iter, 1, file)

        text = ff.contents
        self.sourcetext.get_buffer().set_text(text,-1)
        
    def about(self,action,widget):
        print "about"
        
def main():
    mainWindow = MainWindow()
    mainWindow.load('formulas/fractint.frm')
    gtk.main()

    
    
if __name__ =='__main__': main()
