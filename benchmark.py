#!/usr/bin/env python

import sys
import os
import getopt
import operator
from time import time as now

# gettext
import gettext
os.environ.setdefault('LANG', 'en')
if os.path.isdir('po'):
    gettext.install('gnofract4d','po')
else:
    gettext.install('gnofract4d')

import gtk

from fract4d import fractmain, image
from fract4dgui import main_window

files = [
    'testdata/std.fct',
    'testdata/param.fct',
    'testdata/valley_test.fct',
    'testdata/trigcentric.fct',
    'testdata/zpower.fct'
    ]

times = []

last_time = None
pos = 0

def run_gui():
    global last_time, pos
    window = main_window.MainWindow()

    window.f.set_size(320,240)
    window.f.thaw()

    last_time = now()

    def status_changed(f,status):
        global last_time, pos
        if status == 0:
            # done
            new_time = now()
            times.append(new_time - last_time)
            last_time = new_time
            pos += 1
            if pos < len(files):
                window.load(files[pos])
            else:
                gtk.main_quit()

    window.f.connect('status-changed', status_changed)
    window.load(files[0])
    gtk.main()

def run_nogui():
    main = fractmain.T()
    print main.compiler.path_lists
    last_time = now()
    for file in files:
        main.load(file)
        im = image.T(320,240)
        main.draw(im)
        im.save(file + ".png")
        new_time = now()
        times.append(new_time - last_time)
            
if len(sys.argv) > 1 and sys.argv[1] == "--nogui":
    run_nogui()
else:
    run_gui()
    
for (file,time) in zip(files,times):
    print "%.4f %s" % (time,file)

print reduce(operator.__add__,times,0)

