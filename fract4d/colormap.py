#!/usr/bin/env python
# code to load a .map file and produce a cmap object

import fract4dc
import re

rgb_re = re.compile(r'\s*(\d+)\s+(\d+)\s+(\d+)')
class ColorMap:
    def __init__(self,file=None):
        if file == None:
            r = [(0.0, 0,0,0,0)]
        else:
            r = []; i = 0
            for line in file:
                m = rgb_re.match(line)
                if m != None:
                    r.append((i/256.0,
                              int(m.group(1)),
                              int(m.group(2)),
                              int(m.group(3)),
                              255))
                i += 1
        self.r = r
        self.cmap = fract4dc.cmap_create(r)
        
    def lookup(self,dist):
        return fract4dc.cmap_lookup(self.cmap,dist)
