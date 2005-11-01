# a series of dialogs for negotiating flickr's authorization process
# and uploading images

import os
import re

import gtk, pango

import dialog
import browser
import utils
import preferences
import hig
import random

from fractutils import flickr, slave

TOKEN = None

class FlickrGTKSlave(slave.GTKSlave):
    def __init__(self,cmd,*args):
        slave.GTKSlave.__init__(self,cmd,*args)
    def response(self):
        return flickr.parseResponse(self.output)
            
def is_authorized():
    global TOKEN
    token = preferences.userPrefs.get("user_info", "flickr_token")
    if token == "":
        return False

    try:
        TOKEN = flickr.checkToken(token)
    except flickr.FlickrError, err:
        return False

    return True

def show_flickr_assistant(parent,alt_parent, f,dialog_mode):
    #if is_authorized():
    #    FlickrUploadDialog.show(parent,alt_parent,f,dialog_mode)
    #else:
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
        table.attach(self.upload_button, 0,2,3,4,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.view_my_button = gtk.Button(_("View _My Fractals"))
        self.view_my_button.connect("clicked", self.onViewMy)
        table.attach(self.view_my_button, 0,1,4,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.view_group_button = gtk.Button(_("View G_roup Fractals"))
        self.view_group_button.connect("clicked", self.onViewPool)
        table.attach(self.view_group_button, 1,2,4,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        self.blogs = self.get_blogs()

        self.blog_menu = utils.create_option_menu(
            [_("<None>")] + [b.name for b in self.blogs])

        table.attach(self.blog_menu, 1,2,5,6,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        
    def onResponse(self,widget,id):
        self.hide()

    def get_description(self):
        buffer = self.description.get_buffer()
        return buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())

    def get_blogs(self):
        token = preferences.userPrefs.get("user_info", "flickr_token")
        return flickr.blogs_getList(token)
            
    def get_tags(self):
        formula_tag = FlickrUploadDialog.clean_formula_re.sub('',self.f.funcName)
        return "fractal gnofract4d %s %s" % (formula_tag,self.tags.get_text())
        
    def onUpload(self,widget):
        filename = "/tmp/%d.png" % int(random.uniform(0,1000000))
        self.f.save_image(filename)

        token = preferences.userPrefs.get("user_info", "flickr_token")

        title_ = self.title_entry.get_text()
        description_ = self.get_description()
        id = flickr.upload(
            filename,
            token,
            title=title_,
            description=description_,
            tags=self.get_tags())

        flickr.groups_pools_add(id,token)

        selected_blog = utils.get_selected(self.blog_menu)
        if selected_blog > 0:
            blog = self.blogs[selected_blog-1]
            flickr.blogs_postPhoto(
                blog, id, title_,description_,token)

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

In order to post images to Flickr, you first need to have a Flickr account, and then authorize Gnofract 4D to post images for you. You only need to do this once.

To set that up, please click on the following link and follow the instructions on-screen. When done, close the browser window and click Next.

""")

    success_text=_("""Congratulations, you've successfully authorized Gnofract 4D to access Flickr. Your user details are:

   Username : %s
   Full Name : %s

Click Finish to save your credentials and proceed.""")
    

    NEXT=1
    FINISH=2
    def __init__(self, main_window, f):
        dialog.T.__init__(
            self,
            _("Flickr Integration Setup"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE,
             _("_Next"), FlickrAssistantDialog.NEXT))

        self.main_window = main_window

        self.textview = gtk.TextView()
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.textbuffer = self.textview.get_buffer()
        self.textview.connect("button_release_event",self.onClick)
        self.vbox.pack_start(self.textview)

        self.bar = gtk.ProgressBar()
        self.vbox.pack_end(self.bar,False,False)

        req = flickr.requestFrob()
        self.runRequest(req,self.onFrobReceived)

        self.set_size_request(500,400)

    def runRequest(self,req,on_done):
        self.slave = FlickrGTKSlave(req.cmd,*req.args)
        self.slave.connect('progress-changed',self.onProgress)
        self.slave.connect('operation-complete', on_done)
        self.slave.run(req.input)
        
    def onProgress(self,slave,type,position):
        print "progress", type
        if position == -1.0:
            self.bar.pulse()
        else:
            self.bar.set_fraction(position)
        self.bar.set_text(type)
        return True

    def onFrobReceived(self,slave):
        print "frob received"
        self.frob = flickr.parseFrob(self.slave.response())

        # now display auth screen
        self.auth_url = flickr.getAuthUrl(self.frob)

        self.href_tag = self.textbuffer.create_tag(
            "href",foreground="blue",underline=pango.UNDERLINE_SINGLE)
        
        self.textbuffer.set_text(FlickrAssistantDialog.intro_text,-1)
        self.textbuffer.insert_with_tags(
            self.textbuffer.get_end_iter(),
            self.auth_url,self.href_tag)

        self.vbox.show_all()
        
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
        elif id == FlickrAssistantDialog.NEXT:
            self.onCheck()
        elif id == FlickrAssistantDialog.FINISH:
            self.onAccept()

    def onCheck(self):
        req = flickr.requestToken(self.frob)
        self.runRequest(req,self.onTokenReceived)

    def onTokenReceived(self,slave):
        try:
            self.token = flickr.parseToken(slave.response())
        except flickr.FlickrError, err:
            msg = _("Make sure you followed the link and authorized access.\n") + str(err) 
            d = hig.ErrorAlert(
                _("Flickr returned an error."),
                msg,
                self.main_window)
            
            d.run()
            d.destroy()
            return

        # update window with results
        username, fullname = self.token.user.username, self.token.user.fullname
        success_text = FlickrAssistantDialog.success_text % (username, fullname)
        self.textbuffer.set_text(success_text,-1)

        # hide Next, show Finish
        self.set_response_sensitive(FlickrAssistantDialog.NEXT, False)
        self.add_button(_("_Finish"), FlickrAssistantDialog.FINISH)
        
        
    def onAccept(self):
        preferences.userPrefs.set("user_info", "flickr_token",self.token.token) 
        self.hide()
