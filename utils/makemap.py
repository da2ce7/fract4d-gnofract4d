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

    def increment_children(self):
        self.n_tree_pixels += 1

    def increment(self):
        self.n_local_pixels += 1
    
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
        for (r,g,b) in self.getdata():
            self.insert_pixel(r,g,b)
        
    def dump_octree(self,node,prefix=""):
        if node == None:
            return "None\n"
        val = "%s[(%s,%s)\n" % \
              (prefix, node.n_local_pixels, node.n_tree_pixels)
        child_prefix = "  " + prefix
        for child in node.children:
            val += self.dump_octree(child,child_prefix)
        val += "%s]\n" % prefix
        return val
    
    def adjust_dimension(self, min, length, val, dim):
        length //= 2
        mid = min[dim] + length
        if val < mid:
            # lower half
            return False
        else:
            # upper half
            min[dim] += length
            return True
        
    def which_child(self,min,length, r, g, b):
        'index into child array where this pixel should go'
        child = 0
        if self.adjust_dimension(min, length, r, T.R):
            child += 4
        if self.adjust_dimension(min, length, g, T.G):
            child += 2
        if self.adjust_dimension(min, length, b, T.B):
            child += 1
        return child

    def insert_pixel(self,r,g,b):
        '''update the octree to include this pixel,
        inserting nodes as required.'''
        min = [0,0,0]
        length = 256

        pos = self.root
        x = 0
        while length > 1:
            pos.increment_children()
            child = self.which_child(min,length,r,g,b)
            if pos.children[child] == None:
                pos.children[child] = Node()

            pos = pos.children[child]
            length //= 2
            
        pos.increment()
                
        
