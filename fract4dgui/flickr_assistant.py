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
        if self.process.returncode:
            # an error occurred
            raise Exception("An error occurred:\n%s" % self.err_output)
        return flickr.parseResponse(self.output)            
        
def is_authorized():
    global TOKEN
    TOKEN = preferences.userPrefs.get("user_info", "flickr_token")
    if TOKEN == "":
        return False

    return True

def get_user(window, f):
    if not is_authorized():
        d = FlickrAssistantDialog(window, f)
        d.run()
    return preferences.userPrefs.get("user_info", "nsid")

def show_flickr_assistant(parent,alt_parent, f,dialog_mode):
    if is_authorized():
        FlickrUploadDialog.show(parent,alt_parent,f,dialog_mode)
    else:
        FlickrAssistantDialog.show(parent,alt_parent, f,True)

def display_flickr_error(err):
    d = hig.ErrorAlert(
        _("Flickr Error"),
        str(err),
        None)
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
            _("Upload to Flickr"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.f = f
        self.main_window = main_window
        self.controls = gtk.VBox()
        self.vbox.pack_start(self.controls)
        self.slave = None
        
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

        self.include_params = gtk.CheckButton(
            _("_Include parameters in description"))
        table.attach(self.include_params,0,2,3,4,gtk.EXPAND | gtk.FILL, 0, 2, 2)
                     
        self.upload_button = gtk.Button(_("_Upload"))
        self.upload_button.connect("clicked", self.onUpload)
        table.attach(self.upload_button, 0,2,4,5,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.cancel_button = gtk.Button(_("_Cancel Upload"))
        self.cancel_button.connect("clicked", self.onCancelUpload)
        table.attach(self.cancel_button, 0,2,5,6,gtk.EXPAND | gtk.FILL, 0, 2, 2)
        self.set_upload_mode(True)
        
        #self.view_my_button = gtk.Button(_("View _My Fractals"))
        #self.view_my_button.connect("clicked", self.onViewMy)
        #table.attach(
        #    self.view_my_button,
        #    0,1,4,5,
        #    gtk.EXPAND | gtk.FILL, 0, 2, 2)
        #
        #self.view_group_button = gtk.Button(_("View G_roup Fractals"))
        #self.view_group_button.connect("clicked", self.onViewPool)
        #table.attach(
        #    self.view_group_button,
        #    1,2,4,5,
        #    gtk.EXPAND | gtk.FILL, 0, 2, 2)

        #self.blog_menu = utils.create_option_menu([_("<None>")]) 

        #self.blogs = self.get_blogs()
        
        #table.attach(self.blog_menu, 1,2,6,7,gtk.EXPAND | gtk.FILL, 0, 2, 2)

        self.bar = gtk.ProgressBar()
        self.vbox.pack_end(self.bar,False,False)

    def init_title(self):
        pass
    
    def runRequest(self,req,on_done):
        self.slave = FlickrGTKSlave(req.cmd,*req.args)
        self.slave.connect('progress-changed',self.onProgress)
        self.slave.connect('operation-complete', on_done)
        self.slave.run(req.input)
        
    def onProgress(self,slave,type,position):
        if position == -1.0:
            self.bar.pulse()
        else:
            self.bar.set_fraction(position)
        self.bar.set_text(type)
        return True

    def onCancelUpload(self,button):
        if self.slave:
            self.slave.terminate()
        button.set_sensitive(False)
        
    def onResponse(self,widget,id):
        self.hide()

    def get_description(self):
        buffer = self.description.get_buffer()
        description =  buffer.get_text(
            buffer.get_start_iter(),buffer.get_end_iter())

        if self.include_params.get_active():
            description += "\n-----------------------------------\n"
            description += self.f.serialize()

        return description
    
    def get_blogs(self):
        global TOKEN
        req = flickr.requestBlogsGetList(token)
        self.runRequest(req,onBlogsFetched)

    def onBlogsFetched(self,slave):
        blogs = flickr.parseBlogsList(slave.response())
        
    def get_tags(self):
        formula_tag = FlickrUploadDialog.clean_formula_re.sub('',self.f.funcName)
        return "fractal gnofract4d %s %s" % (formula_tag,self.tags.get_text())

    def set_upload_mode(self,is_upload):
        self.cancel_button.set_sensitive(not is_upload)
        self.upload_button.set_sensitive(is_upload)
        
    def onUpload(self,widget):
        global TOKEN
        filename = "/tmp/%d.png" % int(random.uniform(0,1000000))
        self.f.save_image(filename)

        title_ = self.title_entry.get_text()
        description_ = self.get_description()
        req = flickr.requestUpload(
            filename,
            TOKEN,
            title=title_,
            description=description_,
            tags=self.get_tags())

        self.runRequest(req,self.onUploaded)
        self.set_upload_mode(False)
        
    def onUploaded(self,slave):
        global TOKEN
        try:
            id = flickr.parseUpload(slave.response())
        except Exception,err:
            display_flickr_error(err)
            self.set_upload_mode(True)
            return
        
        req = flickr.requestGroupsPoolsAdd(id,TOKEN)

        self.runRequest(req,self.onPoolAdded)

    def onPoolAdded(self,slave):
        try:
            dummy = slave.response() # just to detect errors
        except Exception,err:
            display_flickr_error(err)
        
	#selected_blog = utils.get_selected(self.blog_menu)
	#if selected_blog > 0:
	#    blog = self.blogs[selected_blog-1]
	#    flickr.blogs_postPhoto(
	#        blog, id, title_,description_,token)
	#
        #print id
        self.set_upload_mode(True)
        
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
        if position == -1.0:
            self.bar.pulse()
        else:
            self.bar.set_fraction(position)
        self.bar.set_text(type)
        return True

    def onFrobReceived(self,slave):
        try:
            self.frob = flickr.parseFrob(self.slave.response())
        except Exception,err:
            display_flickr_error(err)
            return

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
        utils.launch_browser(
            preferences.userPrefs, self.auth_url, self.main_window)

    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.slave.terminate()
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
        except Exception,err:
            display_flickr_error(err)
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
        preferences.userPrefs.set("user_info", "nsid", self.token.user.nsid)
        self.hide()
