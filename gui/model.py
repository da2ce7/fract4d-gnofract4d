# The top-level data structure behind the UI. Corresponds to the MainWindow

import gtkfractal
import undo

class Model:
    def __init__(self,f):
        # undo history
        self.seq = undo.Sequence()

        # used to prevent recursive sets of commands happening
        # at the same time
        self.command_in_progess = False
        self.f = f
        self.old_f = self.f.copy_f()
        self.f.connect('parameters-changed',self.onParametersChanged)
        
    def onParametersChanged(self,*args):
        current = self.f.copy_f()
        def redo():
            self.f.freeze()
            self.f.set_fractal(current)
            self.f.thaw()
            
        previous = self.old_f
        def undo():
            self.f.freeze()
            self.f.set_fractal(previous)
            self.f.thaw()
            
        self.seq.do(redo,undo)

    def undo(self):
        self.seq.undo()

    def redo(self):
        self.seq.redo()
