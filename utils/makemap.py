#!/usr/bin/env python

# create a color map based on an image. Algorithm copied from ImageMagick's
# quantize option

from PIL import ImageFile

class Node:
    def __init__(self):
        self.n_tree_pixels = 0 # pixels in this node and below
        self.n_local_pixels = 0 # pixels in this node alone
        self.sum_r = 0 # sum of R values for local pixels
        self.sum_g = 0 # sum of G values for local pixels
        self.sum_b = 0 # sum of B values for local pixels
        self.error = 0 # quantization error
        self.children = [None for x in range(8)] # no children yet
        
class T:
    R = 0
    G = 1
    B = 2
    def __init__(self,file):
        'Load an image from open stream "file"'
        p = ImageFile.Parser()
        
        while 1:
            s = file.read(1024)
            if not s:
                break
            p.feed(s)

        self.im = p.close()

    def getdata(self):
        return self.im.getdata()
    
    def build_octree(self):
        self.root = Node()

    def mid(self,min,max):
        return (min + max) // 2

    def adjust_dimension(self, min, max, val, dim):
        mid = self.mid(min[dim],max[dim])
        if val > mid:
            min[dim] = mid
            return True
        else:
            max[dim] = mid+1
            return False
        
    def which_child(self,min,max, r, g, b):
        'index into child array where this pixel should go'
        child = 0
        if self.adjust_dimension(min,max, r, T.R):
            child += 4
        if self.adjust_dimension(min,max, g, T.G):
            child += 2
        if self.adjust_dimension(min,max, b, T.B):
            child += 1
        return child
    
    def insert_pixel(self,r,g,b):
        min = [0,0,0]
        max = [256,256,256]

        pos = this.root
        while 1:
            child = which_child(min_max,r,g,b)
            if pos.children[child] == None:
                pos.children[child] = Node()
                
                
                
