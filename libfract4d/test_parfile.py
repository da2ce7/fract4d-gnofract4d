#!/usr/bin/env python

# test cases for parfile.py

import parfile

import string
import unittest

class ParTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testColors(self):
        self.assertEqual(parfile.colorRange(""), [])

        colors = parfile.colorRange("05F")
        self.assertEqual(len(colors),1)
        
        colors = parfile.colorRange("05F<63>DISDISDIS<89>uxxuxxvyyvyywzz<94>05F")
        self.assertEqual(len(colors),256)

        self.assertRaises(RuntimeError,parfile.colorRange, "&*(")
        self.assertRaises(RuntimeError,parfile.colorRange, "00")
        self.assertRaises(RuntimeError,parfile.colorRange, "000<0>000")
        self.assertRaises(RuntimeError,parfile.colorRange, "<1>000")
        
def suite():
    return unittest.makeSuite(ParTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
