#!/usr/bin/env python

#unit tests for gradient editor window

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

from fract4d import gradient, fc, fractal
import gtkgradient

class Test(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        self.compiler.file_path.append("../formulas")
        
        self.f = fractal.T(self.compiler,self)
    
    def tearDown(self):
        pass
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):        
        b = gtkgradient.GradientDialog(None,self.f)
        self.assertNotEqual(b,None)
         
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
