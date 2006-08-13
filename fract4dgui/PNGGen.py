#UI and logic for generation PNG images
#It gets all information from director bean class, gets all values, and,
#in special thread, while it finds in-between values it call gtkfractal.HighResolution
#to create images

import gtk
import gobject
import re
import math
import sys
import os
from threading import *

import gtkfractal, hig
from fract4d import fractal,fracttypes, animation

running=False
thread_error=False

class PNGGeneration(gtk.Dialog,hig.MessagePopper):
    def __init__(self,animation,compiler):
        gtk.Dialog.__init__(self,
            "Generating images...",None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))

        hig.MessagePopper.__init__(self)
        self.lbl_image=gtk.Label("Current image progress")
        self.vbox.pack_start(self.lbl_image,True,True,0)
        self.pbar_image = gtk.ProgressBar()
        self.vbox.pack_start(self.pbar_image,True,True,0)
        self.lbl_overall=gtk.Label("Overall progress")
        self.vbox.pack_start(self.lbl_overall,True,True,0)
        self.pbar_overall = gtk.ProgressBar()
        self.vbox.pack_start(self.pbar_overall,True,True,0)
        self.set_geometry_hints(None,min_aspect=3.5,max_aspect=3.5)
        self.anim=animation

        #-------------loads compiler----------------------------
        self.compiler=compiler

    def generate_png(self):
        global running
        values=[]
        durations=[]

        #--------find values and duration from all keyframes------------
        try:
	   (values, durations) = self.anim.get_keyframe_values()
        except Exception, err:
            self.show_error(_("Error processing keyframes"), str(err))
            yield False
            return

        #---------------------------------------------------------------
        create_all_images=self.to_create_images_again()
        gt=GenerationThread(
            durations,values,self.anim,
            self.compiler,
            create_all_images,self.pbar_image,self.pbar_overall)
        gt.start()
        working=True
        while(working):
            gt.join(1)
            working=gt.isAlive()
            yield True

        if thread_error==True:
            self.show_error("Error during image generation", "Unknown")
            yield False
            return


        if running==False:
            yield False
            return
        running=False
        self.destroy()
        yield False
    
    def to_create_images_again(self):
        create = True
        filelist = self.anim.create_list()
	for f in filelist:		
            if os.path.exists(f):
                gtk.threads_enter()
                try:
		    folder_png = self.anim.get_png_dir()
                    response = self.ask_question(
                        _("The temporary directory: %s already contains at least one image" % folder_png),
                        _("Use them to speed up generation?"))

                except Exception, err:
                    print err
		    gtk.threads_leave()
                    raise

		gtk.threads_leave()
		    
                if response==gtk.RESPONSE_ACCEPT:
                    create=False
                else:
                    create=True
                return create

        return create

    def show_error(self,message,secondary):
        running=False
        self.error=True
        gtk.threads_enter()
        error_dlg = hig.ErrorAlert(
            parent=self,
            primary=message,
            secondary=secondary)
        error_dlg.run()
        error_dlg.destroy()
        gtk.threads_leave()
        event = gtk.gdk.Event(gtk.gdk.DELETE)
        self.emit('delete_event', event)

    def show(self):
        global running
        self.show_all()
        running=True
        self.error=False
        task=self.generate_png()
        gobject.idle_add(task.next)
        response = self.run()
        if response != gtk.RESPONSE_CANCEL:
            if running==True: #destroy by user
                running=False
                self.destroy()
                return 1
            else:
                if self.error==True: #error
                    self.destroy()
                    return -1
                else: #everything ok
                    self.destroy()
                    return 0
        else: #cancel pressed
            running=False
            self.destroy()
            return 1

#thread to interpolate values and calls generation of .png files
class GenerationThread(Thread):
    def __init__(
        self,durations,values,animation,compiler,
        create_all_images,pbar_image,pbar_overall):
        Thread.__init__(self)
        self.durations=durations
        self.values=values
        self.anim=animation
        self.create_all_images=create_all_images
        self.pbar_image=pbar_image
        self.pbar_overall=pbar_overall
        #initializing progress bars
        self.pbar_image.set_fraction(0)
        self.pbar_overall.set_fraction(0)
        self.pbar_overall.set_text("0/"+str(sum(self.durations)+1))
        self.compiler=compiler

        #semaphore to signalize that image generation is finished
        self.next_image=Semaphore(1)

    def onProgressChanged(self,f,progress):
        global running
        if running:
            self.pbar_image.set_fraction(progress/100.0)

    #one image generation complete - tell (with "semaphore" self.next_image) we can continue
    def onStatusChanged(self,f,status_val):
        if status_val == 0:
            #release semaphore
            self.next_image.release()

    def run(self):
        global thread_error,running
        import traceback
        try:
            #first generates image from base keyframe
            self.generate_base_keyframe()
            #pass through all keyframes and generates inter images
            for i in range(self.anim.keyframes_count()-1):
                self.generate_images(i)
                if running==False:
                    return
            #wait for last image to finish rendering
            self.next_image.acquire()
            #generate list file
            list = self.anim.create_list()
	    lfilename = os.path.join(self.anim.get_png_dir(), "list")
	    lfile = open(lfilename,"w")
	    print >>lfile, "\n".join(list)
	    lfile.close()
	    
        except:
            traceback.print_exc()
            thread_error=True
            running=False
            return


    def generate_base_keyframe(self):
        #sum of all frames, needed for padding output files
        sumN=sum(self.durations)
        lenN=len(str(sumN))
        f=fractal.T(self.compiler)
        f.loadFctFile(open(self.anim.get_keyframe_filename(0)))
        #--------------gets directories--------------------------
        folder_png=self.anim.get_png_dir()
        if folder_png[-1]!="/":
            folder_png=folder_png+"/"
        if self.anim.get_fct_enabled():
            folder_fct=self.anim.get_fct_dir()
            if folder_fct[-1]!="/":
                folder_fct=folder_fct+"/"
        #--------------------------------------------------------
        self.next_image.acquire()
        #writes .fct file if user wanted that
        if self.anim.get_fct_enabled():
            f.save(open(folder_fct+"file_"+str(0).zfill(lenN)+".fct","w"))
        #check if image already exist and user wants to leave it or not
        if not(os.path.exists(folder_png+"image_"+str(0).zfill(lenN)+".png") and self.create_all_images==False): #check if image already exist
            self.current = gtkfractal.HighResolution(f.compiler,
                int(self.anim.get_width()),int(self.anim.get_height()))
            self.current.set_fractal(f)
            self.current.connect('status-changed', self.onStatusChanged)
            self.current.connect('progress-changed', self.onProgressChanged)
            self.current.draw_image(folder_png+"image_"+str(0).zfill(lenN)+".png")
        else:
            #just release semaphore
            self.next_image.release()
        return

    #main method for generating images
    #it generates images between iteration-th-1 and iteration-th keyframe
    #first, it gets border values (keyframe values)
    #(values - x,y,z,w,size,angles,formula parameters)
    #then, in a loop, it generates inter values, fill fractal class with it and
    #calls gtkfractal.HighResolution to generate images
    def generate_images(self,iteration):
        print iteration, len(self.durations)
        global running
        #sum of all frames, needed for padding output files
        sumN=sum(self.durations)
        lenN=len(str(sumN))
        #number of images already generated
        sumBefore=sum(self.durations[0:iteration])
        #current duration
        N=self.durations[iteration]
        #creates fractal with base from base keyframe
        f=fractal.T(self.compiler)
        f.loadFctFile(open(self.anim.get_keyframe_filename(0)))
        #--------------gets directories--------------------------
        folder_png=self.anim.get_png_dir()
        if folder_png[-1]!="/":
            folder_png=folder_png+"/"
        if self.anim.get_fct_enabled():
            folder_fct=self.anim.get_fct_dir()
            if folder_fct[-1]!="/":
                folder_fct=folder_fct+"/"
        #--------------------------------------------------------
        #----------------get all values--------------------------
        #x,y,z,w,size
        x1=float(self.values[iteration][f.XCENTER])
        x2=float(self.values[iteration+1][f.XCENTER])
        y1=float(self.values[iteration][f.YCENTER])
        y2=float(self.values[iteration+1][f.YCENTER])
        z1=float(self.values[iteration][f.ZCENTER])
        z2=float(self.values[iteration+1][f.ZCENTER])
        w1=float(self.values[iteration][f.WCENTER])
        w2=float(self.values[iteration+1][f.WCENTER])
        size1=float(self.values[iteration][f.MAGNITUDE])
        size2=float(self.values[iteration+1][f.MAGNITUDE])
        #angles
        xy1=float(self.values[iteration][f.XYANGLE])
        xy2=float(self.values[iteration+1][f.XYANGLE])
        xz1=float(self.values[iteration][f.XZANGLE])
        xz2=float(self.values[iteration+1][f.XZANGLE])
        xw1=float(self.values[iteration][f.XWANGLE])
        xw2=float(self.values[iteration+1][f.XWANGLE])
        yz1=float(self.values[iteration][f.YZANGLE])
        yz2=float(self.values[iteration+1][f.YZANGLE])
        yw1=float(self.values[iteration][f.YWANGLE])
        yw2=float(self.values[iteration+1][f.YWANGLE])
        zw1=float(self.values[iteration][f.ZWANGLE])
        zw2=float(self.values[iteration+1][f.ZWANGLE])
        #parameters
        param1={}
        param2={}
        for param in self.values[iteration][f.ZWANGLE+1]:
            if param in self.values[iteration][f.ZWANGLE+1]:
                param1[param]=self.values[iteration][f.ZWANGLE+1][param]
                param2[param]=self.values[iteration+1][f.ZWANGLE+1][param]
        #-----------------------------------------------------------
        #------------find direction for angles----------------------
        to_right=[False]*6
        #----------xy--------------
        dir_xy=self.anim.get_directions(iteration)[0]
        if dir_xy==0:
            if abs(xy2-xy1)<math.pi and xy1<xy2:
                to_right[0]=True
            if abs(xy2-xy1)>math.pi and xy1>xy2:
                to_right[0]=True
        elif dir_xy==1:
            if abs(xy2-xy1)<math.pi and xy1>xy2:
                to_right[0]=True
            if abs(xy2-xy1)>math.pi and xy1<xy2:
                to_right[0]=True
        elif dir_xy==2:
            to_right[0]=True
        if to_right[0]==True and xy2<xy1:
                xy2=xy2+2*math.pi
        if to_right[0]==False and xy2>xy1:
                xy1=xy1+2*math.pi
        #--------------------------
        #----------xz--------------
        dir_xz=self.anim.get_directions(iteration)[1]
        if dir_xz==0:
            if abs(xz2-xz1)<math.pi and xz1<xz2:
                to_right[1]=True
            if abs(xz2-xz1)>math.pi and xz1>xz2:
                to_right[1]=True
        elif dir_xz==1:
            if abs(xz2-xz1)<math.pi and xz1>xz2:
                to_right[1]=True
            if abs(xz2-xz1)>math.pi and xz1<xz2:
                to_right[1]=True
        elif dir_xz==2:
            to_right[1]=True
        if to_right[1]==True and xz2<xz1:
                xz2=xz2+2*math.pi
        if to_right[1]==False and xz2>xz1:
                xz1=xz1+2*math.pi
        #--------------------------
        #----------xw--------------
        dir_xw=self.anim.get_directions(iteration)[2]
        if dir_xw==0:
            if abs(xw2-xw1)<math.pi and xw1<xw2:
                to_right[2]=True
            if abs(xw2-xw1)>math.pi and xw1>xw2:
                to_right[2]=True
        elif dir_xw==1:
            if abs(xw2-xw1)<math.pi and xw1>xw2:
                to_right[2]=True
            if abs(xw2-xw1)>math.pi and xw1<xw2:
                to_right[2]=True
        elif dir_xw==2:
            to_right[2]=True
        if to_right[2]==True and xw2<xw1:
                xw2=xw2+2*math.pi
        if to_right[2]==False and xw2>xw1:
                xw1=xw1+2*math.pi
        #--------------------------
        #----------yz--------------
        dir_yz=self.anim.get_directions(iteration)[3]
        if dir_yz==0:
            if abs(yz2-yz1)<math.pi and yz1<yz2:
                to_right[3]=True
            if abs(yz2-yz1)>math.pi and yz1>yz2:
                to_right[3]=True
        elif dir_yz==1:
            if abs(yz2-yz1)<math.pi and yz1>yz2:
                to_right[3]=True
            if abs(yz2-yz1)>math.pi and yz1<yz2:
                to_right[3]=True
        elif dir_yz==2:
            to_right[3]=True
        if to_right[3]==True and yz2<yz1:
                yz2=yz2+2*math.pi
        if to_right[3]==False and yz2>yz1:
                yz1=yz1+2*math.pi
        #--------------------------
        #----------yw--------------
        dir_yw=self.anim.get_directions(iteration)[4]
        if dir_yw==0:
            if abs(yw2-yw1)<math.pi and yw1<yw2:
                to_right[4]=True
            if abs(yw2-yw1)>math.pi and yw1>yw2:
                to_right[4]=True
        elif dir_yw==1:
            if abs(yw2-yw1)<math.pi and yw1>yw2:
                to_right[4]=True
            if abs(yw2-yw1)>math.pi and yw1<yw2:
                to_right[4]=True
        elif dir_yw==2:
            to_right[4]=True
        if to_right[4]==True and yw2<yw1:
                yw2=yw2+2*math.pi
        if to_right[4]==False and yw2>yw1:
                yw1=yw1+2*math.pi
        #--------------------------
        #----------zw--------------
        dir_zw=self.anim.get_directions(iteration)[5]
        if dir_zw==0:
            if abs(zw2-zw1)<math.pi and zw1<zw2:
                to_right[5]=True
            if abs(zw2-zw1)>math.pi and zw1>zw2:
                to_right[5]=True
        elif dir_zw==1:
            if abs(zw2-zw1)<math.pi and zw1>zw2:
                to_right[5]=True
            if abs(zw2-zw1)>math.pi and zw1<zw2:
                to_right[5]=True
        elif dir_zw==2:
            to_right[5]=True
        if to_right[5]==True and zw2<zw1:
                zw2=zw2+2*math.pi
        if to_right[5]==False and zw2>zw1:
                zw1=zw1+2*math.pi
        #--------------------------
        #------------------------------------------------------------
        #loop to generate images between current (iteration-th) and previous keyframe
        for i in range(1,N+1):
            #--------------calculating mu----------------------------
            #depending on interpolation type, mu constant get different values from 0 to 1
            int_type=self.anim.get_keyframe_int(iteration)
            mu=float(i)/float(N)
            if int_type==animation.INT_LINEAR:
                mu=mu
            elif int_type==animation.INT_LOG:
                mu=math.log(mu+1,2)
            elif int_type==animation.INT_INVLOG:
                mu=(math.exp(mu)-1)/(math.e-1)
            else:
                mu=(1-math.cos(mu*math.pi))/2
            #--------------------------------------------------------
            #--------------calculating new values-------------------
            #x,y,z,w,size
            new_x=x1*(1-mu)+x2*mu
            new_y=y1*(1-mu)+y2*mu
            new_z=z1*(1-mu)+z2*mu
            new_w=w1*(1-mu)+w2*mu
            new_size=size1*(1-mu)+size2*mu
            #angles
            new_xy=xy1*(1-mu)+xy2*mu
            while new_xy>math.pi:
                new_xy=new_xy-2*math.pi
            new_xz=xz1*(1-mu)+xz2*mu
            while new_xz>math.pi:
                new_xz=new_xz-2*math.pi
            new_xw=xw1*(1-mu)+xw2*mu
            while new_xw>math.pi:
                new_xw=new_xw-2*math.pi
            new_yz=yz1*(1-mu)+yz2*mu
            while new_yz>math.pi:
                new_yz=new_yz-2*math.pi
            new_yw=yw1*(1-mu)+yw2*mu
            while new_yw>math.pi:
                new_yw=new_yw-2*math.pi
            new_zw=zw1*(1-mu)+zw2*mu
            while new_zw>math.pi:
                new_zw=new_zw-2*math.pi
            #parameters
            new_param={}
            for param in param1:
                if len(param1[param])==2:
                    new_param[param]=(param1[param][0]*(1-mu)+param2[param][0]*mu,param1[param][1]*(1-mu)+param2[param][1]*mu)
                elif len(param1[param])==1:
                    new_param[param]=(param1[param][0]*(1-mu)+param2[param][0]*mu,)
            #---------------------------------------------------------
            #--------------putting new values in fractal---------------
            #but, first, wait for previous image to finish rendering
            self.next_image.acquire()
            #check if user canceled us
            if running==False:
                return
            #update progress bar
            percent=float((sumBefore+i))/(sumN+1)
            self.pbar_overall.set_fraction(percent)
            self.pbar_overall.set_text(str(sumBefore+i)+"/"+str(sumN+1))
            #x,y,z,w,size
            f.set_param(f.XCENTER,new_x)
            f.set_param(f.YCENTER,new_y)
            f.set_param(f.ZCENTER,new_z)
            f.set_param(f.WCENTER,new_w)
            f.set_param(f.MAGNITUDE,new_size)
            #angles
            f.set_param(f.XYANGLE,new_xy)
            f.set_param(f.XZANGLE,new_xz)
            f.set_param(f.XWANGLE,new_xw)
            f.set_param(f.YZANGLE,new_yz)
            f.set_param(f.YWANGLE,new_yw)
            f.set_param(f.ZWANGLE,new_zw)
            #parameters
            for form in f.forms:
                if form.sectname=='function':
                    break
            for param in new_param:
                if len(new_param[param])==2:
                    re=new_param[param][0]
                    im=new_param[param][1]
                    form.set_named_param(param,"(%f,%f)"%(re,im))
                elif len(new_param[param])==1:
                    n=new_param[param][0]
                    form.set_named_param(param,"%f"%n)
            #----------------------------------------------------------
            #writes .fct file if user wanted that
            if self.anim.get_fct_enabled():
                f.save(open(folder_fct+"file_"+str(sumBefore+i).zfill(lenN)+".fct","w"))

            #check if image already exist and user wants to leave it or not
            if not(os.path.exists(folder_png+"image_"+str(sumBefore+i).zfill(lenN)+".png") and self.create_all_images==False): #check if image already exist
                self.current = gtkfractal.HighResolution(f.compiler,
                    int(self.anim.get_width()),int(self.anim.get_height()))
                self.current.set_fractal(f)
                self.current.connect('status-changed', self.onStatusChanged)
                self.current.connect('progress-changed', self.onProgressChanged)
                self.current.draw_image(folder_png+"image_"+str(sumBefore+i).zfill(lenN)+".png")
            else:
                #just release semaphore
                self.next_image.release()
        return
