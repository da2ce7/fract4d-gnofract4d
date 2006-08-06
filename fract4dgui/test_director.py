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

sys.path.append("..")
import director, PNGGen, hig

from fract4d import fractal, image, fc,directorbean

g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.file_path.append("../formulas")

class Test(unittest.TestCase):
    def setUp(self):
        # ensure any dialog boxes are dismissed without human interaction
        hig.timeout = 250

    def tearDown(self):
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

    def assertRaisesMessage(self, excClass, msg, callable, *args, **kwargs):
        try:
            callable(*args,**kwargs)
        except excClass, exn:
            self.assertEqual(msg,str(exn))
        else:
            if hasattr(excClass,'__name__'): excName = excClass.__name__
            else: excName = str(excClass)
            raise self.failureException, "%s not raised" % excName

    def testOwnSanity(self):
        # exercise each of the checks in the check_sanity function
        f = fractal.T(g_comp)
        dd= director.DirectorDialog(None,f,"")
        self.assertRaisesMessage(
            director.SanityCheckError, "Base keyframe not set",
            dd.check_sanity)

        dd.dir_bean.set_base_keyframe("fred")
        self.assertRaisesMessage(
            director.SanityCheckError, "There must be at least one keyframe",
            dd.check_sanity)
        
        dd.dir_bean.add_keyframe("/tmp/director2.fct",1,10,directorbean.INT_LOG)
        dd.dir_bean.set_png_dir("")
        self.assertRaisesMessage(
            director.SanityCheckError,
            "Directory for temporary .png files not set",
            dd.check_sanity)

        dd.dir_bean.set_png_dir("fishy")
        self.assertRaisesMessage(
            director.SanityCheckError,
            "Path for temporary .png files is not a directory",
            dd.check_sanity)

        dd.dir_bean.set_png_dir("/tmp/")
        
        self.assertRaisesMessage(
            director.SanityCheckError,
            "Output AVI file name not set",
            dd.check_sanity)

        dd.dir_bean.set_avi_file("/tmp/foo.avi")

        dd.dir_bean.set_fct_enabled(True)
        
        self.assertRaisesMessage(
            director.SanityCheckError,
            "Keyframe /tmp/director2.fct is in the temporary .fct directory and could be overwritten. Please change temp directory.",
            dd.check_sanity)

        
        
    def testKeyframeClash(self):
        f = fractal.T(g_comp)
        dd= director.DirectorDialog(None,f,"")

        dd.check_for_keyframe_clash("/a","/b")
        
        self.assertRaises(
            director.SanityCheckError,
            dd.check_for_keyframe_clash, "/tmp/foo.fct", "/tmp")
        self.assertRaises(
            director.SanityCheckError,
            dd.check_for_keyframe_clash, "/tmp/foo.fct", "/tmp/")

        
        
    def testPNGGen(self):
        f = fractal.T(g_comp)
        dd= director.DirectorDialog(None,f,"")
        pg = PNGGen.PNGGeneration(dd.dir_bean,g_comp)
        pg.generate_png()
        
        dd.destroy()
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
