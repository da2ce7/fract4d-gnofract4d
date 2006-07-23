#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2006  Branko Kokanovic
#
#   AVIGen.py: generates AVI from transcode software
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#                                                                             
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#                                                                             
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import gtk
import gobject
import os
import re
from threading import *

from DirectorBean import *

class AVIGeneration:
	
	def __init__(self,dir_bean,parent):
		self.dialog=gtk.Dialog("Generating AVI file...",parent,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
		self.pbar = gtk.ProgressBar()
		self.pbar.set_text("Please wait...")
		self.dialog.vbox.pack_start(self.pbar,True,True,0)
		self.dialog.set_geometry_hints(None,min_aspect=3.5,max_aspect=3.5)
		self.dir_bean=dir_bean
		self.parent=parent
		self.delete_them=-1
			
	def generate_avi(self):
		#-------getting all needed information------------------------------
		folder_png=self.dir_bean.get_png_dir()
		if folder_png[-1]!="/":
			folder_png=folder_png+"/"
			
		avi_file=self.dir_bean.get_avi_file()
		width=self.dir_bean.get_width()
		height=self.dir_bean.get_height()
		framerate=self.dir_bean.get_framerate()
		yield True
		#------------------------------------------------------------------
		
		try:
			if self.running==False:
				yield False
				return

			if not(os.path.exists(folder_png+"list")): #check if image listing already exist
					gtk.threads_enter()
					error_dlg = gtk.MessageDialog(self.dialog,
						gtk.DIALOG_MODAL  | gtk.DIALOG_DESTROY_WITH_PARENT,
						gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
						"In directory: %s there is no listing file. Cannot continue" %(folder_png))
					response=error_dlg.run()
					error_dlg.destroy()
					gtk.threads_leave()
					event = gtk.gdk.Event(gtk.gdk.DELETE)
					self.dialog.emit('delete_event', event)
					yield False
					return
			#--------calculating total number of frames------------
			count=self.dir_bean.get_base_stop()
			for i in range(self.dir_bean.keyframes_count()):
				count=count+self.dir_bean.get_keyframe_duration(i)
				count=count+self.dir_bean.get_keyframe_stop(i)-1
			#------------------------------------------------------
			#calling transcode
			swap=""
			if self.dir_bean.get_redblue():
				swap="-k"
				
			call="transcode -z -i %slist -x imlist,null -g %dx%d -y ffmpeg,null -F mpeg4 -f %d -o %s -H 0 --use_rgb %s 2>/dev/null"%(folder_png,width,height,framerate,avi_file,swap)
			dt=DummyThread(call,self.pbar,float(count))
			dt.start()

			radi=True
			while(radi):
				dt.join(0.5) #refresh gtk every 0.5 seconds
				radi=dt.isAlive()
				yield True

			if self.running==False:
				yield False
				return
			yield True
		except:
			self.running=False
			self.error=True
			gtk.threads_enter()
			error_dlg = gtk.MessageDialog(self.dialog,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"Unknown error during generation of avi file")
			error_dlg.run()
			error_dlg.destroy()
			gtk.threads_leave()
			event = gtk.gdk.Event(gtk.gdk.DELETE)
			self.dialog.emit('delete_event', event)
			yield False
			return
		if self.running==False:
			yield False
			return
		self.running=False
		self.dialog.destroy()
		yield False


	def show(self):
		#---------checking if there are transcode in PATH------------
		found=False
		env=os.environ['PATH']
		for d in env.split(':'):
			if found:
				break
			if 'transcode' in os.listdir(d):
				found=True
		if not found:
			gtk.threads_enter()
			error_dlg = gtk.MessageDialog(self.dialog,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"transcode not found in PATH. Make sure you installed it. I will not continue")
			error_dlg.run()
			error_dlg.destroy()
			gtk.threads_leave()
			self.dialog.destroy()
			return -1
		#------------------------------------------------------------
		self.dialog.show_all()
		self.running=True
		self.error=False
		task=self.generate_avi()
		gobject.idle_add(task.next)
		response = self.dialog.run()
		if response != gtk.RESPONSE_CANCEL:
			if self.running==True: #destroy by user
				self.running=False
				self.dialog.destroy()
				return 1
			else:
				if self.error==True: #error
					self.dialog.destroy()
					return -1
				else: #everything ok
					self.dialog.destroy()
					return 0
		else: #cancel pressed
			self.running=False
			self.dialog.destroy()
			return 1
		
#thread for calling transcode
class DummyThread(Thread):
	def __init__(self,s,pbar,count):
		Thread.__init__(self)
		self.s=s
		self.pbar=pbar
		self.count=count
	
	def run(self):
		#os.system(self.s) <----this is little faster, but user can't see any progress
		reg=re.compile("\[.*-.*\]")
		pipe=os.popen(self.s)
		for line in pipe:
			m=reg.search(line)
			if m!=None:
				cur=re.split("-",m.group())[1][0:-1]
				self.pbar.set_fraction(float(cur)/self.count)
		return
