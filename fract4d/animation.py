#!/usr/bin/python

# Copyright (C) 2006  Branko Kokanovic
#
#   DirectorBean.py: class which stores an animation
#

import os, sys, copy, math

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import fracttypes, fractal

# FIXME
sys.path.append("..")
from fract4dgui import preferences

#interpolation type constants
INT_LINEAR=    0
INT_LOG=    1
INT_INVLOG=    2
INT_COS=    3

class KeyFrame:
    def __init__(self,filename,duration,stop,int_type):
        self.filename = filename
        self.duration = duration
        self.stop = stop
        self.int_type = int_type
        
class T:
    def __init__(self, compiler):
        self.compiler = compiler
        self.reset()

    def reset(self):
        self.avi_file=""
        self.width=640
        self.height=480
        self.framerate=25
        self.redblue=True
        #keyframe is a list containing of a tuples
        #example: keyframe=[("/home/baki/a.fct",25),("/home/baki/b.fct",50)]
        self.keyframes=[]

    def get_fct_enabled(self):
        return preferences.userPrefs.getboolean("director","fct_enabled")
    
    def set_fct_enabled(self,fct_enabled):
        if fct_enabled:
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
        except Exception, err:
            #retrieve previous__dict__
            self.__dict__=odict
            raise

    def save_animation(self,file):
        fh=open(file,"w")
        fh.write('<?xml version="1.0"?>\n')
        fh.write("<animation>\n")
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

    #leftover from debugging purposes
    def pr(self):
        print self.__dict__

    def get_image_filename(self,n):
        "The filename of the image containing the Nth frame"
        return os.path.join(self.get_png_dir(),"image_%07d.png" %n)

    def get_fractal_filename(self,n):
        "The filename of the .fct file which generates the Nth frame"
        return os.path.join(self.get_fct_dir(),"file_%07d.fct" % n)

    def get_mu(self, int_type, x):
        if int_type==INT_LINEAR:
            mu=x
        elif int_type==INT_LOG:
            mu=math.log(x+1,2)
        elif int_type==INT_INVLOG:
            mu=(math.exp(x)-1)/(math.e-1)
        elif int_type==INT_COS:
            mu=(1-math.cos(x*math.pi))/2
        else:
            raise ValueError("Unknown interpolation type %d" % int_type)
        return mu
    
    # create a list containing all the filenames of the frames
    def create_list(self):
        framelist = []
        folder_png=self.get_png_dir()

        current=1
        for i in range(self.keyframes_count()):
            for j in range(self.get_keyframe_stop(i)): #output keyframe 'stop' times
                framelist.append(self.get_image_filename(current-1))

	    if i < self.keyframes_count()-1:
                # final frame has no transitions following it
                for j in range(self.get_keyframe_duration(i)): #output all transition files
                    framelist.append(self.get_image_filename(current))
                    current=current+1
	
	return framelist

    def get_keyframe_durations(self):
        durations = []
        for i in xrange(self.keyframes_count()):
            durations.append(self.get_keyframe_duration(i))

        return durations

    def get_total_frames(self):
        count = 0
        nframes = self.keyframes_count()
        for i in xrange(nframes):
            count += self.get_keyframe_stop(i)
            if i < nframes - 1:
                # don't count the last frame's duration
                count += self.get_keyframe_duration(i)
        return count
    
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
        if name=="output":
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

