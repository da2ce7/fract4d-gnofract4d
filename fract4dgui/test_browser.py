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
        self.compiler.add_func_path("../formulas")
        self.compiler.add_func_path("../fract4d")
        
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

    def testFuncTypes(self):
        b = browser.BrowserDialog(None,self.f)
        self.assertEqual(browser.FRACTAL, b.func_type)

        b.set_type(browser.INNER)
        self.assertEqual(browser.INNER, b.func_type)

        b.set_type(browser.OUTER)
        self.assertEqual(browser.OUTER, b.func_type)

        b.set_type(browser.TRANSFORM)
        self.assertEqual(browser.TRANSFORM, b.func_type)

        b.set_type(browser.GRADIENT)
        self.assertEqual(browser.GRADIENT, b.func_type)

    def test_update(self):
        b = browser.update(None)
        m = browser.get_model(self.compiler)
        self.assertEqual(None, m.current.fname)
        self.assertEqual(None, m.current.formula)

        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
