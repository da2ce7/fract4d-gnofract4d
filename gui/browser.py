#!/usr/bin/env python

# a browser to examine fractal functions
import string

import gobject
import gtk

_browser = None

def show(parent, f):
    global _browser
    if not _browser:
        _browser = BrowserDialog(parent,f)
    _browser.show_all()

class BrowserDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        gtk.Dialog.__init__(
            self,
            "Formula Browser",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.formula_list = gtk.ListStore(
            gobject.TYPE_STRING)

        self.file_list = gtk.ListStore(
            gobject.TYPE_STRING)

        self.f = f
        self.compiler = f.compiler
        self.current_fname = None
        
        #self.accelgroup = gtk.AccelGroup()
        #self.window.add_accel_group(self.accelgroup)

        self.create_panes()
        
        self.connect('response',self.onResponse)

    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        else:
            print "unexpected response %d" % id

    def create_file_list(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.treeview = gtk.TreeView (self.file_list)
        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn ('File', renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.connect('changed',self.file_selection_changed)

        self.populate_file_list()
        return sw

    def populate_file_list(self):
        for (fname,formulalist) in self.compiler.files.items():
            iter = self.file_list.append ()
            self.file_list.set (iter, 0, fname)

    def populate_formula_list(self,fname):
        self.formula_list.clear()
        
        ff = self.compiler.files[fname]

        form_names = ff.formulas.keys()
        form_names.sort()        
        for formula_name in form_names:
            iter = self.formula_list.append()
            self.formula_list.set(iter,0,formula_name)
        
    def create_formula_list(self):
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
        selection.connect('changed',self.formula_selection_changed)
        return sw

    def create_scrolled_textview(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()
        sw.add(textview)
        return (textview,sw)
    
    def create_panes(self):
        # 3 panes: files, formulas, formula contents
        panes1 = gtk.HPaned()
        self.vbox.pack_start(panes1, gtk.TRUE, gtk.TRUE)
        panes1.set_border_width(5)

        file_list = self.create_file_list()
        formula_list = self.create_formula_list()
        
        panes2 = gtk.HPaned()
        # left-hand pane displays file list
        panes2.add1(file_list)
        # middle is formula list for that file
        panes2.add2(formula_list)        
        panes1.add1(panes2)

        # right-hand pane is details of current formula
        notebook = gtk.Notebook()

        # source
        (self.sourcetext,sw) = self.create_scrolled_textview()
        notebook.append_page(sw, gtk.Label('Source'))
        
        # parse tree
        (self.text,sw) = self.create_scrolled_textview()
        notebook.append_page(sw, gtk.Label('Parse Tree'))

        # translated tree
        (self.transtext,sw) = self.create_scrolled_textview()
        notebook.append_page(sw, gtk.Label('IR Tree'))

        # messages
        (self.msgtext, sw) = self.create_scrolled_textview()
        notebook.append_page(sw, gtk.Label('Messages'))

        # asm
        #(self.asmtext, sw) = self.create_scrolled_textview()
        #notebook.append_page(sw, gtk.Label('Generated Code'))
        
        panes1.add2(notebook)

    def file_selection_changed(self,selection):
        (model,iter) = selection.get_selected()
        if iter == None:
            return
        
        self.current_fname = model.get_value(iter,0)
        text = self.compiler.files[self.current_fname].contents
        self.sourcetext.get_buffer().set_text(text,-1)
        self.populate_formula_list(self.current_fname)

    def formula_selection_changed(self,selection):
        (model,iter) = selection.get_selected()
        if iter == None:
            return
        
        form_name = model.get_value(iter,0)
        file = self.current_fname
        formula = self.compiler.get_parsetree(file,form_name)
        
        # update parse tree
        buffer = self.text.get_buffer()
        buffer.set_text(formula.pretty(),-1)

        #update location of source buffer
        sourcebuffer = self.sourcetext.get_buffer()
        iter = sourcebuffer.get_iter_at_line(formula.pos-1)
        self.sourcetext.scroll_to_iter(iter,0.0,gtk.TRUE,0.0,0.0)

        # update IR tree
        self.ir = self.compiler.get_formula(file,form_name)
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

        #self.compiler.generate_code(formula,"browser-tmp.c")
        
        #buffer = self.asmtext.get_buffer()
        #buffer.set_text(self.compiler.c_code,-1)
        
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

                
    def display_file(self,ff,name):
        for formula in ff.formulas:
            iter = self.formula_list.append ()
            self.formula_list.set (iter, 0, formula)

        text = ff.contents
        self.sourcetext.get_buffer().set_text(text,-1)
        
