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
import painter
import gtkfractal

class Test(unittest.TestCase):
    def setUp(self):
        self.compiler = fc.Compiler()
        self.compiler.file_path.append("../formulas")
        self.compiler.file_path.append("../fract4d")
        
        self.f = gtkfractal.T(self.compiler)
        self.settings = painter.PainterDialog(None,self.f)
        
    def tearDown(self):
        pass
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
