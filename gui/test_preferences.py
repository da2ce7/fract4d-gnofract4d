#!/usr/bin/env python

# test classes for preferences logic

import unittest
import sys
import os

import preferences

class Test(unittest.TestCase):
    def setUp(self):
        self.config = preferences.Preferences("test.config")
    
    def tearDown(self):
        pass
        
    def testCreate(self):        
        flags = self.config.get("compiler","options")
        self.assertEqual(flags,"-shared -O3 -ffast-math")

    def testSave(self):
        self.config.set("compiler","options","-foo")
        self.assertEqual(self.config.get("compiler","options"),"-foo")
        self.config.write(open("config.tmp","w"))

        config2 = preferences.Preferences("config.tmp")
        self.assertEqual(config2.get("compiler","options"),"-foo")
        #os.remove("config.tmp")
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
