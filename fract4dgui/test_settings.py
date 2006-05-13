#!/usr/bin/env python

#unit tests for settings window

import unittest
import copy
import math
import os
import sys

import gtk
import gettext
os.environ.setdefault('LANG', 'en')
gettext.install('gnofract4d')
sys.path.append("..")

from fract4d import fc, fractal
import settings
import gtkfractal

class Test(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        self.compiler.file_path.append("../formulas")
        self.compiler.file_path.append("../fract4d")
        
        self.f = gtkfractal.T(self.compiler)
        self.settings = settings.SettingsDialog(None,self.f)
        
    def tearDown(self):
        pass
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def search_for_named_widget(self, page, label_name):
        for child in page.get_children():
            if isinstance(child, gtk.Label):
                this_label_name = child.get_text()
                #print this_label_name
                if this_label_name == label_name:
                    entry = child.get_mnemonic_widget()
                    self.assertNotEqual(entry, None,
                                        "all widgets should have mnemonics")
                    self.assertEqual(isinstance(entry,gtk.Entry),True)
                    return entry
            elif isinstance(child, gtk.Container):
                widget = self.search_for_named_widget(child,label_name)
                if widget:
                    return widget
        
    def get_param_entry(self, page_name, label_name):
        'Find and return an entry widget on the settings dialog'
        notebook = self.settings.notebook
        i = 0
        page = notebook.get_nth_page(0)
        while page != None:
            this_page_name = notebook.get_tab_label_text(page)
            if this_page_name == page_name:
                widget = self.search_for_named_widget(page,label_name)
                self.assertNotEqual(
                    widget, None,
                    "Page doesn't contain widget '%s'" % label_name)
                return widget
            i += 1
            page = notebook.get_nth_page(i)
            
        self.fail("Can't find page %s" % page_name)
        
    def testFractalChangeUpdatesSettings(self):
        self.f.set_param(self.f.MAGNITUDE, 2000.0)
        widget = self.get_param_entry(_("Location"), _("Size :"))
        self.assertEqual(widget.get_text(),"2000.00000000000000000")

        self.f.forms[0].set_named_param("@bailout", 578.0)
        self.assertEqual(
            self.f.forms[0].get_named_param_value("@bailout"), 578.0)
        
        widget = self.get_param_entry(_("Formula"), _("bailout"))
        self.assertEqual(widget.get_text(),"578.00000000000000000")

def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
