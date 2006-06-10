#!/usr/bin/env python

# create a color map based on an image.
# vaguely octre-inspired

from PIL import ImageFile

class T:
    R = 0
    G = 1
    B = 2
    def __init__(self):
        'Load an image from open stream "file"'
        N = 8
        self.nodes = [0] * 8**N

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

    def getIndex(self,r,g,b,n):
        r = r >> (8-n)
        g = g >> (8-n)
        b = b >> (8-n)        
        return (r << n*2) | (g << n) | b
    
    def insert_pixel(self,r,g,b):
        self.nodes[self.getIndex(r,g,b,8)] += 1

    def combine(self,r,g,b,n):
        return (r << n*2) | (g << n) | b
        
    def children(self,r,g,b,n):
        # all 8 pixels which are (r|r+1,g|g+1,b|b+1),
        # ie children of node (which must be even) at level n
        delta = 1 << (8-n)
        r = r >> (8-n)
        g = g >> (8-n)
        b = b >> (8-n)
        indexes = [
            (r,g,b),
            (r,g,b+delta),
            (r,g+delta,b),
            (r,g+delta, b+delta),
            (r+delta,g,b),
            (r+delta, g, b+delta),
            (r+delta, g+delta, b),
            (r+delta, g+delta, b+delta)]
        
        return [ self.combine(a,b,c,n) for (a,b,c) in indexes]
            
        
    def most_popular(self,n):
        pops = []
        minpop = 0
        for i in xrange(len(self.nodes)):
            if self.nodes[i] > minpop:
                pops.append((self.nodes[i],i))
        pops.sort()
        pops.reverse()
        return [i for (pop,i) in pops[:n]]

if __name__ == "__main__":
    import sys
    mm = T()
    mm.load(open(sys.argv[1]))
    mm.build()
    mp = mm.most_popular(256)
    for c in mp:
        (r,g,b) = (c >> 16, c >> 8 & 0xff, c & 0xff)
        print "%d %d %d" % (r,g,b)

