#!/usr/bin/env python

# a browser to examine fractal functions
import string
import os

import gobject
import gtk

import preferences

FRACTAL = 0
INNER = 1
OUTER = 2

_browser = None

def stricmp(a,b):
    return cmp(a.lower(),b.lower())

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
    RESPONSE_EDIT = 1
    RESPONSE_REFRESH = 2
    RESPONSE_COMPILE = 3
    def __init__(self,main_window,f):
        gtk.Dialog.__init__(
            self,
            _("Formula Browser"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (#_("Co_mpile"), BrowserDialog.RESPONSE_COMPILE,
             gtk.STOCK_REFRESH, BrowserDialog.RESPONSE_REFRESH,
             gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
             gtk.STOCK_OK, gtk.RESPONSE_OK,
             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.set_default_response(gtk.RESPONSE_OK)
        self.disable_apply()
        
        self.formula_list = gtk.ListStore(
            gobject.TYPE_STRING)

        self.file_list = gtk.ListStore(
            gobject.TYPE_STRING)

        self.f = f
        self.compiler = f.compiler
        self.current_fname = None
        self.current_formula = None
        self.ir = None
        self.func_type = FRACTAL
        self.tooltips = gtk.Tooltips()
        self.main_window = main_window
        self.set_size_request(600,500)

        self.dirty_formula = False
        self.create_panes()

        self.connect('response',self.onResponse)

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
        elif id == BrowserDialog.RESPONSE_EDIT:
            self.onEdit()
        elif id == BrowserDialog.RESPONSE_REFRESH:
            self.onRefresh()
        elif id == BrowserDialog.RESPONSE_COMPILE:
            self.onCompile()
        else:
            print "unexpected response %d" % id

    def onEdit(self):
        editor = preferences.userPrefs.get("editor","name")
        file = self.compiler.find_file(self.current_fname)
        os.system("%s %s &" % (editor, file))

    def onRefresh(self):
        self.f.refresh()
        self.set_file(self.current_fname) # update text window

    def get_current_text(self):
        buffer = self.sourcetext.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(), False)
        return text
    
    def onCompile(self):
        if self.current_fname:
            text = self.get_current_text()
            formulas = self.compiler.parse_file(text)

            ff = self.compiler.files.get(self.current_fname)
            ff.override_buffer(text,formulas)
            self.set_file(self.current_fname)
            frm = formulas.get(self.current_formula)
            if self.ir and self.ir.errors == []:
                self.onApply()
            
    def onApply(self):
        self.f.freeze()
        if not self.current_formula or not self.current_fname:
            #can't apply
            return
        
        if self.func_type == FRACTAL:
            self.f.set_formula(self.current_fname,self.current_formula)
            self.f.reset()
        elif self.func_type == INNER:
            self.f.set_inner(self.current_fname,self.current_formula)
        elif self.func_type == OUTER:
            self.f.set_outer(self.current_fname,self.current_formula)
        else:
            assert(False)
        if self.f.thaw():
            self.f.changed()

    def set_type_cb(self,optmenu):
        if self.confirm():
            self.set_type(optmenu.get_history())
            
    def set_type(self,type):
        if self.func_type == type:
            return
        self.func_type = type
        self.funcTypeMenu.set_history(type)
        self.populate_file_list()
        
    def disable_apply(self):
        self.set_response_sensitive(gtk.RESPONSE_APPLY,False)
        self.set_response_sensitive(gtk.RESPONSE_OK,False)
        self.set_edit_sensitivity()

    def set_edit_sensitivity(self):
        is_editable = hasattr(self,"current_fname") and self.current_fname != None
        self.set_response_sensitive(BrowserDialog.RESPONSE_EDIT,is_editable)
        
    def enable_apply(self):
        self.set_response_sensitive(gtk.RESPONSE_APPLY,True)
        self.set_response_sensitive(gtk.RESPONSE_OK,True)
        self.set_edit_sensitivity()
        
    def create_file_list(self):
        sw = gtk.ScrolledWindow ()

        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.filetreeview = gtk.TreeView (self.file_list)
        self.tooltips.set_tip(
            self.filetreeview,
            _("A list of files containing fractal formulas"))
        
        sw.add(self.filetreeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn ('_File', renderer, text=0)
        
        self.filetreeview.append_column (column)

        selection = self.filetreeview.get_selection()
        selection.connect('changed',self.file_selection_changed)
        return sw

    def populate_file_list(self):
        self.file_list.clear()
        if self.func_type == FRACTAL:
            files = self.compiler.find_formula_files()
        else:
            files = self.compiler.find_colorfunc_files()

        files.sort(stricmp)
        for fname in files:
            iter = self.file_list.append ()
            self.file_list.set (iter, 0, fname)

        self.formula_list.clear()
        self.formula_selection_changed(None)
        
    def populate_formula_list(self,fname):
        self.formula_list.clear()
        
        ff = self.compiler.files[fname]

        exclude = [None, "OUTSIDE", "INSIDE"]
        
        form_names = ff.get_formula_names(exclude[self.func_type])
        form_names.sort(stricmp)        
        for formula_name in form_names:
            iter = self.formula_list.append()
            self.formula_list.set(iter,0,formula_name)
            if formula_name == self.current_formula:
                self.treeview.get_selection().select_iter(iter)
                self.set_formula(formula_name)
                
    def create_formula_list(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.treeview = gtk.TreeView (self.formula_list)

        self.tooltips.set_tip(
            self.treeview,
            _("A list of formulas in the selected file"))

        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_('F_ormula'), renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.connect('changed',self.formula_selection_changed)
        return sw

    def create_scrolled_textview(self,tip):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()
        self.tooltips.set_tip(textview, tip)
        textview.set_editable(False)
        
        sw.add(textview)
        return (textview,sw)

    def onEditFormula(self,buffer):
        self.dirty_formula = True
        
    def create_panes(self):
        # option menu for choosing Inner/Outer/Fractal
        self.funcTypeMenu = gtk.OptionMenu()
        menu = gtk.Menu()
        for item in [
            _("Fractal Function"),
            _("Inner Coloring Function"),
            _("Outer Coloring Function")]:
            mi = gtk.MenuItem(item)
            menu.append(mi)
        self.funcTypeMenu.set_menu(menu)

        self.tooltips.set_tip(
            self.funcTypeMenu,
            _("Which formula of the current fractal to change"))

        self.funcTypeMenu.connect('changed',self.set_type_cb)

        # label for the menu
        hbox = gtk.HBox()
        label = gtk.Label(_("Function _Type to Modify : "))
        label.set_use_underline(True)
        label.set_mnemonic_widget(self.funcTypeMenu)
        
        hbox.pack_start(label, gtk.FALSE, gtk.FALSE)
                
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
        (self.sourcetext,sw) = self.create_scrolled_textview(
            _("The contents of the currently selected formula file"))
        self.sourcetext.get_buffer().connect('changed',self.onEditFormula)
        
        label = gtk.Label(_('_Source'))
        label.set_use_underline(True)
        notebook.append_page(sw, label)

        # messages
        (self.msgtext, sw) = self.create_scrolled_textview(
            _("Any compiler warnings or errors in the current function"))
        
        label = gtk.Label(_('_Messages'))
        label.set_use_underline(True)
        notebook.append_page(sw, label)

        # parse tree
        (self.text,sw) = self.create_scrolled_textview("")
        #notebook.append_page(sw, gtk.Label(_('_Parse Tree')))

        # translated tree
        (self.transtext,sw) = self.create_scrolled_textview("")
        #notebook.append_page(sw, gtk.Label(_('_IR Tree')))


        # asm
        (self.asmtext, sw) = self.create_scrolled_textview("")
        #notebook.append_page(sw, gtk.Label('Generated Code'))
        
        panes1.add2(notebook)

    def file_selection_changed(self,selection):
        (model,iter) = selection.get_selected()
        if iter == None:
            return
        
        fname = model.get_value(iter,0)
        self.set_file(fname)

    def confirm(self):
        msg = _("Do you want to save changes to formula file '%s'?")
        carry_on = True
        if self.dirty_formula:
            d = gtk.MessageDialog(None,
                                  gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_QUESTION,
                                  gtk.BUTTONS_YES_NO,
                                  msg % self.current_fname)
            response = d.run()                
            d.destroy()
            carry_on = (response == gtk.RESPONSE_NO) 
            if response == gtk.RESPONSE_YES:
                self.save()
                carry_on = True

        return carry_on
        
    def save(self):
        text = self.get_current_text()
        f = open(self.compiler.find_file(self.current_fname),"w")
        f.write(text)
        f.close()
        self.dirty_formula = False
        
    def set_file(self,fname):
        if self.dirty_formula and self.current_fname != fname:
            if not self.confirm():
                return
        
        self.current_fname = fname
        text = self.compiler.get_text(self.current_fname)
        self.clear_selection()
        self.sourcetext.get_buffer().set_text(text,-1)
        self.dirty_formula = False
        self.populate_formula_list(self.current_fname)
        self.set_edit_sensitivity()
        
    def clear_selection(self):
        self.text.get_buffer().set_text("",-1)
        self.transtext.get_buffer().set_text("",-1)
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
        self.set_formula(form_name)
        
    def set_formula(self,form_name):
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
            msg += _("Errors:\n") + string.join(self.ir.errors,"\n") + "\n"
        if self.ir.warnings != []:
            msg += _("Warnings:\n") + string.join(self.ir.warnings,"\n")
        if msg == "":
            msg = _("No messages")
            
        buffer.set_text(msg,-1)

        if self.ir.errors == []:
            self.enable_apply()
        else:
            self.disable_apply()        
        
    def open(self,action,widget):
        fs = gtk.FileSelection(_("Open Formula File"))
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
        
