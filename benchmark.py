#!/usr/bin/env python

import sys
import os
import getopt
from time import time as now

# gettext
import gettext
os.environ.setdefault('LANG', 'en')
if os.path.isdir('po'):
    gettext.install('gnofract4d','po')
else:
    gettext.install('gnofract4d')

import gtk

from fract4dgui import main_window

window = main_window.MainWindow()

window.f.set_size(320,240)
window.f.thaw()

pos = 0

files = [
    'testdata/std.fct',
    'testdata/param.fct',
    'testdata/valley_test.fct',
    'testdata/trigcentric.fct',
    'testdata/zpower.fct'
    ]

times = []

last_time = now()

def status_changed(f,status):
    global pos, files, times, last_time
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

print times

