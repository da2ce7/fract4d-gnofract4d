#!/usr/bin/env python

# test classes for preferences logic

import unittest
import sys
import os

sys.path.append("..")
import preferences

class CallCounter:
    def __init__(self):
        self.count = 0
    def cb(self,*args):
        self.count += 1

class Test(unittest.TestCase):
    def setUp(self):
        self.config = preferences.Preferences("test.config")
    
    def tearDown(self):
        pass
        
    def testSignals(self):
        counter = CallCounter()
        
        self.config.connect('preferences-changed',counter.cb)

        # callback should happen
        self.config.set('compiler','name','cc')
        self.assertEqual(counter.count,1)

        # no callback, value already set
        self.config.set('compiler','name','cc')
        self.assertEqual(counter.count,1)

        # new option, callback called
        self.config.set('compiler','foop','cc')
        self.assertEqual(counter.count,2)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
