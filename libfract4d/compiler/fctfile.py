#!/usr/bin/env python
# import Gnofract4d 1.4-1.9 .fct files

import string

class T:
    def __init__(self,f):
        for line in f:
            x = line.split("=",1)
            if len(x) == 0: continue
            if len(x) < 2:
                val = None
            else:
                val = x[1]
            name = x[0]
            
            print "%s : %s" % (name,val)

def (fname):
    f = open(fname)
    return FctFile(f)
