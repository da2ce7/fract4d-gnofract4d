#!/usr/bin/env python

# create a color map based on an image. Algorithm copied from ImageMagick's
# quantize option

from PIL import ImageFile

class Node:
    def __init__(self,r,g,b):
        self.n_tree_pixels = 0 # pixels in this node and below
        self.n_local_pixels = 1 # pixels in this node alone
        self.sum_r = 0 # sum of R values for local pixels
        self.sum_g = 0 # sum of G values for local pixels
        self.sum_b = 0 # sum of B values for local pixels
        self.error = 0 # quantization error
        self.rgb = (r,g,b)
        self.children = [None for x in range(8)] # no children yet

    def increment_children(self):
        self.n_tree_pixels += 1

    def increment(self):
        self.n_local_pixels += 1

    def is_leaf_node(self):
        return self.rgb != None

    def make_interior_node(self):
        self.rgb = None
        self.n_local_pixels=0
    
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
        self.root = None
        
    def getdata(self):
        return self.im.getdata()
    
    def build_octree(self):
        for (r,g,b) in self.getdata():
            self.insert_pixel(r,g,b)
        
    def dump_octree(self,node,prefix=""):
        if node == None:
            return ""
        val = "%s[(%s,%s,%s)\n" % \
              (prefix, node.rgb,node.n_local_pixels, node.n_tree_pixels)
        child_prefix = "  " + prefix
        for i in xrange(8):
            child = node.children[i]
            if child != None:
                val += "%d:" % i + self.dump_octree(child,child_prefix)
            
        val += "%s]\n" % prefix
        return val
    
    def adjust_dimension(self, min, length, val, dim):
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
        if not pos:
            self.root = Node(r,g,b)
            self.root.increment_children()
            return
        
        x = 0
        while length > 1:
            pos.increment_children()
            length //= 2
            if pos.rgb == (r,g,b):
                # found a node representing this color
                pos.increment()
                break

            # need to find a child
            child = self.which_child(min,length,r,g,b)
            if pos.children[child] == None:
                # no child exists
                if pos.is_leaf_node():                    
                    # if this is a leaf, make it internal and push its
                    # contents down to be another new child
                    (this_r,this_g,this_b) = pos.rgb
                    other_child = self.which_child(
                        min,length,this_r,this_g,this_b)
                    if other_child == child:
                        
                    new_child = Node(this_r,this_g,this_b)
                    new_child.n_local_pixels = pos.n_local_pixels
                    new_child.n_tree_pixels = pos.n_local_pixels+1
                    pos.children[other_child] = new_child 
                    #print "new child", new_child.rgb
                    
                    pos.make_interior_node()
                
                #add new child...
                pos.children[child] = Node(r,g,b)
                break
            else:
                pos = pos.children[child]
        
                
        
