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
        self.is_leaf = True
        self.children = [None for x in range(8)] # no children yet

    def increment_children(self):
        self.n_tree_pixels += 1

    def increment(self,x=1):
        self.n_local_pixels += x

    def is_leaf_node(self):
        return self.is_leaf

    def make_interior_node(self,r,g,b):
        self.rgb = (r,g,b)
        self.is_leaf = False
        self.n_local_pixels=0

def _make_bit_table():
    # create an array from i -> [bits of i]
    x = []
    bits = [ 0x80, 0x40, 0x20, 0x10, 8, 4, 2, 1]
    for i in xrange(256):
        bitarray = [(i & bit) and 1 or 0 for bit in bits]
        #print bitarray
        x.append(bitarray)

    return x

class T:
    R = 0
    G = 1
    B = 2
    bit_table = _make_bit_table()
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
        data = [ x for x in self.getdata()]
        npixels = len(data)
        if npixels==0:
            return

        data.sort()
        count = 1
        i = 0
        for i in xrange(npixels-1):
            pixel = data[i]
            next = data[i+1]
            if pixel == next:
                count += 1
            else:
                self.insert_pixel(pixel[0],pixel[1],pixel[2],count)
                count=1

        # last pixel
        (r,g,b) = data[-1]
        self.insert_pixel(r,g,b,count)
        
        self.update_counts(self.root)
        
    def dump_octree(self,node,prefix=""):
        if node == None:
            return ""
        val = "%s[(%s,%s,%s %s)\n" % \
              (prefix, node.rgb,node.n_local_pixels, node.n_tree_pixels, node.error)
        child_prefix = "  " + prefix
        for i in xrange(8):
            child = node.children[i]
            if child != None:
                val += child_prefix + "%d:" % i + self.dump_octree(child,child_prefix)
            
        val += "%s]\n" % prefix
        return val

    def count_leaves(self,node):
        if not node:
            return 0

        if node.is_leaf_node():
            return 1
        else:
            count = 0
            for child in node.children:
                count += self.count_leaves(child)

            return count

    def remove_least_node(self):
        
        pass

    def get_reduce_targets(self,node,parent):
        if not node:
            return []
        
        if node.is_leaf_node():
            return []

        targets = [(node.error, node,parent)]
        for child in node.children:
            targets += self.get_reduce_targets(child,node)

        return targets

    def reduce_node(self,target):
        (error,child,parent) = target
        parent.n_local_pixels += child.n_local_pixels
        parent.error = 0
        parent.is_leaf = True
        
        # remove child from parent
        for i in xrange(len(parent.children)):
            if parent.children[i] == child:
                parent.children[i] = None
                break

        
    def reduce(self, target_nodes):
        targets = self.get_reduce_targets(self.root,None)
        targets.sort()

        n = self.count_leaves(self.root)
        while n > target_nodes:
            self.reduce_node(targets[0])
            targets.pop(0)
            n -= 1
        
    def update_counts(self,node):
        if not node:
            return (0,0)
        
        if node.is_leaf_node():
            return (node.n_local_pixels,0)

        (sum,error) = (0,0)
        for child in node.children:
            if child != None:
                (child_count,child_error) = self.update_counts(child)
                sum += child_count
                #error += child_error

                error += self.sqr_error(node.rgb, child.rgb) * child_count
                
        node.n_tree_pixels = sum
        node.error = error
        return (sum,error)

    def sqr_error(self,a,b):
        err = 0
        for (x,y) in zip(a,b):
            err += (x-y)*(x-y)
        return err
    
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
        #print "insert(%d,%d,%d,%d)" % (r,g,b,weight)
        
        min = [0,0,0]
        length = 256

        pos = self.root
        if not pos:
            self.root = Node(r,g,b)
            self.root.increment(weight-1)
            return
        
        while length > 0:
            l2 = (length-1) * 0.5
            (ir,ig,ib) = (min[0] + l2, min[1]+ l2, min[2] + l2)

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
                self.make_interior_node(pos,ir,ig,ib)
                break
            else:
                # a child is there, descend 
                pos = pos.children[child]
            
    def make_interior_node(self,node,ir,ig,ib):
        if not node.is_leaf_node():
            return

        # it is a leaf, but now has children. Must be made into a leaf
        (r,g,b) = node.rgb
        n = node.n_local_pixels
        node.make_interior_node(ir,ig,ib)        
        #print "reinsert:",r,g,b,n
        self.insert_pixel(r,g,b,n)
        
def do_prof():
    mm = T(open("tattered2.jpg","rb"))
    mm.build_octree()

                   
if __name__ == '__main__':
    import hotshot
    import sys
    prof = hotshot.Profile("makemap.prof")
    prof.runcall(do_prof)
    prof.close()
