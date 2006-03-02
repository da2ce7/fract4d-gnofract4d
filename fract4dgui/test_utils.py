#!/usr/bin/env python

# unit tests for utils module

import unittest
import sys
import os
import commands
import warnings

import gtk

import utils


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

        utils.hide_extra_widgets(chooser)
        
        self.runAndDismiss(chooser)


        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def runAndDismiss(self,d):
        def dismiss():
            d.response(gtk.RESPONSE_ACCEPT)
            d.hide()
            return False

        # increase timeout to see what dialogs look like
        utils.timeout_add(10,dismiss)
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
