#!/usr/bin/env python

# a browser to examine fractal functions
import string

import gobject
import gtk

FRACTAL = 0
INNER = 1
OUTER = 2

_browser = None

def show(parent, f,type):
    global _browser
    if not _browser:
        _browser = BrowserDialog(parent,f)
    _browser.set_type(type)
    _browser.populate_file_list()
    _browser.show_all()

def update():
    global _browser
    if _browser:
        _browser.populate_file_list()
    
class BrowserDialog(gtk.Dialog):
    def __init__(self,main_window,f):
        gtk.Dialog.__init__(
            self,
            "Formula Browser",
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.disable_apply()
        
        self.formula_list = gtk.ListStore(
            gobject.TYPE_STRING)

        self.file_list = gtk.ListStore(
            gobject.TYPE_STRING)

        self.f = f
        self.compiler = f.compiler
        self.current_fname = None
        self.func_type = FRACTAL
        
        self.set_size_request(750,500)
        #self.accelgroup = gtk.AccelGroup()
        #self.window.add_accel_group(self.accelgroup)

        self.create_panes()
        
        self.connect('response',self.onResponse)

    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        elif id == gtk.RESPONSE_APPLY:
            self.onApply()
        else:
            print "unexpected response %d" % id

    def onApply(self):
        self.f.freeze()
        if self.func_type == FRACTAL:
            self.f.set_formula(self.current_fname,self.current_formula)
        elif self.func_type == INNER:
            self.f.set_inner(self.current_fname,self.current_formula)
        elif self.func_type == OUTER:
            self.f.set_outer(self.current_fname,self.current_formula)
        else:
            assert(False)
        self.f.reset()
        if self.f.thaw():
            self.f.changed()

    def set_type_cb(self,optmenu):
        self.set_type(optmenu.get_history())
            
    def set_type(self,type):
        if self.func_type == type:
            return
        self.func_type = type
        self.funcTypeMenu.set_history(type)
        self.populate_file_list()
        
    def disable_apply(self):
        self.set_response_sensitive(gtk.RESPONSE_APPLY,False)

    def enable_apply(self):
        self.set_response_sensitive(gtk.RESPONSE_APPLY,True)

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
        return sw

    def populate_file_list(self):
        self.file_list.clear()
        if self.func_type == FRACTAL:
            files = self.compiler.formula_files()
        else:
            files = self.compiler.colorfunc_files()
            
        for (fname,formulalist) in files:
            iter = self.file_list.append ()
            self.file_list.set (iter, 0, fname)

        self.formula_list.clear()
        self.formula_selection_changed(None)
        
    def populate_formula_list(self,fname):
        self.formula_list.clear()
        
        ff = self.compiler.files[fname]

        exclude = [None, "OUTSIDE", "INSIDE"]
        
        form_names = ff.get_formula_names(exclude[self.func_type])
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
        sw.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()
        sw.add(textview)
        return (textview,sw)

    def create_panes(self):
        # option menu for choosing Inner/Outer/Fractal
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Function to Modify : "), gtk.FALSE, gtk.FALSE)
        
        self.funcTypeMenu = gtk.OptionMenu()
        menu = gtk.Menu()
        for item in [
            "Fractal Function",
            "Inner Coloring Function",
            "Outer Coloring Function"]:
            mi = gtk.MenuItem(item)
            menu.append(mi)
        self.funcTypeMenu.set_menu(menu)

        self.funcTypeMenu.connect('changed',self.set_type_cb)
        
        hbox.pack_start(self.funcTypeMenu,gtk.TRUE, gtk.TRUE)
        self.vbox.pack_start(hbox,gtk.FALSE, gtk.FALSE)
        
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

    def clear_selection(self):
        self.text.get_buffer().set_text("",-1)
        self.transtext.get_buffer().set_text("",-1)
        self.sourcetext.get_buffer().set_text("",-1)
        self.msgtext.get_buffer().set_text("",-1)
        self.disable_apply()
        
    def formula_selection_changed(self,selection):
        if not selection:
            self.clear_selection()
            return
        
        (model,iter) = selection.get_selected()
        if iter == None:
            self.clear_selection()
            return
        
        form_name = model.get_value(iter,0)
        self.current_formula = form_name
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

        if self.ir.errors == []:
            self.enable_apply()
        else:
            self.disable_apply()
        
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
        
