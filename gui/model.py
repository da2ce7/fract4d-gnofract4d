# The top-level data structure behind the UI. Corresponds to the MainWindow

import gtkfractal
import undo

class Model:
    def __init__(self,f):
        # undo history
        self.seq = undo.Sequence()

        # used to prevent undo/redo from triggering new commands
        self.callback_in_progress = False
        self.f = f
        self.old_f = self.f.copy_f()
        self.f.connect('parameters-changed',self.onParametersChanged)

    def block_callbacks(self):
        self.callback_in_progress = True

    def unblock_callbacks(self):
        self.callback_in_progress = False

    def callbacks_allowed(self):
        return not self.callback_in_progress
    
    def onParametersChanged(self,*args):
        if not self.callbacks_allowed():
            return
        
        current = self.f.copy_f()
        def redo():
            self.f.freeze()
            self.f.set_fractal(current)
            if self.f.thaw():
                self.block_callbacks()
                self.f.changed()
                self.f.unblock_callbacks()
                
        previous = self.old_f        
        def undo():
            self.f.freeze()
            self.f.set_fractal(previous)
            if self.f.thaw():
                self.block_callbacks()
                self.f.changed()
                self.unblock_callbacks()

        self.seq.do(redo,undo)
        self.old_f = current
        
    def undo(self):
        if self.seq.can_undo():
            self.seq.undo()

    def redo(self):
        if self.seq.can_redo():
            self.seq.redo()
