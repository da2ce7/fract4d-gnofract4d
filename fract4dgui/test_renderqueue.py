#!/usr/bin/env python

# unit tests for renderqueue module

import unittest
import sys
import os
import commands

import gtk

import renderqueue

sys.path.append("..")

from fract4d import fractal, image, fc

g_comp = fc.Compiler()
g_comp.file_path.append("../fract4d")
g_comp.file_path.append("../formulas")

class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def wait(self):
        gtk.main()
        
    def quitloop(self,rq):
        gtk.main_quit()

    def testRQ(self):
        rq = renderqueue.T(g_comp)
        self.assertEqual(0, len(rq.queue))

        # should be a no-op
        rq.start()

        # add a fractal to generate
        f = fractal.T(g_comp)
        rq.add(f,"rq1.png",2048,1536)

        # check it got added
        self.assertEqual(1, len(rq.queue))
        entry = rq.queue[0]
        self.assertEqual("rq1.png", entry.name)
        self.assertEqual(2048, entry.w)
        self.assertEqual(1536, entry.h)

        # run
        rq.connect('done', self.quitloop)
        rq.start()
        self.wait()

        self.assertEqual(0, len(rq.queue))
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
