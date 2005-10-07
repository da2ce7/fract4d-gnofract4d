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

    def increment(self,x=1):
        self.n_local_pixels += x

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
        self.update_counts(self.root)
        
    def dump_octree(self,node,prefix=""):
        if node == None:
            return ""
        val = "%s[(%s,%s,%s)\n" % \
              (prefix, node.rgb,node.n_local_pixels, node.n_tree_pixels)
        child_prefix = "  " + prefix
        for i in xrange(8):
            child = node.children[i]
            if child != None:
                val += child_prefix + "%d:" % i + self.dump_octree(child,child_prefix)
            
        val += "%s]\n" % prefix
        return val

    def update_counts(self,node):
        if not node:
            return 0
        
        if node.is_leaf_node():
            return node.n_local_pixels

        sum = 0
        for child in node.children:
            sum += self.update_counts(child)

        node.n_tree_pixels = sum
        return sum
    
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

    def insert_pixel(self,r,g,b,weight=1):
        '''update the octree to include this pixel,
        inserting nodes as required.'''
        min = [0,0,0]
        length = 256

        pos = self.root
        if not pos:
            self.root = Node(r,g,b)
            #self.root.increment_children()
            return
        
        while length > 0:
            #pos.increment_children()
            length //= 2
            if pos.rgb == (r,g,b):
                # found a node representing this color
                pos.increment(weight)
                break

            # need to find a child
            child = self.which_child(min,length,r,g,b)

            if pos.children[child] == None:
                # no child exists, add new child & quit
                pos.children[child] = Node(r,g,b)
                pos.children[child].increment(weight-1)
                self.make_interior_node(pos)
                break
            else:
                # a child is there, descend 
                pos = pos.children[child]
            
    def make_interior_node(self,node):
        if not node.is_leaf_node():
            return

        # it is a leaf, but now has children. Must be made into a leaf
        (r,g,b) = node.rgb
        n = node.n_local_pixels
        node.make_interior_node()        
        #print "reinsert:",r,g,b,n
        self.insert_pixel(r,g,b,n)
        
            #    if pos.is_leaf_node():                    
            #        # if this is a leaf, make it internal and push its
            #        # contents down to be another new child
            #        (this_r,this_g,this_b) = pos.rgb
            #        this_as_child = self.which_child(
            #            min,length,this_r,this_g,this_b)
            #        
            #        if this_as_child == child:
            #            pos.children[child].increment()
            #        else:
            #            # create another node for the freshly-inserted pixel
            #            new_child = Node(this_r,this_g,this_b)
            #            new_child.n_local_pixels = pos.n_local_pixels
            #            new_child.n_tree_pixels = pos.n_local_pixels+1
            #            pos.children[child] = new_child 
            #        
            #        pos.make_interior_node()
            #    
            #    #add new child...
            #    break
            
                
        
