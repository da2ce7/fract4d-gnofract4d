#!/usr/bin/env python

import unittest

import testbase
import sys

sys.path.append("build/lib.linux-i686-2.2") # FIXME
import colormap


class CmapTest(testbase.TestBase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testLoad(self):
        f = open("../maps/volcano.map","r")
        c = colormap.ColorMap(f)
        self.assertEqual(c.r[0],(0.0,0,0,0,255))
        for i in xrange(256):
            l = c.lookup(i/256.0)
            o = c.r[i]
            self.assertEqual((o[1],o[2],o[3],o[4]),l)
            
def suite():
    return unittest.makeSuite(CmapTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
