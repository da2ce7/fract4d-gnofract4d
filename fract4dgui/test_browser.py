#!/usr/bin/env python

#unit tests for browser window

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
import browser

class Test(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        self.compiler.file_path.append("../formulas")
        self.compiler.file_path.append("../fract4d")
        
        self.f = fractal.T(self.compiler,self)
    
    def tearDown(self):
        pass
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):        
        b = browser.BrowserDialog(None,self.f)
        self.assertNotEqual(b,None)

    def testLoadFormula(self):
        b = browser.BrowserDialog(None,self.f)
        b.set_file('gf4d.frm')
        b.set_formula('Newton')
        self.assertEqual(b.ir.errors,[])

    def testBadFormula(self):
        b = browser.BrowserDialog(None,self.f)
        b.set_file('test.frm')
        b.set_formula('parse_error')
        self.assertNotEqual(b.ir.errors,[])
        buffer = b.msgtext.get_buffer()
        all_text = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            True)
        self.assertNotEqual(all_text,"")
        self.assertEqual(all_text[0:7],"Errors:")

    def test_update(self):
        b = browser.update(None)
         
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
