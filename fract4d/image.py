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
    def __init__(self,xsize,ysize):
        self.xsize = xsize
        self.ysize = ysize
        self._img = fract4dc.image_create(xsize,ysize)
        self.update_bufs()

    def update_bufs(self):
        self.fate_buf = fract4dc.image_fate_buffer(self._img,0,0)
        self.image_buf = fract4dc.image_buffer(self._img,0,0)

    def resize(self,x,y):
        fract4dc.image_resize(self._img, x, y)
        self.xsize = x
        self.ysize = y
        self.update_bufs()
        
    def clear(self):
        fract4dc.image_clear(self._img)
        
    def pos(self,x,y,size):
        return size * (y * self.xsize + x)

    def fate_buffer(self,x=0,y=0):
        return fract4dc.image_fate_buffer(self._img, x, y)

    def image_buffer(self,x=0,y=0):
        return fract4dc.image_buffer(self._img, x, y)
        
    def get_fate(self,x,y):
        return ord(self.fate_buf[self.pos(x,y,T.FATE_SIZE)])

    def get_all_fates(self,x,y):
        pos = self.pos(x,y,T.FATE_SIZE)
        return map(ord,list(self.fate_buf[pos:pos+T.FATE_SIZE]))

    def get_color(self,x,y):
        pos = self.pos(x,y,T.COL_SIZE)
        return map(ord,list(self.image_buf[pos:pos+T.COL_SIZE]))

    def get_color_index(self,x,y,sub=0):
        return fract4dc.image_get_color_index(self._img,x,y,sub)
    
    
