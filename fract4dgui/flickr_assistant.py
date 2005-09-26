# a series of boxes for negotiating flickr's authorization process

# doesn't actually use the gnome 'druid' framework, we do it ourselves to keep dependencies simpler

import os
import re

import gtk, pango

import dialog
import browser
import utils
import preferences
import hig
import random

from fractutils import flickr

TOKEN = None

def is_authorized():
    global TOKEN
    token = preferences.userPrefs.get("user_info", "flickr_token")
    if token == "":
        return False

    try:
        TOKEN = flickr.checkToken(token)
    except FlickrError, err:
        return False

    return True

def show_flickr_assistant(parent,alt_parent, f,dialog_mode):
    if is_authorized():
        FlickrUploadDialog.show(parent,alt_parent,f,dialog_mode)
    else:
        FlickrAssistantDialog.show(parent,alt_parent, f,True)

def launch_browser(url, window):
    browser = preferences.userPrefs.get("helpers","browser")
    cmd = browser % ('"' + url + '"')
    try:
        os.system(cmd)
    except Exception, err:
        d = hig.ErrorAlert(
            _("Error launching browser"),
            _("Try modifying your preferences or copy the URL manually to a browser window.\n") + \
            str(err),window) 
        d.run()
        d.destroy()

class FlickrUploadDialog(dialog.T):
    clean_formula_re = re.compile(r'[^a-z0-9]', re.IGNORECASE)
    def show(parent, alt_parent, f,dialog_mode):
        dialog.T.reveal(FlickrUploadDialog,dialog_mode, parent, alt_parent, f)
            
    show = staticmethod(show)

    def __init__(self, main_window, f):        
        dialog.T.__init__(
            self,
            _("Flickr"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f
        self.main_window = main_window
        self.controls = gtk.VBox()
        self.vbox.pack_start(self.controls)

        table = gtk.Table(5,2,False)
        self.controls.pack_start(table)

        self.title_entry = gtk.Entry()
        table.attach(self.title_entry,1,2,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        title_label = gtk.Label(_("Tit_le:"))
        title_label.set_mnemonic_widget(self.title_entry)
        title_label.set_use_underline(True)
        table.attach(title_label,0,1,0,1,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.tags = gtk.Entry()
        table.attach(self.tags,1,2,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        tag_label = gtk.Label(_("Ta_gs:"))
        tag_label.set_mnemonic_widget(self.tags)
        tag_label.set_use_underline(True)
        table.attach(tag_label,0,1,1,2,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        self.description = gtk.TextView()
        self.description.set_wrap_mode(gtk.WRAP_WORD)

        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.description)
        
        table.attach(sw,1,2,2,3,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        desc_label = gtk.Label(_("_Description:"))
        desc_label.set_mnemonic_widget(self.description)
        desc_label.set_use_underline(True)
        table.attach(desc_label,0,1,2,3,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
        self.upload_button = gtk.Button(_("_Upload"))
        self.upload_button.connect("clicked", self.onUpload)
        self.controls.pack_start(self.upload_button)

        self.view_my_button = gtk.Button(_("View _My Fractals"))
        self.view_my_button.connect("clicked", self.onViewMy)
        self.controls.pack_start(self.view_my_button)

        self.view_pool_button = gtk.Button(_("View G_roup Fractals"))
        self.view_pool_button.connect("clicked", self.onViewPool)
        self.controls.pack_start(self.view_pool_button)

    def onResponse(self,widget,id):
        self.hide()

    def get_description(self):
        buffer = self.description.get_buffer()
        return buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())

    def get_tags(self):
        formula_tag = FlickrUploadDialog.clean_formula_re.sub('',self.f.funcName)
        return "fractal gnofract4d %s %s" % (formula_tag,self.tags.get_text())
        
    def onUpload(self,widget):
        filename = "/tmp/%d.png" % int(random.uniform(0,1000000))
        self.f.save_image(filename)

        token = preferences.userPrefs.get("user_info", "flickr_token")

        id = flickr.upload(
            filename,
            token,
            title=self.title_entry.get_text(),
            description=self.get_description(),
            tags=self.get_tags())

        #print id

    def onViewMy(self,widget):
        global TOKEN
        url = flickr.urls_getUserPhotos(TOKEN.user.nsid)
        launch_browser(url,self.main_window)

    def onViewPool(self,widget):
        launch_browser("http://flickr.com/groups/gnofract4d/pool/",self.main_window)
    
class FlickrAssistantDialog(dialog.T):
    def show(parent, alt_parent, f,dialog_mode):
        dialog.T.reveal(FlickrAssistantDialog,dialog_mode, parent, alt_parent, f)
            
    show = staticmethod(show)

    intro_text=_("""Flickr is an online image-sharing service. If you like, Gnofract 4D can post your fractal images to the service so others can see them.

In order to post images to Flickr, you first need to have a Flickr account, and then authorize Gnofract 4D to post images for you.

To set that up, please click on the following link and follow the instructions on-screen. When done, close the browser window and click OK.

""")

    
    def __init__(self, main_window, f):
        dialog.T.__init__(
            self,
            _("Flickr Integration Setup"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE,
             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.main_window = main_window

        self.textview = gtk.TextView()
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.textbuffer = self.textview.get_buffer()

        self.frob = flickr.getFrob()
        self.auth_url = flickr.getAuthUrl(self.frob)

        self.href_tag = self.textbuffer.create_tag(
            "href",foreground="blue",underline=pango.UNDERLINE_SINGLE)
        
        self.textbuffer.set_text(FlickrAssistantDialog.intro_text,-1)
        self.textbuffer.insert_with_tags(self.textbuffer.get_end_iter(),self.auth_url,self.href_tag)

        self.textview.connect("button_release_event",self.onClick)
        self.vbox.pack_start(self.textview)

        self.set_size_request(500,400)

    def onClick(self, widget, event):
        if event.button!=1:
            return
        
        (x,y) = (event.x, event.y)
        (bx, by) = widget.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT,int(x),int(y))
        
        iter = widget.get_iter_at_location(bx,by)

        if not iter.has_tag(self.href_tag):
            # click wasn't on a URL 
            return

        # user clicked on URL, launch browser
        launch_browser(self.auth_url, self.main_window)

    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        elif id == gtk.RESPONSE_ACCEPT:
            self.onAccept()

    def onAccept(self):
        try:
            token = flickr.getToken(self.frob)
        except flickr.FlickrError, err:
            msg = hint = _("Make sure you followed the link and authorized access.\n") + str(err) 
            d = hig.ErrorAlert(
                _("Flickr returned an error."),
                msg,
                self.main_window)
            
            d.run()
            d.destroy()
            return

        preferences.userPrefs.set("user_info", "flickr_token",token.token) 
        self.hide()
