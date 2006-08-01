#UI for gathering needed data and storing them in director bean class
#then it calls PNGGeneration, and (if everything was OK) AVIGeneration

#TODO: change default directory when selecting new according to already set item
#(for temp dirs, avi and fct files selections)

import gtk
import gobject
import os
import fnmatch
import pickle
import sys
import tempfile

import dialog
from fract4d import directorbean

import PNGGen,AVIGen,DlgAdvOpt,director_prefs

VERSION="0.13b"

def show(parent,alt_parent, f,dialog_mode,conf_file=""):
    DirectorDialog.show(parent,alt_parent, f,dialog_mode,conf_file)

class DirectorDialog(dialog.T):
	def show(parent, alt_parent, f,dialog_mode,conf_file):
		dialog.T.reveal(DirectorDialog, dialog_mode, parent, alt_parent, f,conf_file)

	show = staticmethod(show)

	#returns -1 if there was problem, 0 otherwise
	def check_sanity(self):
		try:
			#check if base keyframe has been set
			if self.dir_bean.get_base_keyframe()=="":
				error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"Base keyframe not set")
				error_dlg.run()
				error_dlg.destroy()
				return -1
			#check if at least one keyframe exist
			if self.dir_bean.keyframes_count()<1:
				error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"There must be at least one keyframe")
				error_dlg.run()
				error_dlg.destroy()
				return -1
			#check png temp dir is set
			if self.dir_bean.get_png_dir()=="":
				error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"Directory for temporary .png files not set")
				error_dlg.run()
				error_dlg.destroy()
				return -1
			#check if it is directory
			if not os.path.isdir(self.dir_bean.get_png_dir()):
				error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"Directory for temporary .png files is not directory")
				error_dlg.run()
				error_dlg.destroy()
				return -1
			#check avi file is set
			if self.dir_bean.get_avi_file()=="":
				error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"Directory for resulting avi file not set")
				error_dlg.run()
				error_dlg.destroy()
				return -1
			#things to check with fct temp dir
			if self.dir_bean.get_fct_enabled()==True:
				#check fct temp dir is set
				if self.dir_bean.get_fct_dir()=="":
					error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
												gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
												"Directory for temporary .fct files not set")
					error_dlg.run()
					error_dlg.destroy()
					return -1
				#check if it is directory
				if not os.path.isdir(self.dir_bean.get_fct_dir()):
					error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
												gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
												"Directory for temporary .fct files is not directory")
					error_dlg.run()
					error_dlg.destroy()
					return -1
				fct_path=self.dir_bean.get_fct_dir()
				if fct_path[-1]!="/":
					fct_path=fct_path+"/"
				#chech if any keyframe fct files are in temp fct dir
				for i in range(self.dir_bean.keyframes_count()):
					k=os.path.split(self.dir_bean.get_keyframe_filename(i))[0]
					if k[-1]!="/":
						k=k+"/"
						if k==fct_path:
							error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
														gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
														"OMG! Keyframe %s resides in temporary .fct directory. I refuse to continue."%(self.dir_bean.get_keyframe_filename(i)))
							error_dlg.run()
							error_dlg.destroy()
							return -1
				#check if base keyframe is in temp fct dir
				k=os.path.split(self.dir_bean.get_base_keyframe())[0]
				if k[-1]!="/":
					k=k+"/"
					if k==fct_path:
						error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
													gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
													"OMG! Base keyframe resides in temporary .fct directory. I refuse to continue.")
						error_dlg.run()
						error_dlg.destroy()
						return -1
				#check if there are any .fct files in temp fct dir
				has_any=False
				for file in os.listdir(fct_path):
					if has_any:
						break
					if fnmatch.fnmatch(file,"*.fct"):
						has_any=True
				if has_any:
					error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
												gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
												"Directory for temporary .fct files contains other .fct files. Is it OK to delete them?")
					response=error_dlg.run()
					error_dlg.destroy()
					if response==gtk.RESPONSE_YES:
						for file in os.listdir(fct_path):
							if fnmatch.fnmatch(file,"*.fct"):
								os.unlink(fct_path+file)
					else:
						return -1
		except:
			error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK,
				"Unknown error occured. I will not continue. Contact author:)")
			response=error_dlg.run()
			error_dlg.destroy()
			return -1
		return 0

	#wrapper to show dialog for selecting .fct file
	#returns selected file or empty string
	def get_fct_file(self):
		temp_file=""
		dialog = gtk.FileChooserDialog("Choose keyframe...",None,gtk.FILE_CHOOSER_ACTION_OPEN,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		#----setting filters---------
		filter = gtk.FileFilter()
		filter.set_name("gnofract4d files (*.fct)")
		filter.add_pattern("*.fct")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		#----------------------------
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			temp_file=dialog.get_filename()
		dialog.destroy()
		return temp_file

	#wrapper to show dialog for selecting .avi file
	#returns selected file or empty string
	def get_avi_file(self):
		temp_file=""
		dialog = gtk.FileChooserDialog("Save AVI file...",None,gtk.FILE_CHOOSER_ACTION_SAVE,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			temp_file=dialog.get_filename()
		dialog.destroy()
		return temp_file

	#wrapper to show dialog for selecting .cfg file
	#returns selected file or empty string
	def get_cfg_file_save(self):
		temp_file=""
		dialog = gtk.FileChooserDialog("Save animation...",None,gtk.FILE_CHOOSER_ACTION_SAVE,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_current_name("animation.fcta")
		#----setting filters---------
		filter = gtk.FileFilter()
		filter.set_name("gnofract4d animation files (*.fcta)")
		filter.add_pattern("*.fcta")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		#----------------------------
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			temp_file=dialog.get_filename()
		dialog.destroy()
		return temp_file

	#wrapper to show dialog for selecting .fct file
	#returns selected file or empty string
	def get_cfg_file_open(self):
		temp_file=""
		dialog = gtk.FileChooserDialog("Choose animation...",None,gtk.FILE_CHOOSER_ACTION_OPEN,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		#----setting filters---------
		filter = gtk.FileFilter()
		filter.set_name("gnofract4d animation files (*.fcta)")
		filter.add_pattern("*.fcta")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		#----------------------------
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			temp_file=dialog.get_filename()
		#elif response == gtk.RESPONSE_CANCEL:
		#	print 'Closed, no files selected'
		dialog.destroy()
		return temp_file

	def temp_avi_clicked(self,widget, data=None):
		avi=self.get_avi_file()
		if avi!="":
			self.txt_temp_avi.set_text(avi)
			self.dir_bean.set_avi_file(avi)

	def output_width_changed(self,widget,data=None):
		self.dir_bean.set_width(self.spin_width.get_value())

	def output_height_changed(self,widget,data=None):
		self.dir_bean.set_height(self.spin_height.get_value())

	def output_framerate_changed(self,widget,data=None):
		self.dir_bean.set_framerate(self.spin_framerate.get_value())

	def duration_changed(self,widget, data=None):
		if self.current_select==-1:
			return
		self.dir_bean.set_keyframe_duration(self.current_select,int(self.spin_duration.get_value()))
		self.update_model()

	def stop_changed(self,widget, data=None):
		if self.current_select==-1:
			return
		self.dir_bean.set_keyframe_stop(self.current_select,int(self.spin_kf_stop.get_value()))
		self.update_model()

	def base_stop_changed(self,widget, data=None):
		self.dir_bean.set_base_stop(int(self.spin_base_stop.get_value()))

	def interpolation_type_changed(self,widget,data=None):
		if self.current_select==-1:
			return
		self.dir_bean.set_keyframe_int(self.current_select,int(self.cmb_interpolation_type.get_active()))
		self.update_model()

	#point of whole program:)
	#first we generate  png files and list, then .avi
	def generate(self,create_avi=True):
		if self.check_sanity()!=0:
			return
		png_gen=PNGGen.PNGGeneration(self.dir_bean)
		res=png_gen.show()
		if res==1:
			gtk.threads_enter()
			error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
					"User canceled")
			error_dlg.run()
			error_dlg.destroy()
			gtk.threads_leave()
			return
		elif res!=0:
			return

		if create_avi==False:
			return
		avi_gen=AVIGen.AVIGeneration(self.dir_bean)
		res=avi_gen.show()
		if res==1:
			gtk.threads_enter()
			error_dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
					"User canceled (but avi file is still generating, check later if it exist?)")
			error_dlg.run()
			error_dlg.destroy()
			gtk.threads_leave()
			return
		elif res==0:
			dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
					"AVI file created! Check to see what it looks like now;)")
			dlg.run()
			dlg.destroy()
		else:
			return

	def generate_clicked(self, widget, data=None):
		self.generate(True)

	def adv_opt_clicked(self,widget,data=None):
		if self.current_select==-1:
			return
		dlg=DlgAdvOpt.DlgAdvOptions(self.current_select,self.dir_bean)
		res=dlg.show()

	#before selecting keyframes in list box we must update values of spin boxes in case user typed something in there
	def before_selection(self,selection, data=None):
		self.spin_duration.update()
		self.spin_kf_stop.update()
		return True

	#update right box (duration, stop, interpolation type) when keyframe is selected from list
	def selection_changed(self,widget, data=None):
		(model,it)=self.tv_keyframes.get_selection().get_selected()
		if it!=None:
			#------getting index of selected row-----------
			index=0
			it=model.get_iter_first()
			while it!=None:
				if self.tv_keyframes.get_selection().iter_is_selected(it):
					break
				it=model.iter_next(it)
				index=index+1
			self.current_select=index
			self.spin_duration.set_value(int(self.dir_bean.get_keyframe_duration(index)))
			self.spin_kf_stop.set_value(self.dir_bean.get_keyframe_stop(index))
			self.cmb_interpolation_type.set_active(self.dir_bean.get_keyframe_int(index))
			return
		else:
			self.spin_duration.set_value(25)
			self.spin_kf_stop.set_value(1)
			self.cmb_interpolation_type.set_active(directorbean.INT_LINEAR)
			self.current_select=-1

	def update_model(self):
		(model,it)=self.tv_keyframes.get_selection().get_selected()
		if it!=None:
			#------getting index of selected row-----------
			index=0
			it=model.get_iter_first()
			while it!=None:
				if self.tv_keyframes.get_selection().iter_is_selected(it):
					break
				it=model.iter_next(it)
				index=index+1

			model.set(it,1,self.dir_bean.get_keyframe_duration(index))
			model.set(it,2,self.dir_bean.get_keyframe_stop(index))
			int_type=self.dir_bean.get_keyframe_int(index)
			if int_type==directorbean.INT_LINEAR:
				model.set(it,3,"Linear")
			elif int_type==directorbean.INT_LOG:
				model.set(it,3,"Logarithmic")
			elif int_type==directorbean.INT_INVLOG:
				model.set(it,3,"Inverse logarithmic")
			else:
				model.set(it,3,"Cosine")

	def swap_redblue_clicked(self,widget,data=None):
		self.dir_bean.set_redblue(self.chk_swapRB.get_active())

	def add_from_file(self,widget,data=None):
		file=self.get_fct_file()
		if file!="":
			self.add_keyframe(file)

	def add_from_file_bk(self,widget,data=None):
		file=self.get_fct_file()
		if file!="":
			self.add_basekeyframe(file)

	def add_from_current(self,widget,data=None):
		(tmp_fd, tmp_name) = tempfile.mkstemp(suffix='.fct')
		f = os.fdopen(tmp_fd, 'w')
		self.f.save(f)
		self.add_keyframe(tmp_name)
		return

	def add_from_current_bk(self,widget,data=None):
		(tmp_fd, tmp_name) = tempfile.mkstemp(suffix='.fct')
		f = os.fdopen(tmp_fd, 'w')
		self.f.save(f)
		self.add_basekeyframe(tmp_name)
		return

	def add_keyframe(self,file):
		if file!="":
			#get current seletion
			(model,it)=self.tv_keyframes.get_selection().get_selected()
			if it==None: #if it's none, just append at the end of the list
				it=model.append([file,25,1,"Linear"])
			else: #append after currently selected
				it=model.insert_after(it,[file,25,1,"Linear"])

			#add to bean with default parameters
			if self.current_select!=-1:
				self.dir_bean.add_keyframe(file,25,1,directorbean.INT_LINEAR,self.current_select+1)
			else:
				self.dir_bean.add_keyframe(file,25,1,directorbean.INT_LINEAR)
			#and select newly item
			self.tv_keyframes.get_selection().select_iter(it)
			#set default duration
			self.spin_duration.set_value(25)
			#set default stop
			self.spin_kf_stop.set_value(1)
			#set default interpolation type
			self.cmb_interpolation_type.set_active(directorbean.INT_LINEAR)

	def add_basekeyframe(self,file):
		if file!="":
			self.txt_first_kf.set_text(file)
			self.dir_bean.set_base_keyframe(file)

	def add_keyframe_clicked(self,widget, event):
		if event.type == gtk.gdk.BUTTON_PRESS:
			widget.popup(None, None, None, event.button, event.time)
			# Tell calling code that we have handled this event the buck
			# stops here.
			return True
		# Tell calling code that we have not handled this event pass it on.
		return False

	def add_basekeyframe_clicked(self, widget, event):
		if event.type == gtk.gdk.BUTTON_PRESS:
			widget.popup(None, None, None, event.button, event.time)
			# Tell calling code that we have handled this event the buck
			# stops here.
			return True
		# Tell calling code that we have not handled this event pass it on.
		return False

	def remove_keyframe_clicked(self,widget,data=None):
		#is anything selected
		(model,it)=self.tv_keyframes.get_selection().get_selected()
		if it!=None:
			temp_curr=self.current_select
			model.remove(it)
			self.dir_bean.remove_keyframe(temp_curr)

	def updateGUI(self):
		#base keyframe part
		self.txt_first_kf.set_text(self.dir_bean.get_base_keyframe())
		self.spin_base_stop.set_value(self.dir_bean.get_base_stop())
		#keyframes
		(model,it)=self.tv_keyframes.get_selection().get_selected()
		model.clear()
		for i in range(self.dir_bean.keyframes_count()-1,-1,-1):
			filename=self.dir_bean.get_keyframe_filename(i)
			duration=self.dir_bean.get_keyframe_duration(i)
			stopped=self.dir_bean.get_keyframe_stop(i)
			it=model.insert(0,[filename,duration,stopped,""])
			int_type=self.dir_bean.get_keyframe_int(i)
			if int_type==directorbean.INT_LINEAR:
				model.set(it,3,"Linear")
			elif int_type==directorbean.INT_LOG:
				model.set(it,3,"Logarithmic")
			elif int_type==directorbean.INT_INVLOG:
				model.set(it,3,"Inverse logarithmic")
			else:
				model.set(it,3,"Cosine")
		#output part
		self.txt_temp_avi.set_text(self.dir_bean.get_avi_file())
		self.spin_width.set_value(self.dir_bean.get_width())
		self.spin_height.set_value(self.dir_bean.get_height())
		self.spin_framerate.set_value(self.dir_bean.get_framerate())
		self.chk_swapRB.set_active(self.dir_bean.get_redblue())

	#loads configuration file, returns 0 on ok, -1 on error (and displays error message)
	def load_configuration(self,file):
		if file=="":
			return -1
		result=self.dir_bean.load_animation(file)
		if result==-1:
			dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
								gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
								"Animation file could not be loaded.")
			dlg.run()
			dlg.destroy()
			return -1
		#set GUI to reflect changes
		self.updateGUI()
		return 0

	#loads configuration from pickled file
	def load_configuration_clicked(self,widget,data=None):
		cfg=self.get_cfg_file_open()
		if cfg!="":
			self.load_configuration(cfg)

	#reset all field to defaults
	def new_configuration_clicked(self,widget,data=None):
		self.dir_bean.reset()
		self.updateGUI()

	#save pickled configuration in file
	def save_configuration_clicked(self,widget,data=None):
		cfg=self.get_cfg_file_save()
		if cfg!="":
			#output=open(cfg,"w")
			#pickle.dump(self.dir_bean,output)
			#output.close()
			result=self.dir_bean.save_animation(cfg)
			if result==-1:
				dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
									gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
									"Error during saving animation file")
				dlg.run()
				dlg.destroy()
				return

	def preferences_clicked(self,widget,data=None):
		dlg=director_prefs.DirectorPrefs(self.dir_bean)
		res=dlg.show()

	#creating window...
	def __init__(self, main_window, f,conf_file):
		dialog.T.__init__(
			self,
			_("Director"),
			main_window,
			gtk.DIALOG_DESTROY_WITH_PARENT,
			(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

		self.dir_bean=directorbean.DirectorBean()
		self.f=f
		self.realize()

		#self.window.set_border_width(10)
		#main VBox
		self.box_main=gtk.VBox(False,0)
		#--------------------menu-------------------------------
		self.menu_items = (
			( "/_Director",					None,			None, 0, "<Branch>" ),
			( "/Director/_New animation", 	"<control>N",	self.new_configuration_clicked,	0, None),
			( "/Director/_Load animation",	"<control>O",	self.load_configuration_clicked,0, None ),
			( "/Director/_Save animation",	"<control>S",	self.save_configuration_clicked,0, None ),
			( "/_Edit",						None,			None,							0, "<Branch>"),
			( "/Edit/_Preferences...",		"<control>P",	self.preferences_clicked,		0, None)
			#( "/File/sep1",     None,         None, 0, "<Separator>" ),
			#( "/File/Quit",     "<control>Q", self.quit, 0, None ),
			#( "/_Help",         None,         None, 0, "<LastBranch>" ),
			#( "/_Help/About",   None,         self.about,0, None ),
		)
		accel_group = gtk.AccelGroup()
		self.item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
		self.item_factory.create_items(self.menu_items)
		#self.window.add_accel_group(accel_group)
		self.menubar=self.item_factory.get_widget("<main>")
		self.box_main.pack_start(self.menubar,False,False,0)
		#-------------------------------------------------------------
		#-----------creating popup menu-------------------------------
		#popup menu for keyframes
		self.popup_menu=gtk.Menu()
		self.mnu_pop_add_file=gtk.MenuItem("From file")
		self.popup_menu.append(self.mnu_pop_add_file)
		self.mnu_pop_add_file.connect("activate", self.add_from_file, None)
		self.mnu_pop_add_file.show()
		self.mnu_pop_add_current=gtk.MenuItem("From current fractal")
		self.popup_menu.append(self.mnu_pop_add_current)
		self.mnu_pop_add_current.connect("activate", self.add_from_current, None)
		self.mnu_pop_add_current.show()
		#popup menu for base keyframe
		self.popup_menu_bk=gtk.Menu()
		self.mnu_pop_add_file_bk=gtk.MenuItem("From file")
		self.popup_menu_bk.append(self.mnu_pop_add_file_bk)
		self.mnu_pop_add_file_bk.connect("activate", self.add_from_file_bk, None)
		self.mnu_pop_add_file_bk.show()
		self.mnu_pop_add_current_bk=gtk.MenuItem("From current fractal")
		self.popup_menu_bk.append(self.mnu_pop_add_current_bk)
		self.mnu_pop_add_current_bk.connect("activate", self.add_from_current_bk, None)
		self.mnu_pop_add_current_bk.show()
		#-------------------------------------------------------------
		#-----------------base keyframe box---------------------------
		self.frm_base=gtk.Frame("Base keyframe")
		self.frm_base.set_border_width(10)
		self.tbl_base=gtk.Table(2,3,False)
		self.tbl_base.set_row_spacings(10)
		self.tbl_base.set_col_spacings(10)
		self.tbl_base.set_border_width(10)

		self.lbl_first_kf=gtk.Label("Base keyframe")
		self.tbl_base.attach(self.lbl_first_kf,0,1,0,1)

		self.txt_first_kf=gtk.Entry(0)
		self.txt_first_kf.set_editable(False)
		self.tbl_base.attach(self.txt_first_kf,1,2,0,1)

		self.btn_browse_first_kf=gtk.Button("Set")
		self.btn_browse_first_kf.connect_object("event",self.add_basekeyframe_clicked,self.popup_menu_bk)
		#self.btn_browse_first_kf.connect("clicked",self.browse_base_keyframe,None)
		self.tbl_base.attach(self.btn_browse_first_kf,2,3,0,1)

		self.lbl_first_kf_stopped=gtk.Label("Stopped for:")
		self.tbl_base.attach(self.lbl_first_kf_stopped,0,1,1,2)

		adj_base_stop=gtk.Adjustment(1,1,10000,1,10)
		self.spin_base_stop=gtk.SpinButton(adj_base_stop)
		self.spin_base_stop.connect("output",self.base_stop_changed,None)
		self.tbl_base.attach(self.spin_base_stop,1,2,1,2)

		self.frm_base.add(self.tbl_base)
		self.box_main.pack_start(self.frm_base,False,False,0)
		#--------------------------------------------------------------
		#--------------Keyframes box-----------------------------------
		self.frm_kf=gtk.Frame("Keyframes")
		self.frm_kf.set_border_width(10)
		self.hbox_kfs=gtk.HBox(False,0)
		self.tbl_keyframes_left=gtk.Table(2,2,False)
		self.tbl_keyframes_left.set_row_spacings(10)
		self.tbl_keyframes_left.set_col_spacings(10)
		self.tbl_keyframes_left.set_border_width(10)

		self.sw=gtk.ScrolledWindow()
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#		filenames=gtk.ListStore(gobject.TYPE_STRING,
#            gobject.TYPE_STRING)
#		self.tv_keyframes=gtk.TreeView(filenames)
#		self.tv_column_name = gtk.TreeViewColumn('Keyframes')
#		self.tv_keyframes.append_column(self.tv_column_name)
#		self.tv_column_duration = gtk.TreeViewColumn('Duration')
#		self.tv_keyframes.append_column(self.tv_column_duration)
#		self.cell_name = gtk.CellRendererText()
#		self.tv_column_name.pack_start(self.cell_name, True)
#		self.tv_column_name.add_attribute(self.cell_name, 'text', 0)
#		self.cell_duration = gtk.CellRendererText()
#		self.tv_column_name.pack_start(self.cell_duration, True)
#		self.tv_column_name.add_attribute(self.cell_duration, 'text', 0)
		filenames=gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_UINT,
							gobject.TYPE_UINT, gobject.TYPE_STRING)
		self.tv_keyframes = gtk.TreeView(filenames)
		column = gtk.TreeViewColumn('Keyframes', gtk.CellRendererText(),text=0)
		self.tv_keyframes.append_column(column)

		column = gtk.TreeViewColumn('Duration', gtk.CellRendererText(),text=1)
		self.tv_keyframes.append_column(column)

		column = gtk.TreeViewColumn('Stopped for', gtk.CellRendererText(),text=2)
		self.tv_keyframes.append_column(column)

		column = gtk.TreeViewColumn('Interpolation type', gtk.CellRendererText(),text=3)
		self.tv_keyframes.append_column(column)

		self.sw.add_with_viewport(self.tv_keyframes)
		self.tv_keyframes.get_selection().connect("changed",self.selection_changed,None)
		self.tv_keyframes.get_selection().set_select_function(self.before_selection,None)
		self.current_select=-1
		self.tbl_keyframes_left.attach(self.sw,0,2,0,1)

		self.btn_add_keyframe=gtk.Button("Add",gtk.STOCK_ADD)
		#self.btn_add_keyframe.connect("clicked",self.add_keyframe_clicked,None)
		self.btn_add_keyframe.connect_object("event",self.add_keyframe_clicked,self.popup_menu)
		self.tbl_keyframes_left.attach(self.btn_add_keyframe,0,1,1,2,0,0)

		self.btn_remove_keyframe=gtk.Button("Remove",gtk.STOCK_REMOVE)
		self.btn_remove_keyframe.connect("clicked",self.remove_keyframe_clicked,None)
		self.tbl_keyframes_left.attach(self.btn_remove_keyframe,1,2,1,2,0,0)
		self.hbox_kfs.pack_start(self.tbl_keyframes_left,True,True,10)

		self.tbl_keyframes_right=gtk.Table(4,2,True)
		self.tbl_keyframes_right.set_row_spacings(10)
		self.tbl_keyframes_right.set_col_spacings(10)
		self.tbl_keyframes_right.set_border_width(10)

		self.lbl_duration=gtk.Label("Duration")
		self.tbl_keyframes_right.attach(self.lbl_duration,0,1,0,1)

		adj_duration=gtk.Adjustment(25,1,10000,1,10)
		self.spin_duration=gtk.SpinButton(adj_duration)
		self.spin_duration.connect("output",self.duration_changed,None)
		self.tbl_keyframes_right.attach(self.spin_duration,1,2,0,1)

		self.lbl_kf_stop=gtk.Label("Keyframe stopped for:")
		self.tbl_keyframes_right.attach(self.lbl_kf_stop,0,1,1,2)

		adj_kf_stop=gtk.Adjustment(1,1,10000,1,10)
		self.spin_kf_stop=gtk.SpinButton(adj_kf_stop)
		self.spin_kf_stop.connect("output",self.stop_changed,None)
		self.tbl_keyframes_right.attach(self.spin_kf_stop,1,2,1,2)

		self.lbl_int_type=gtk.Label("Interpolation type:")
		self.tbl_keyframes_right.attach(self.lbl_int_type,0,1,2,3)

		self.cmb_interpolation_type=gtk.combo_box_new_text() #gtk.ComboBox()
		self.cmb_interpolation_type.append_text("Linear")
		self.cmb_interpolation_type.append_text("Logarithmic")
		self.cmb_interpolation_type.append_text("Inverse logarithmic")
		self.cmb_interpolation_type.append_text("Cosine")
		self.cmb_interpolation_type.set_active(0)
		self.cmb_interpolation_type.connect("changed",self.interpolation_type_changed,None)
		self.tbl_keyframes_right.attach(self.cmb_interpolation_type,1,2,2,3)

		self.btn_adv_opt=gtk.Button("Advanced options")
		self.btn_adv_opt.connect("clicked",self.adv_opt_clicked,None)
		self.tbl_keyframes_right.attach(self.btn_adv_opt,0,2,3,4)

		self.hbox_kfs.pack_start(self.tbl_keyframes_right,False,False,10)
		self.frm_kf.add(self.hbox_kfs)
		self.box_main.pack_start(self.frm_kf,True,True,0)
		#-------------------------------------------------------------------
		#----------------------output box-----------------------------------
		self.frm_output=gtk.Frame("Output options")
		self.frm_output.set_border_width(10)

		self.box_output_main=gtk.VBox(True,10)
		self.box_output_file=gtk.HBox(False,10)

		self.lbl_temp_avi=gtk.Label("Resulting video file:")
		self.box_output_file.pack_start(self.lbl_temp_avi,False,False,10)

		self.txt_temp_avi=gtk.Entry(0)
		self.txt_temp_avi.set_editable(False)
		self.box_output_file.pack_start(self.txt_temp_avi,True,True,10)

		self.btn_temp_avi=gtk.Button("Browse")
		self.btn_temp_avi.connect("clicked",self.temp_avi_clicked,None)
		self.box_output_file.pack_start(self.btn_temp_avi,True,True,10)

		self.box_output_main.pack_start(self.box_output_file,True,True,0)

		self.box_output_res=gtk.HBox(False,10)

		self.lbl_res=gtk.Label("Resolution:")
		self.box_output_res.pack_start(self.lbl_res,False,False,10)

		adj_width=gtk.Adjustment(640,320,2048,10,100,0)
		self.spin_width=gtk.SpinButton(adj_width)
		self.spin_width.connect("output",self.output_width_changed,None)
		self.box_output_res.pack_start(self.spin_width,False,False,10)

		self.lbl_x=gtk.Label("x")
		self.box_output_res.pack_start(self.lbl_x,False,False,10)

		adj_height=gtk.Adjustment(480,240,1536,10,100,0)
		self.spin_height=gtk.SpinButton(adj_height)
		self.spin_height.connect("output",self.output_height_changed,None)
		self.box_output_res.pack_start(self.spin_height,False,False,10)

		self.box_output_main.pack_start(self.box_output_res,True,True,0)

		self.box_output_framerate=gtk.HBox(False,10)

		self.lbl_framerate=gtk.Label("Frame rate:")
		self.box_output_framerate.pack_start(self.lbl_framerate,False,False,10)

		adj_framerate=gtk.Adjustment(25,5,100,1,5,0)
		self.spin_framerate=gtk.SpinButton(adj_framerate)
		self.spin_framerate.connect("output",self.output_framerate_changed,None)
		self.box_output_framerate.pack_start(self.spin_framerate,False,False,10)

		self.chk_swapRB=gtk.CheckButton("Swap red and blue component")
		self.chk_swapRB.set_active(True)
		self.chk_swapRB.connect("toggled",self.swap_redblue_clicked,None)
		self.box_output_framerate.pack_start(self.chk_swapRB,False,False,50)

		self.box_output_main.pack_start(self.box_output_framerate,True,True,0)

		self.frm_output.add(self.box_output_main)
		self.box_main.pack_start(self.frm_output,False,False,0)
		#-----------------------------------------------------------------
		#------------------button box-------------------------------------
		self.box_buttons=gtk.HBox(False,10)

		self.btn_generate = gtk.Button("Render")
		self.btn_generate.connect("clicked", self.generate_clicked, None)
		self.box_buttons.pack_start(self.btn_generate,True,False,0)

		#self.btn_exit=gtk.Button("Exit",gtk.STOCK_QUIT)
		#self.btn_exit.connect("clicked", self.quit,1)
		#self.box_buttons.pack_start(self.btn_exit,True,False,0)

		self.box_main.pack_start(self.box_buttons,False,False,10)
		#--------------showing all-------------------------------
		self.vbox.add(self.box_main)
		self.controls = self.vbox
		if conf_file!="":
			self.load_configuration(conf_file)


	def main(self):
		gtk.main()


if __name__ == "__main__":
	gobject.threads_init()
	gtk.threads_init()
	fracwin = DirectorDialog()
	fracwin.main()
