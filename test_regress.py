#!/usr/bin/env python

# compare output of fract4d with that of older version
# complain about anything too different

# this requires the Python Imaging Library and gnofract4d 1.9
# to run.

import os
import operator
from PIL import Image, ImageChops, ImageFilter, ImageStat

good_files = [
    # look ok
    "abyssal.fct", 
    "antialias_bug.fct", 
    "bailout_breaker.fct", 
    #"barnsley_t2_odd.fct", 
    "barnsley_worm.fct",
    "cathedral.fct",
    "chaos_engine.fct",
    "compass_rose.fct",
    "crest.fct",
    "cubicspiral.fct",
]

bad_files = [
    # not equivalent
    "caduceus.fct",
    "caduceus_fixed.fct",
    "contrail.fct",
    "daisychain.fct",
]

def render2_0(fctfile):
    cmd = "fract4d/fractal.py %s" % fctfile
    #print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("error running new version")

    outfile = os.path.basename(fctfile) + ".tga"
    return Image.open(outfile)
    
def render1_9(fctfile):
    outfile = os.path.basename(fctfile) + ".png"
    cmd = "gnofract4d -p %s -i 64 -s %s -q" % (fctfile, outfile)
    #print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("error running old version")

    return Image.open(outfile)

def render(fctfile):
    a = render2_0(fctfile)
    b = render1_9(fctfile)
    sa = a.filter(ImageFilter.BLUR)
    sb = b.filter(ImageFilter.BLUR)
    diff = ImageChops.difference(sa,sb)

    diff.save(os.path.basename(fctfile) + ".diff.png")
    
    stats = ImageStat.Stat(diff)
    print "%f\t%d\t%f" % \
          (total(stats.mean), total(stats.median), total(stats.rms))

def total(l):
    return reduce(operator.__add__,l)

def check_file(f):
    try:
        print "%s\t" % f,
        render(f)
    except Exception, err:
        print "Error %s" % err

if __name__ == '__main__':
    import sys
    print "file\tmean\tmedian\trms"
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:        
            check_file(f)
    else:
        for f in [ "testdata/" + x for x in good_files]:
            check_file(f)
        for f in [ "testdata/" + x for x in bad_files]:
            check_file(f)

