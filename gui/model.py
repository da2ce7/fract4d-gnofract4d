# The top-level data structure behind the UI. Corresponds to the MainWindow

import gtkfractal
import undo

class Model:
    def __init__(self,f):
        self.seq = undo.Sequence
        self.command_in_progess = False
        self.f = f
        self.old_f = None
        
    def start(self):
        if self.command_in_progess: return False

        self.command_in_progess = True
        self.old_f = self.f.copy_f()
        
    def finish(self):
        current = self.f
        def redo():
            self.f = current

        previous = self.old_f
        def undo():
            self.f = previous

        self.seq.do(redo,undo)
        self.f.emit('parameters-changed')
    
