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

    def get_param_entry(self, page_name, label_name):
        'Find and return an entry widget on the settings dialog'
        notebook = self.settings.notebook
        i = 0
        page = notebook.get_nth_page(0)
        while page != None:
            i += 1
            this_page_name = notebook.get_tab_label_text(page)
            if this_page_name == page_name:
                for child in page.get_children():
                    if isinstance(child, gtk.Label):
                        this_label_name = child.get_text()
                        if this_label_name == label_name:
                            entry = child.get_mnemonic_widget()
                            self.assertEqual(isinstance(entry,gtk.Entry),True)
                            return entry
                        
            page = notebook.get_nth_page(i)
            
        self.fail("Can't find page %s" % page_name)
        
    def testFractalChangeUpdatesSettings(self):
        self.f.set_param(self.f.MAGNITUDE, 2000.0)
        widget = self.get_param_entry(_("Location"), _("Size :"))
        self.assertEqual(widget.get_text(),"2000.00000000000000000")
                         
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
