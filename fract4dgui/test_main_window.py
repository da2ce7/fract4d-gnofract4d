#!/usr/bin/env python

# high-level unit tests for main window

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

import main_window

class Test(unittest.TestCase):
    def setUp(self):
        self.mw = main_window.MainWindow()
        self.assertEqual(self.mw.filename, None, "shouldn't have a filename")
        self.mw.show_error_message = self.save_error_message
        self.errors = []
    
    def tearDown(self):
        self.errors = []
        if os.path.exists('mytest.fct'):
            os.remove('mytest.fct')
        os.system("killall realyelp > /dev/null 2>&1")
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def save_error_message(self,message,exception):
        self.errors.append((message,exception))
        
    def testLoad(self):
        # load good file
        fn_good = "../testdata/test.fct"
        result = self.mw.load(fn_good)
        self.failUnless(result, "load failed")
        self.assertEqual(self.mw.filename, fn_good)

        # load bad file
        fn_bad = "test_main_window.py"
        result = self.mw.load(fn_bad)
        self.assertEqual(result, False, "load of bad file succeeded")
        self.assertEqual(self.mw.filename, fn_good) # filename shouldn't change
        self.assertEqual(
            self.errors[0][0], "Error opening test_main_window.py")

        # load missing file
        fn_bad = "wibble.fct"
        result = self.mw.load(fn_bad)
        self.assertEqual(result, False, "load of missing file succeeded")
        self.assertEqual(self.mw.filename, fn_good) # filename shouldn't change
        self.assertEqual(
            self.errors[1][0], "Error opening wibble.fct")

    def testSave(self):
        # load good file
        fn_good = "../testdata/test.fct"
        result = self.mw.load(fn_good)
        self.failUnless(result, "load failed")

        # save again
        result = self.mw.save_file("mytest.fct")
        self.assertEqual(result, True, "save file failed")
        self.assertEqual(self.mw.filename, "mytest.fct")

        # fail to save to bad location
        result = self.mw.save_file("/no_such_dir/mytest.fct")
        self.assertEqual(result, False, "save file to bad location succeeded")
        self.assertEqual(self.mw.filename, "mytest.fct")
        self.assertEqual(
            self.errors[0][0], "Error saving to file /no_such_dir/mytest.fct")
        
    def testLoadFormula(self):
        # load good formula file
        result = self.mw.load_formula("../formulas/fractint.cfrm")
        self.assertEqual(result, True, "failed to load formula")

        #load missing file
        result = self.mw.load_formula("/no_such_dir/wibble.frm")
        self.assertEqual(result, False, "load bad formula succeeded")
        self.assertEqual(
            self.errors[0][0], "Error opening /no_such_dir/wibble.frm")

        # load bad file. Formula parser is pretty permissive so
        # we'll just load it and claim it contains no formulas
        fn_bad = "test_main_window.py"
        result = self.mw.load_formula(fn_bad)
        self.assertEqual(result, True, "load of bad file failed")

    def testDialogs(self):
        self.mw.settings(None,None)
        self.mw.colors(None,None)
        self.mw.preferences(None,None)
        self.mw.autozoom(None,None)
        self.mw.contents(None,None)
        self.mw.browser(None,None)

    def testExplorer(self):
        self.mw.set_explorer_state(True)
        self.mw.set_explorer_state(False)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
