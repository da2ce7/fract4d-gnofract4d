
import gtk
import gobject

class UndoSequence(gobject.GObject):
    __gsignals__ = {
        'can-undo' : (
        gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
        'can-redo' : (
        gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
        }
    
    def __init__(self):
        gobject.GObject.__init__(self)
        self.can_undo = False
        self.can_redo = False
        self.pos = 0
        self.history = []

    def do(self,action):
        could_redo = self.can_redo
        could_undo = self.can_undo

        del self.history[self.pos:]
        
        self.history.append(action)
        if !could_undo:
            self.emit('can-undo', gtk.TRUE)
        if could_redo:
            self.emit('can-redo', gtk.FALSE)

    def undo(self):
        if self.pos <= 0:
            raise ValueError("Can't Undo at start of sequence")
        self.pos -= 1
        history[self.pos]() 
    

gobject.type_register(UndoSequence)
