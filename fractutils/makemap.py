#!/usr/bin/env python

# create a color map based on an image.
# vaguely octree-inspired

from PIL import ImageFile

class Node:
    def __init__(self,r,g,b,count):
        self.branches = [None] * 8
        self.r = r
        self.g = g
        self.b = b
        self.count = count
        self._isleaf = True
        
    def isleaf(self):
        return self._isleaf

    def matches(self,r,g,b):
        return self.r == r and self.g == g and self.b == b
    
class T:
    R = 0
    G = 1
    B = 2
    def __init__(self):
        'Load an image from open stream "file"'
        self.root = None

    def addLeafNode(self,r,g,b,count):
        return Node(r,g,b,count)

    def addInternalNode(self,r,g,b):
        n = Node(r,g,b,0)
        n._isleaf = False
        return n
    
    def load(self,file):
        p = ImageFile.Parser()
        while 1:
            s = file.read(1024)
            if not s:
                break
            p.feed(s)

        self.im = p.close()
        
    def getdata(self):
        return self.im.getdata()
    
    def build(self):
        for (r,g,b) in self.getdata():
            self.insert_pixel(r,g,b)

    def getBranch(self,r,g,b,nr,ng,nb):
        branch = 0
        if r > nr:
            branch += 4
        if g > ng:
            branch += 2
        if b > nb:
            branch += 1
        return branch

    def getInteriorRGB(self,r,g,b,nr,ng,nb,size):
        if r > nr:
            nr += size
        else:
            nr -= size
        if g > ng:
            ng += size
        else:
            ng -= size
        if b > nb:
            nb += size
        else:
            nb -= size
        return (nr,ng,nb)
    
    def insertNode(self,parent,r,g,b,count,nr,ng,nb,size):
        if parent == None:
            parent = self.addLeafNode(r,g,b,count)
        elif parent.matches(r,g,b) and parent.isleaf():
            parent.count += 1
        elif parent.isleaf():
            # replace it with a new interior node, reinsert this leaf and the new one
            currentleaf = parent
            parent = self.addInternalNode(nr,ng,nb)
            currentbranch = self.getBranch(
                currentleaf.r,currentleaf.g,currentleaf.b,nr,ng,nb)
            newbranch = self.getBranch(
                r,g,b,nr,ng,nb)
            if currentbranch == newbranch:
                # need to subdivide further
                (nr,ng,nb) = self.getInteriorRGB(r,g,b,nr,ng,nb,size/2)
                parent.branches[newbranch] = self.addInternalNode(nr,ng,nb)
                parent.branches[newbranch] = self.insertNode(
                    parent.branches[newbranch],r,g,b,1,nr,ng,nb,size/2)
                parent.branches[newbranch] = self.insertNode(
                    parent.branches[newbranch],
                    currentleaf.r, currentleaf.g, currentleaf.b,
                    currentleaf.count,
                    nr,ng,nb,size/2)
            else:
                parent.branches[currentbranch] = currentleaf
                parent.branches[newbranch] = self.addLeafNode(r,g,b,1)
        else:
            # parent is an interior node, recurse to appropriate branch
            newbranch = self.getBranch(r,g,b,nr,ng,nb)
            (nr,ng,nb) = self.getInteriorRGB(r,g,b,nr,ng,nb,size/2)
            parent.branches[newbranch] = self.insertNode(
                parent.branches[newbranch],r,g,b,1,nr,ng,nb,size/2)
        return parent
    
    def insert_pixel(self,r,g,b):
        self.root = self.insertNode(self.root,r,g,b,1,127,127,127,128)



