#!/usr/bin/env python

# compare output of fract4d with that of older version
# complain about anything too different

import os

def render2_0(fctfile):
    cmd = "./fractal.py %s" % fctfile
    #print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("error running new version")
    return os.path.basename(fctfile) + ".tga"
    
def render1_9(fctfile):
    outfile = os.path.basename(fctfile) + ".png"
    cmd = "gnofract4d -p %s -i 64 -s %s -q" % (fctfile, outfile)
    #print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("error running old version")
    return outfile

def render(fctfile):
    a = render2_0(fctfile)
    b = render1_9(fctfile)
    diff_file = os.path.basename(b)[:-8] + ".diff.raw" # remove .fct.png
    cmd = "composite -compose difference %s %s %s" % (a,b,diff_file)
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("error running imagemagick")
    print diff_file
    
if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        render(f)

