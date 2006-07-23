#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2006  Branko Kokanovic
#
#   PNGGen.py: generates PNG images
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
from threading import *

from DirectorBean import *

class PNGGeneration:
	
	def __init__(self,dir_bean,parent):
		self.dialog=gtk.Dialog("Generating PNG images...",parent,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
		self.pbar = gtk.ProgressBar()
		self.dialog.vbox.pack_start(self.pbar,True,True,0)
		self.dialog.set_geometry_hints(None,min_aspect=3.5,max_aspect=3.5)
		self.dir_bean=dir_bean
		self.parent=parent
		self.delete_them=-1
			
	def generate_png(self):
		#-------getting all needed information------------------------------
		#getting all durations, needed for progress and where to stop generating images
		self.durations=[]
		for i in range(self.dir_bean.keyframes_count()):
			self.durations.append(self.dir_bean.get_keyframe_duration(i))
		
		
		sumN=sum(self.durations)
		lenN=len(str(sumN))
		
		folder_fct=self.dir_bean.get_fct_dir()
		if folder_fct[-1]!="/":
			folder_fct=folder_fct+"/"
			
		folder_png=self.dir_bean.get_png_dir()
		if folder_png[-1]!="/":
			folder_png=folder_png+"/"
			
		width=self.dir_bean.get_width()
		height=self.dir_bean.get_height()
		#--------------------------------------------------------------------
		#first show
		self.pbar.set_fraction(0)
		self.pbar.set_text("0/"+str(sumN+1))
		yield True
		
		try:
			##-----------------creating images---------------------------
			for i in range(sumN+1):
				if self.running==False:
					yield False
					break
				
				create=True
				if os.path.exists(folder_png+"image_"+str(i).zfill(lenN)+".png"): #check if image already exist
					if self.delete_them==-1: #check to see if we got an answer
						gtk.threads_enter()
						error_dlg = gtk.MessageDialog(self.dialog,
							gtk.DIALOG_MODAL  | gtk.DIALOG_DESTROY_WITH_PARENT,
							gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
							"In directory: %s already exist at least one image. Should I use them to speed up generation?" %(folder_png))
						response=error_dlg.run()
						error_dlg.destroy()
						gtk.threads_leave()
						if response==gtk.RESPONSE_YES:
							self.delete_them=0
							create=False
						else:
							self.delete_them=1
					elif self.delete_them==0:
						create=False
				if create:
					number=str(i).zfill(lenN)
					dt=DummyThread("gnofract4d -q -s %simage_%s.png -i %d -j %d %sfile_%s.fct"%
							(folder_png,number,width,height,folder_fct,number))
					dt.start()
					radi=True
					while(radi):
						dt.join(1)
						radi=dt.isAlive()
						yield True
				if self.running==False:
					yield False
					break
				percent=float(i+1)/float(sumN+1)
				self.pbar.set_fraction(percent)
				self.pbar.set_text(str(i+1)+"/"+str(sumN+1))
				yield True
			#-------------------------------------------------------
			#-------------creating list file------------------------
			output=open(folder_png+"list","w")
			for i in range(self.dir_bean.get_base_stop()): #first output base keyframe 'stop' times
				output.write(folder_png+"image_"+str(0).zfill(lenN)+".png\n")
				
			current=1
			for i in range(self.dir_bean.keyframes_count()):
				for j in range(self.dir_bean.get_keyframe_duration(i)): #output all transition files
					output.write(folder_png+"image_"+str(current).zfill(lenN)+".png\n")
					current=current+1
				for j in range(self.dir_bean.get_keyframe_stop(i)-1): #then output keyframe 'stop' times
					output.write(folder_png+"image_"+str(current-1).zfill(lenN)+".png\n")
			output.close()
			#------------------------------------------------------
		except:
			self.running=False
			self.error=True
			gtk.threads_enter()
			error_dlg = gtk.MessageDialog(self.dialog,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"Unknown error during generation of .png files")
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
		#---------checking if there are gnofract in PATH------------
		found=False
		env=os.environ['PATH']
		for d in env.split(':'):
			if found:
				break
			if 'gnofract4d' in os.listdir(d):
				found=True
		if not found:
			error_dlg = gtk.MessageDialog(self.dialog,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
					"gnofract4d not found in PATH. Make sure you installed it. I will not continue")
			error_dlg.run()
			error_dlg.destroy()
			self.dialog.destroy()
			return -1
		#------------------------------------------------------------
		self.dialog.show_all()
		self.running=True
		self.error=False
		task=self.generate_png()
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

#thread to call gnofract4d
class DummyThread(Thread):
	def __init__(self,s):
		Thread.__init__(self)
		self.s=s
	
	def run(self):
		os.system(self.s)
		return
