#!/usr/bin/env python

import shutil
from distutils.core import setup, Extension
import distutils.sysconfig
import os
import commands
import sys

module1 = Extension(
    'fract4d.fract4dc',
    sources = [
    'fract4d/c/fract4dmodule.cpp',
    'fract4d/c/cmap.c',
    'fract4d/c/pointFunc.cpp',
    'fract4d/c/fractFunc.cpp',
    'fract4d/c/STFractWorker.cpp',
    'fract4d/c/MTFractWorker.cpp',
    'fract4d/c/image.cpp'
    ],
    include_dirs = [
    'fract4d/c'
    ],
    libraries = [
    'stdc++'
    ],
    extra_compile_args = [
    ],
    define_macros = [ ('_REENTRANT',1),
                      #('DEBUG_CREATION',1)
                      ],
    undef_macros = [ 'NDEBUG']
    
    )

# GUI extension needs to link against gtk+. We use pkg-config
# to find the appropriate set of includes and libs

gtk_pkg = "gtk+-2.0"

def call_package_config(package,option):
    '''invoke pkg-config, if it exists, to find the appropriate
    arguments for a library'''
    cmd = "pkg-config %s %s" % (package, option)
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        print >>sys.stderr, "Can't set up. Error running '%s'." % cmd
        print >>sys.stderr, output
        sys.exit(1)

    return output.split()

def strip_option(arg):
    ' change -lfoo into foo'
    if arg[0] == "-" and len(arg) > 2:
        arg = arg[2:]
    return arg

gtk_flags = call_package_config(gtk_pkg,"--cflags")
gtk_libs =  call_package_config(gtk_pkg,"--libs")


module2 = Extension(
    'gui.fract4dguic',
    sources = [
    'gui/c/guicmodule.cpp',
    ],
    include_dirs = [
    'gui/c',
    'fract4d/c/'
    ],
    libraries = [
    'stdc++'
    ],
    extra_compile_args = gtk_flags,
    extra_link_args = gtk_libs,    
    define_macros = [ ('_REENTRANT',1),
                      #('DEBUG_CREATION',1)
                      ],
    undef_macros = [ 'NDEBUG']    
    )

def get_files(dir,ext):
    return [ os.path.join(dir,x) for x in os.listdir(dir) if x.endswith(ext)] 

setup (name = 'gnofract4d',
       version = '2.0',
       description = 'A program to draw fractals',
       author = 'Edwin Young',
       author_email = 'edwin@sourceforge.net',
       url = 'http://gnofract4d.sourceforge.net/',
       packages = ['fract4d', 'gui'],
       ext_modules = [module1, module2],
       scripts = ['gnofract4d'],
       data_files = [
           # color maps
           ('share/maps/gnofract4d',
            get_files("maps",".map")),

           # formulas
           ('share/formulas/gnofract4d',
            ['fract4d/gf4d.frm', 'fract4d/gf4d.cfrm']),

           # documentation
           ('share/gnome/help/gnofract4d/C',
            ['doc/gnofract4d-manual/C/gnofract4d-manual.xml',
             'fract4d/stdlib.xml']),
           ('share/gnome/help/gnofract4d/C/figures',
            get_files("doc/gnofract4d-manual/C/figures",".png")),

           #icons
           ('share/pixmaps/gnofract4d', get_files('pixmaps','.png')),
            
           # GNOME .desktop file
           ('/share/gnome/apps/Graphics/', ['gnofract4d.desktop']),           
           ]
       )

# I need to find the file I just built and copy it up out of the build
# location so it's possible to run without installing. Can't find a good
# way to extract the actual target directory out of distutils, hence
# this egregious hack

so_extension = distutils.sysconfig.get_config_var("SO")

lib_targets = {
    "fract4dguic" + so_extension : "gui",
    "fract4dc" + so_extension : "fract4d"}

def copy_libs(dummy,dirpath,namelist):
     for name in namelist:
         target = lib_targets.get(name)
         if target != None:
             shutil.copy(os.path.join(dirpath, name), target)
            
os.path.walk("build",copy_libs,None)




