# utilities to comply with Gnome Human Interface Guidelines.
# these are defined at http://developer.gnome.org/projects/gup/hig/2.0/

import gtk

class Alert(gtk.Dialog):
    def __init__(self, image, primary_text, secondary_text="",
                 buttons=(),parent=None,flags=0):

        if not isinstance(image,gtk.Image):
            image = gtk.image_new_from_stock(image, gtk.ICON_SIZE_DIALOG)
            
        flags = flags | (gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        gtk.Dialog.__init__(self,"",parent,flags,buttons)
        self.set_resizable(False)
        self.set_border_width(6)
        self.set_has_separator(False)

        self.vbox.set_spacing(12)
        
        upper_hbox = gtk.HBox()
        upper_hbox.set_spacing(12)
        upper_hbox.set_border_width(6)

        image.set_alignment(0.5,0.5)
        image.icon_size = gtk.ICON_SIZE_DIALOG
        
        upper_hbox.pack_start(image)
        
        if secondary_text and len(secondary_text) > 0:
            secondary_text = "\n\n" + secondary_text
        label_text = '<span weight="bold" size="larger">%s</span>%s' % \
                     (primary_text, secondary_text)

        label = gtk.Label(label_text)
        label.set_use_markup(True)
        label.set_line_wrap(True)
        
        upper_hbox.pack_start(label)
        
        self.vbox.pack_start(upper_hbox)
        
        self.show_all()

class InformationAlert(Alert):
    def __init__(self,primary_text, secondary_text="",parent=None):
        Alert.__init__(
            self,
            gtk.STOCK_DIALOG_INFO,
            primary_text,
            secondary_text,
            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT),
            parent)

class ErrorAlert(Alert):
    FIX = 1
    def __init__(self,
                 primary_text,
                 secondary_text="",
                 parent=None,
                 fix_button=None):

        # if optional fix button supplied, add to list of buttons
        buttons = []
        if fix_button:
            buttons = [ fix_button, ErrorAlert.FIX]
        buttons += [gtk.STOCK_OK, gtk.RESPONSE_ACCEPT]
        
        Alert.__init__(
            self,
            gtk.STOCK_DIALOG_ERROR,
            primary_text,
            secondary_text,
            tuple(buttons),
            parent)

        self.set_default_response(gtk.RESPONSE_ACCEPT)

class ConfirmationAlert(Alert):
    ALTERNATE=1
    def __init__(self,
                 primary_text,
                 secondary_text,
                 parent=None,
                 proceed_button=gtk.STOCK_OK,
                 alternate_button=None):

        # if optional fix button supplied, add to list of buttons
        buttons = []
        if alternate_button:
            buttons = [ alternate_button, ConfirmationAlert.ALTERNATE]

        buttons += [gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    proceed_button, gtk.RESPONSE_ACCEPT]
        
        Alert.__init__(
            self,
            gtk.STOCK_DIALOG_WARNING,
            primary_text,
            secondary_text,
            tuple(buttons),
            parent)

        self.set_default_response(gtk.RESPONSE_CANCEL)

def _periodText(seconds):
    if seconds > 86400:
        return "%d days" % (seconds // 86400)
    elif seconds > 3600:
        return "%d hours" % (seconds // 3600)
    elif seconds > 60:
        return "%d minutes" % (seconds // 60)
    else:
        return "%d seconds" % seconds
    
class SaveConfirmationAlert(ConfirmationAlert):
    NOSAVE = ConfirmationAlert.ALTERNATE
    def __init__(self,
                 document_name,
                 time_period=-1,
                 parent=None):

        if time_period==-1:
            text = "If you don't save, changes will be discarded."
        else:
            text = ("If you don't save, changes from the past %s " + \
                   "will be discarded.") % _periodText(time_period)
        ConfirmationAlert.__init__(
            self,
            'Save changes to document "%s" before closing?' % document_name,
            text,
            parent,
            gtk.STOCK_SAVE,
            "_Close without Saving")
        
