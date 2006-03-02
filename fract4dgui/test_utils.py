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
