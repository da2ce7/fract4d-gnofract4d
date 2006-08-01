#!/usr/bin/env python

# unit tests for renderqueue module

import unittest
import sys
import os
import commands

import gtk
import gettext
os.environ.setdefault('LANG', 'en')
gettext.install('gnofract4d')
import director

sys.path.append("..")

from fract4d import fractal, image, fc,directorbean

g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.file_path.append("../formulas")

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
    	print "b"
        pass

    def wait(self):
        gtk.main()

    def quitloop(self,rq):
        gtk.main_quit()

    def testDirectorDialog(self):
        f = fractal.T(g_comp)
        dd=director.DirectorDialog(None,f,"")
        dd.show(None,None,f,True,"")
        png_before=dd.dir_bean.get_png_dir()
        fct_enabled_before=dd.dir_bean.get_fct_enabled()
        dd.dir_bean.set_png_dir("./")
        dd.dir_bean.set_fct_enabled(False)
        dd.dir_bean.set_base_keyframe("../testdata/director1.fct")
        dd.dir_bean.add_keyframe("../testdata/director2.fct",1,10,directorbean.INT_LOG)
        dd.dir_bean.set_avi_file("./video.avi")
        dd.dir_bean.set_width(320)
        dd.dir_bean.set_height(240)
        dd.generate(False)
        dd.dir_bean.set_png_dir(png_before)
        dd.dir_bean.set_fct_enabled(fct_enabled_before)
        self.assertEqual(os.path.exists("./image_0.png"),True)
        self.assertEqual(os.path.exists("./image_1.png"),True)
        dd.destroy()

def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
