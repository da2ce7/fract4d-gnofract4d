# A module which manages a queue of images to render in the background
# and a UI for the same


import copy

import gobject

import gtkfractal

class QueueEntry:
    def __init__(self, f, name, w, h):
        self.f = f
        self.name = name
        self.w = w
        self.h = h
        
# the underlying queue object
class T(gobject.GObject):
    __gsignals__ = {
        'done' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'image-complete' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ())
        }

    def __init__(self,compiler):
        gobject.GObject.__init__(self)
        self.compiler = compiler
        self.queue = []
        self.current = None
        
    def add(self,f,name,w,h):
        entry = QueueEntry(copy.copy(f),name,w,h)
        self.queue.append(entry)
        
    def start(self):
        self.next()

    def next(self):
        if self.queue == []:
            self.emit('done')
            return

        entry = self.queue.pop()

        self.current = gtkfractal.HighResolution(self.compiler,entry.w,entry.h)
        self.current.set_fractal(entry.f)
        
        self.current.connect('status-changed', self.onImageComplete)
        self.current.draw_image(entry.name)

    def onImageComplete(self, f, status):
        if status == 0:
            self.emit('image-complete')
            self.next()

# explain our existence to GTK's object system
gobject.type_register(T)
