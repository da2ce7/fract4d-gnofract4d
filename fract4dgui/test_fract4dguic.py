#!/usr/bin/env python

# unit tests for fract4dgui C module

import unittest
import sys
import os
import commands

import gtk

import fract4dguic

class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testGConf(self):
        mail_editor = fract4dguic.get_gconf_string("/desktop/gnome/url-handlers/mailto/command")
        browser = fract4dguic.get_gconf_string("/desktop/gnome/url-handlers/http/command")
                
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
