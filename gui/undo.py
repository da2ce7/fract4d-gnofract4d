
import gtk
import gobject

class HistoryEntry:
    def __init__(self,redo,undo):
        self.undo_action = undo
        self.redo_action = redo
    
class Sequence(gobject.GObject):
    __gsignals__ = {
        'can-undo' : (
        gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
        'can-redo' : (
        gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
        }
    
    def __init__(self):
        gobject.GObject.__init__(self)
        self.pos = 0 # the position after the current item
        self.history = []

    def can_undo(self):
        return self.pos > 0

    def can_redo(self):
        return self.pos < len(self.history)

    def send_signals(self):        
        self.emit('can-undo', self.can_undo())
        self.emit('can-redo', self.can_redo())
        
    def do(self,redo_action,undo_action):
        # replace everything from here on with the new item
        del self.history[self.pos:]
        self.history.append(HistoryEntry(redo_action,undo_action))
        self.pos = len(self.history)

        self.send_signals()
        
    def undo(self):
        if not self.can_undo():
            raise ValueError("Can't Undo at start of sequence")
        self.pos -= 1
        self.history[self.pos].undo_action()
        self.send_signals()

    def redo(self):
        if not self.can_redo():
            raise ValueError("Can't Redo at end of sequence")
        self.history[self.pos].redo_action()
        self.pos += 1
        
        self.send_signals()
        
gobject.type_register(Sequence)
