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

    def assertUndoStatus(self,undoer,should_undo,should_redo):
        self.assertEqual(undoer.can_undo(),should_undo)
        self.assertEqual(undoer.can_redo(),should_redo)
        self.assertExternalAndInternalStatusMatch(undoer)

    def assertExternalAndInternalStatusMatch(self,undoer):
        self.assertEqual(self.undo_cb_status.count, undoer.can_undo())
        self.assertEqual(self.redo_cb_status.count, undoer.can_redo())
        
    def testCreateUndoRedo(self):        
        status = Status()
        self.undo_cb_status = Status()
        self.redo_cb_status = Status()
        
        def inc_status():
            status.count += 1
            
        def dec_status():
            status.count -= 1

        def set_undoable(sequence,state):
            #print "undo_status: %s" % state
            self.undo_cb_status.count = state

        def set_redoable(sequence,state):
            #print "redo_status: %s" % state
            self.redo_cb_status.count = state
            
        self.assertEqual(status.count,0)
        self.assertEqual(self.undo_cb_status.count,0)
        self.assertEqual(self.redo_cb_status.count,0)
                
        # create sequence
        undoer = undo.Sequence()
        undoer.connect('can-undo',set_undoable)
        undoer.connect('can-redo',set_redoable)
        
        self.assertEqual(undoer.can_undo(),False)
        self.assertEqual(undoer.can_redo(),False)
        self.assertExternalAndInternalStatusMatch(undoer)
        
        self.assertEqual(undoer.pos,0)
        self.assertEqual(len(undoer.history),0)
        
        # perform an action
        undoer.do(inc_status,dec_status)
        
        self.assertEqual(status.count,1)
        self.assertUndoStatus(undoer,True,False)        
        self.assertEqual(len(undoer.history),1)
        self.assertEqual(undoer.pos,1)

        # undo it
        undoer.undo()

        # check externals
        self.assertEqual(status.count,0)
        self.assertUndoStatus(undoer,False,True)
        
        # check internals
        self.assertEqual(len(undoer.history),1)
        self.assertEqual(undoer.pos,0)
        
        # redo it
        undoer.redo()

        # check externals
        self.assertEqual(status.count,1)
        self.assertUndoStatus(undoer,True,False)
        
        # check internals
        self.assertEqual(len(undoer.history),1)
        self.assertEqual(undoer.pos,1)

    def testUndoAndRedoAreAssociated(self):
        status = Status()

        def inc_status():
            status.count += 1
            
        def dec_status():
            status.count -= 1

        def make_status_string():
            status.count = "foo"

        def make_status_int():
            status.count = 1
                    
        self.assertEqual(status.count,0)

        # create sequence
        undoer = undo.Sequence()
        undoer.do(inc_status,dec_status)
        undoer.do(make_status_string, make_status_int)

        self.assertEqual(status.count,"foo")
        undoer.undo()
        self.assertEqual(status.count,1)
        undoer.undo()
        self.assertEqual(status.count,0)

    def testDoRemovesRedoStack(self):
        status = Status()

        def inc_status():
            status.count += 1
            
        def dec_status():
            status.count -= 1
                    
        self.assertEqual(status.count,0)

        # perform 3 actions, undo 2, do 1 again
        undoer = undo.Sequence()
        undoer.do(inc_status,dec_status)
        undoer.do(inc_status,dec_status)
        undoer.do(inc_status,dec_status)
        undoer.undo()
        undoer.undo()
        self.assertEqual(status.count,1)
        
        undoer.do(inc_status,dec_status)
        self.assertEqual(len(undoer.history),2)
        self.assertEqual(undoer.can_redo(), False)
        self.assertEqual(status.count,2)

    def testInvalidOperationsThrow(self):
        undoer = undo.Sequence()
        self.assertRaises(ValueError,undoer.undo)
        self.assertRaises(ValueError,undoer.redo)
        
def suite():
    return unittest.makeSuite(UndoTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
