#!/usr/bin/python

# Copyright (C) 2006  Branko Kokanovic
#
#   DirectorBean.py: bean for storing configuration
#

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os

from fract4dgui import preferences

#interpolation type constants
INT_LINEAR=	0
INT_LOG=	1
INT_INVLOG=	2
INT_COS=	3

class DirectorBean:
	def __init__(self):
		self.reset()

	def reset(self):
		self.base_keyframe=""
		self.base_stop=1
		self.avi_file=""
		self.width=640
		self.height=480
		self.framerate=25
		self.redblue=True
		#keyframe is a list containing of a tuples
		#example: keyframe=[("/home/baki/a.fct",25),("/home/baki/b.fct",50)]
		self.keyframes=[]

	def get_base_keyframe(self):
		return self.base_keyframe

	def set_base_keyframe(self,filename):
		if filename!=None:
			self.base_keyframe=filename
		else:
			self.base_keyframe=""

	def get_base_stop(self):
		return self.base_stop

	def set_base_stop(self,stop):
		if stop!=None:
			self.base_stop=int(stop)
		else:
			self.base_stop=1

	def get_fct_enabled(self):
		return preferences.userPrefs.getboolean("director","fct_enabled")

	def set_fct_enabled(self,fct_enabled):
		if fct_enabled==True:
			preferences.userPrefs.set("director","fct_enabled","1")
		else:
			preferences.userPrefs.set("director","fct_enabled","0")

	def get_fct_dir(self):
		return preferences.userPrefs.get("director","fct_dir")

	def set_fct_dir(self,dir):
		preferences.userPrefs.set("director","fct_dir",dir)

	def get_png_dir(self):
		return preferences.userPrefs.get("director","png_dir")

	def set_png_dir(self,dir):
		preferences.userPrefs.set("director","png_dir",dir)

	def get_avi_file(self):
		return self.avi_file

	def set_avi_file(self,file):
		if file!=None:
			self.avi_file=file
		else:
			self.avi_file=""

	def get_width(self):
		return self.width

	def set_width(self,width):
		if width!=None:
			self.width=int(width)
		else:
			self.width=640

	def get_height(self):
		return self.height

	def set_height(self,height):
		if height!=None:
			self.height=int(height)
		else:
			self.height=480

	def get_framerate(self):
		return self.framerate

	def set_framerate(self,fr):
		if fr!=None:
			self.framerate=int(fr)
		else:
			self.framerate=25

	def get_redblue(self):
		return self.redblue

	def set_redblue(self,rb):
		if rb!=None:
			if rb==1:
				self.redblue=True
			elif rb==0:
				self.redblue=False
				self.redblue=rb
		else:
			self.redblue=True

	def add_keyframe(self,filename,duration,stop,int_type,index=None):
		if index==None:
			self.keyframes.append((filename,duration,stop,int_type,(0,0,0,0,0,0)))
		else:
			self.keyframes[index:index]=[(filename,duration,stop,int_type,(0,0,0,0,0,0))]

	def remove_keyframe(self,index):
		self.keyframes[index:index+1]=[]

	def change_keyframe(self,index,duration,stop,int_type):
		if index<len(self.keyframes):
			self.keyframes[index:index+1]=[(self.keyframes[index][0],duration,stop,int_type,self.keyframes[index][4])]

	def get_keyframe(self,index):
		return self.keyframes[index]

	def get_keyframe_filename(self,index):
		return self.keyframes[index][0]

	def get_keyframe_duration(self,index):
		return self.keyframes[index][1]

	def set_keyframe_duration(self,index,duration):
		if index<len(self.keyframes):
			self.keyframes[index:index+1]=[(self.keyframes[index][0],duration,
				self.keyframes[index][2],self.keyframes[index][3],self.keyframes[index][4])]

	def get_keyframe_stop(self,index):
		return self.keyframes[index][2]

	def set_keyframe_stop(self,index,stop):
		if index<len(self.keyframes):
			self.keyframes[index:index+1]=[(self.keyframes[index][0],self.keyframes[index][1],
				stop,self.keyframes[index][3],self.keyframes[index][4])]

	def get_keyframe_int(self,index):
		return self.keyframes[index][3]

	def set_keyframe_int(self,index,int_type):
		if index<len(self.keyframes):
			self.keyframes[index:index+1]=[(self.keyframes[index][0],self.keyframes[index][1],
				self.keyframes[index][2],int_type,self.keyframes[index][4])]

	def get_directions(self,index):
		return self.keyframes[index][4]

	def set_directions(self,index,drct):
		if index<len(self.keyframes):
			self.keyframes[index:index+1]=[(self.keyframes[index][0],self.keyframes[index][1],
				self.keyframes[index][2],self.keyframes[index][3],drct)]

	def keyframes_count(self):
		return len(self.keyframes)

	def __getstate__(self):
		odict = self.__dict__.copy() # copy the dict since we change it
		#del odict['fh']              # remove filehandle entry
		return odict

	def __setstate__(self,dict):
		self.keyframes=[]
		self.__dict__.update(dict)   # update attributes

	#returns -1 if there was error loading XML file, 0 otherwise
	def load_animation(self,file):
		#save __dict__ if there was error
		odict = self.__dict__.copy()
		import traceback
		try:
			self.keyframes=[]
			parser = make_parser()
			ah = AnimationHandler(self)
			parser.setContentHandler(ah)
			parser.parse(open(file))
			return 0
		except:
			#retrieve previous__dict__
			self.__dict__=odict.copy()
			return -1

	#save current animation configuration in XML file
	#returns -1 if there was error saving XML file, 0 otherwise
	def save_animation(self,file):
		try:
			fh=open(file,"w")
			fh.write('<?xml version="1.0"?>\n')
			fh.write("<animation>\n")
			fh.write('\t<base filename="%s" stopped="%d"/>\n'%(self.base_keyframe,self.base_stop))
			fh.write('\t<keyframes>\n')
			for kf in self.keyframes:
				fh.write('\t\t<keyframe filename="%s">\n'%kf[0])
				fh.write('\t\t\t<duration value="%d"/>\n'%kf[1])
				fh.write('\t\t\t<stopped value="%d"/>\n'%kf[2])
				fh.write('\t\t\t<interpolation value="%d"/>\n'%kf[3])
				fh.write('\t\t\t<directions xy="%d" xz="%d" xw="%d" yz="%d" yw="%d" zw="%d"/>\n'%kf[4])
				fh.write('\t\t</keyframe>\n')
			fh.write('\t</keyframes>\n')
			fh.write('\t<output filename="%s" framerate="%d" width="%d" height="%d" swap="%d"/>\n'%
					(self.avi_file,self.framerate,self.width,self.height,self.redblue))
			fh.write("</animation>\n")
			fh.close()
			return 0
		except:
			return -1

	#leftover from debugging purposes
	def pr(self):
		print self.__dict__

class AnimationHandler(ContentHandler):

	def __init__(self,dir_bean):
		self.dir_bean=dir_bean
		self.curr_index=0
		self.curr_filename=""
		self.curr_duration=25
		self.curr_stopped=1
		self.curr_int_type=0
		self.curr_directions=()

	def startElement(self, name, attrs):
		if name=="base":
			self.dir_bean.set_base_keyframe(attrs.get("filename"))
			self.dir_bean.set_base_stop(attrs.get("stopped"))
		elif name=="output":
			self.dir_bean.set_avi_file(attrs.get("filename"))
			self.dir_bean.set_framerate(attrs.get("framerate"))
			self.dir_bean.set_width(attrs.get("width"))
			self.dir_bean.set_height(attrs.get("height"))
			self.dir_bean.set_redblue(int(attrs.get("swap")))
		elif name=="keyframe":
			if attrs.get("filename")!=None:
				self.curr_filename=attrs.get("filename")
		elif name=="duration":
			if attrs.get("value")!=None:
				self.curr_duration=int(attrs.get("value"))
		elif name=="stopped":
			if attrs.get("value")!=None:
				self.curr_stopped=int(attrs.get("value"))
		elif name=="interpolation":
			if attrs.get("value")!=None:
				self.curr_int_type=int(attrs.get("value"))
		elif name=="directions":
			if attrs.get("xy")!=None:
				xy=int(attrs.get("xy"))
			else:
				xy=0
			if attrs.get("xz")!=None:
				xz=int(attrs.get("xz"))
			else:
				xz=0
			if attrs.get("xw")!=None:
				xw=int(attrs.get("xw"))
			else:
				xw=0
			if attrs.get("yz")!=None:
				yz=int(attrs.get("yz"))
			else:
				yz=0
			if attrs.get("yw")!=None:
				yw=int(attrs.get("yw"))
			else:
				yw=0
			if attrs.get("zw")!=None:
				zw=int(attrs.get("zw"))
			else:
				zw=0
			self.curr_directions=(xy,xz,xw,yz,yw,zw)
		return

	def endElement(self, name):
		if name=="keyframe":
			self.dir_bean.add_keyframe(self.curr_filename,self.curr_duration,self.curr_stopped,self.curr_int_type)
			self.dir_bean.set_directions(self.curr_index,self.curr_directions)
			self.curr_index=self.curr_index+1
			#reset
			self.curr_filename=""
			self.curr_duration=25
			self.curr_stopped=1
			self.curr_int_type=0
			self.curr_directions=()
		return
