#!/usr/bin/env python

# unit tests for model

import unittest
import copy
import sys

import gtk
import model

sys.path.append("..") #FIXME

from fract4d import fractal,fc,fract4dc

import gtkfractal
import settings
import preferences
import autozoom
import undo

# do compiler setup once
g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.load_formula_file("gf4d.frm")
g_comp.load_formula_file("gf4d.cfrm")

class Test(unittest.TestCase):
    def setUp(self):
        global g_comp
        self.compiler = g_comp
        self.f = gtkfractal.T(self.compiler)        
        self.m = model.Model(self.f)
    
    def tearDown(self):
        self.f = self.m = None
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):
        self.failUnless(self.f)
        self.failUnless(self.m)
        self.assertEqual(self.m.f, self.f)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
