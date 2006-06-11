#!/usr/bin/env python

# unit tests for utils module

import unittest
import sys
import os
import commands
import warnings

import gtk

import utils
import gtkfractal

from fract4d import fc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.file_path.append("../formulas")


class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testOptionMenu(self):
        om = utils.create_option_menu(["foo","bar","Bazniculate Geometry"])
        utils.add_menu_item(om,"fishy")
        utils.set_selected(om,3)
        self.assertEqual(3, utils.get_selected(om))

        utils.set_menu_from_list(om, ["hello","world"])
        utils.set_selected(om,1)
        item1 = utils.get_selected_value(om)
        self.assertEqual("world",item1)

        utils.set_selected_value(om,"hello")
        i = utils.get_selected(om)
        self.assertEqual(0,i)

        utils.set_selected_value(om,"world")
        i = utils.get_selected(om)
        self.assertEqual(1,i)
        
    def testCreateColor(self):
        cyan = utils.create_color(0.0,1.0,1.0)
        self.assertEqual(cyan.red,0)
        self.assertEqual(cyan.green,65535)
        self.assertEqual(cyan.blue,65535)

    def testFileSaveChooser(self):
        extra = gtk.Label("hello")
        chooser = utils.get_file_save_chooser(
            "Foo",None,["*.py"], extra)

        self.assertEqual(utils.get_file_chooser_extra_widget(chooser), extra)
        self.runAndDismiss(chooser)

    def testFileOpenChooser(self):
        preview = gtkfractal.SubFract(g_comp, 120, 90)
        chooser = utils.get_file_open_chooser(
            "Bar", None, ["*.fct"])
        
        utils.file_chooser_set_preview(chooser, preview, self.on_update_preview)

        self.runAndDismiss(chooser)

    def on_update_preview(self, chooser, preview):
        filename = chooser.get_preview_filename()
        try:
            preview.loadFctFile(open(filename))
            preview.draw_image(False, False)
            active=True
        except Exception,err:
            active=False
        chooser.set_preview_widget_active(active)
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def runAndDismiss(self,d, time=1):
        def dismiss():
            d.response(gtk.RESPONSE_ACCEPT)
            d.hide()
            return False

        # increase timeout to see what dialogs look like
        utils.timeout_add(10 * time,dismiss)
        r = d.run()
        d.destroy()

class ThrowbackTest(Test):
    """Test all the 'old' versions of the utilities."""
    def setUp(self):
        utils.force_throwback()

        # don't clutter output with known deprecation warnings
        warnings.filterwarnings(
            "ignore",
            ".*",
            DeprecationWarning,
            ".*",
            0)

    def tearDown(self):
        utils.unforce_throwback()

    
def suite():
    s = unittest.makeSuite(Test,'test')
    s.addTest(unittest.makeSuite(ThrowbackTest, 'test'))
    return s

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
