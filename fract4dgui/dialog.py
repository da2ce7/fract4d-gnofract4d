# superclass for dialogs

import gtk
import new

_dialogs = {}

class T(gtk.Dialog):
    def __init__(self,title=None,parent=None,flags=0,buttons=None):
        gtk.Dialog.__init__(self,title,parent,flags,buttons)

        self.set_default_response(gtk.RESPONSE_CLOSE)
        self.connect('response',self.onResponse)

        self.connect('destroy-event', self.clear_global)
        self.connect('delete-event', self.clear_global)

    def clear_global(self,*args):
        global _dialogs
        _dialogs[self.__class__] = None

    def reveal(type,*args):
        global _dialogs
        if not _dialogs.get(type):
            _dialogs[type] = type(*args)
        _dialogs[type].show_all()
        _dialogs[type].present()
        return _dialogs[type]
    
    reveal = staticmethod(reveal)

    
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        else:
            print "unexpected response %d" % id
