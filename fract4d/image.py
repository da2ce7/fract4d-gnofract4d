# A type representing an image - this wraps the underlying C++ image type
# exposed via fract4dmodule and provides some higher-level options around it

import fract4dc

class T:
    FATE_SIZE = 4
    COL_SIZE = 3
    OUT=0
    IN=1 | 128 # in pixels have solid bit set
    UNKNOWN=255
    BLACK=[0,0,0]
    WHITE=[255,255,255]
    def __init__(self,xsize,ysize,img):
        self.xsize = xsize
        self.ysize = ysize
        self.fate_buf = fract4dc.image_fate_buffer(img,0,0)
        self.image_buf = fract4dc.image_buffer(img,0,0)
        self.img = img

    def pos(self,x,y,size):
        return size * (y * self.xsize + x)
    
    def get_fate(self,x,y):
        return ord(self.fate_buf[self.pos(x,y,T.FATE_SIZE)])

    def get_all_fates(self,x,y):
        pos = self.pos(x,y,T.FATE_SIZE)
        return map(ord,list(self.fate_buf[pos:pos+T.FATE_SIZE]))

    def get_color(self,x,y):
        pos = self.pos(x,y,T.COL_SIZE)
        return map(ord,list(self.image_buf[pos:pos+T.COL_SIZE]))

    def get_color_index(self,x,y,sub=0):
        return fract4dc.image_get_color_index(self.img,x,y,sub)
    
    
