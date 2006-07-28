#!/usr/bin/python

# Copyright (C) 2006  Branko Kokanovic
#
#   DirectorBean.py: bean for storing configuration
#

#interpolation type constants
INT_LINEAR=	0
INT_LOG=	1
INT_INVLOG=	2
INT_COS=	3

class DirectorBean:
	def __init__(self):
		self.base_keyframe=""
		self.base_stop=1
		self.fct_enabled=False
		self.fct_dir="/tmp"
		self.png_dir="/tmp"
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
		self.base_keyframe=filename

	def get_base_stop(self):
		return self.base_stop

	def set_base_stop(self,stop):
		self.base_stop=stop

	def get_fct_enabled(self):
		return self.fct_enabled

	def set_fct_enabled(self,fct_enabled):
		self.fct_enabled=fct_enabled

	def get_fct_dir(self):
		return self.fct_dir

	def set_fct_dir(self,dir):
		self.fct_dir=dir

	def get_png_dir(self):
		return self.png_dir

	def set_png_dir(self,dir):
		self.png_dir=dir

	def get_avi_file(self):
		return self.avi_file

	def set_avi_file(self,file):
		self.avi_file=file

	def get_width(self):
		return self.width

	def set_width(self,width):
		self.width=width

	def get_height(self):
		return self.height

	def set_height(self,height):
		self.height=height

	def get_framerate(self):
		return self.framerate

	def set_framerate(self,fr):
		self.framerate=fr

	def get_redblue(self):
		return self.redblue

	def set_redblue(self,rb):
		self.redblue=rb


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

	#leftover from debugging purposes
	def pr(self):
		print self.__dict__
