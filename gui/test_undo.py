#!/usr/bin/env python

#unit tests for undo code

import unittest
import copy
import math

import gtk
import undo

class Status:
    def __init__(self):
        self.count = 0
        
class UndoTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):
        undoer = undo.Sequence()
        self.assertEqual(len(undoer.history),0)
        self.assertEqual(undoer.can_undo(),False)
        self.assertEqual(undoer.can_redo(),False)
        self.assertEqual(undoer.pos,0)
        
        status = Status()
        def inc_status():
            status.count += 1
            
        def dec_status():
            status.count -= 1

        self.assertEqual(status.count,0)

        # perform an action
        inc_status()
        undoer.do(inc_status,dec_status)
        
        self.assertEqual(status.count,1)
        self.assertEqual(len(undoer.history),1)
        self.assertEqual(undoer.can_undo(),True)
        self.assertEqual(undoer.can_redo(),False)
        self.assertEqual(undoer.pos,1)
        
        # undo it
        undoer.undo()
        self.assertEqual(status.count,0)
        self.assertEqual(len(undoer.history),1)
        self.assertEqual(undoer.can_undo(),False)
        self.assertEqual(undoer.can_redo(),True)
        self.assertEqual(undoer.pos,0)
        
        # redo it
        undoer.redo()
        self.assertEqual(status.count,1)
        self.assertEqual(len(undoer.history),1)
        self.assertEqual(undoer.can_undo(),True)
        self.assertEqual(undoer.can_redo(),False)
        self.assertEqual(undoer.pos,1)
        
def suite():
    return unittest.makeSuite(UndoTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
