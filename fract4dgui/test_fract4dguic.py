#!/usr/bin/env python

# unit tests for fract4dgui C module

import unittest
import sys
import os
import commands

import gtk

sys.path.append("..") #FIXME

from fract4d import fract4dc
import fract4dguic

class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testBadSaves(self):
        try:
            self.saveAndCheck("test.gif","GIF")
            self.fail("No exception thrown")
        except ValueError, err:
            self.assertEqual(
                str(err),
                "Unsupported file format '.gif'. Please use .JPG or .PNG.")
        except Exception:
            self.fail("Wrong exception type")

        try:
            self.saveAndCheck("no_extension","GIF")
            self.fail("No exception thrown")
        except ValueError, err:
            self.assertEqual(
                str(err),
                "No file extension in 'no_extension'. " +
                "Can't determine file format. " +
                "Please use .JPG or .PNG.")
        except Exception:
            self.fail("Wrong exception type")

        try:
            self.saveAndCheck("no_such_dir/test.png","PNG")
            self.fail("No exception thrown")
        except IOError, err:
            self.assertEqual(
                str(err),
                "Unable to save image to 'no_such_dir/test.png' : " +
                "No such file or directory")
        except Exception:
            self.fail("Wrong exception type")

    def testMailtoHandler(self):
        mail_editor = fract4dguic.get_gconf_setting("/desktop/gnome/url-handlers/mailto/command")
        browser = fract4dguic.get_gconf_setting("/desktop/gnome/url-handlers/http/command")
        
    def testSave(self):
        self.saveAndCheck("test.png","PNG")
        self.saveAndCheck("test.PNG","PNG")
        self.saveAndCheck("test.jpeg","JPEG")
        self.saveAndCheck("test.jpg","JPEG")
        
    def saveAndCheck(self,name,format):
        if os.path.exists(name):
            os.remove(name)
        image = fract4dc.image_create(64,48)
        fract4dguic.image_save(image, name)
        self.assertEqual(os.path.isfile(name), True)
        # run ImageMagick to test file contents
        (status,output) = commands.getstatusoutput("identify %s" % name)
        self.assertEqual(status,0)
        fields = output.split()
        self.assertEqual(fields[0],name)
        self.assertEqual(fields[1],format)
        self.assertEqual(fields[2],"64x48")
        
        os.remove(name)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
