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
    def __init__(self,xsize,ysize,txsize=-1,tysize=-1):
        self._img = fract4dc.image_create(xsize,ysize,txsize, tysize)
        self.update_bufs()

    def get_xsize(self):
        return self.get_dim(fract4dc.IMAGE_WIDTH)

    def get_ysize(self):
        return self.get_dim(fract4dc.IMAGE_HEIGHT)

    def get_total_xsize(self):
        return self.get_dim(fract4dc.IMAGE_TOTAL_WIDTH)

    def get_total_ysize(self):
        return self.get_dim(fract4dc.IMAGE_TOTAL_HEIGHT)

    def get_xoffset(self):
        return self.get_dim(fract4dc.IMAGE_XOFFSET)

    def get_yoffset(self):
        return self.get_dim(fract4dc.IMAGE_YOFFSET)
    
    def get_dim(self,dim):
        return fract4dc.image_dims(self._img)[dim]

    xsize = property(get_xsize)
    ysize = property(get_ysize)
    total_xsize = property(get_total_xsize)
    total_ysize = property(get_total_ysize)
    xoffset = property(get_xoffset)
    yoffset = property(get_yoffset)

    def save(self,name):
        file = open(name,"wb")
        fract4dc.image_save(self._img, file)
        file.close()
        
    def get_tile_list(self):
        x = 0
        y = 0
        base_xres = self.xsize
        base_yres = self.ysize
        tiles = []
        while y < self.total_ysize:
            while x < self.total_xsize:
                w = min(base_xres, self.total_xsize - x)
                h = min(base_yres, self.total_ysize - y)
                tiles.append((x,y,w,h))
                x += base_xres
            y += base_yres
            x = 0
        return tiles
    
    def set_offset(self,x,y):
        fract4dc.image_set_offset(self._img,x,y)
        
    def update_bufs(self):
        self.fate_buf = fract4dc.image_fate_buffer(self._img,0,0)
        self.image_buf = fract4dc.image_buffer(self._img,0,0)

    def resize(self,x,y,txsize=-1,tysize=-1):
        fract4dc.image_resize(self._img, x, y)
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
    
    
