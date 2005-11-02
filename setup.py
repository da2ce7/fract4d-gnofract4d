#!/usr/bin/env python

import shutil
from distutils.core import setup, Extension
import distutils.sysconfig
import os
import commands
import sys

gnofract4d_version = "2.11"

if float(sys.version[:3]) < 2.2:
    print "Sorry, you need python 2.2 or higher to run Gnofract 4D."
    print "You have version %s. Please upgrade." % sys.version
    sys.exit(1)

# hack to use a different Python for building if an env var is set
# I use this to build python-2.2 and 2.4 RPMs.
build_version = os.environ.get("BUILD_PYTHON_VERSION")
build_python = os.environ.get("BUILD_PYTHON")

if build_version and build_python and sys.version[:3] != build_version:
    print sys.version[:3], build_version
    args = ["/usr/bin/python"] + sys.argv
    print "running other Python version %s with args: %s" % (build_python,args)
    os.execv(build_python, args)

import my_bdist_rpm
import my_build
import my_build_ext

# use currently specified compilers, not ones from when Python was compiled
# this is necessary for cross-compilation
compiler = os.environ.get("CC","gcc")
cxxcompiler = os.environ.get("CXX","g++")

module1 = Extension(
    'fract4d.fract4dc',
    sources = [
    'fract4d/c/fract4dmodule.cpp',
    'fract4d/c/cmap.cpp',
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
    #'stdc++'
    ],
    extra_compile_args = [
    '-O0',
    '-Wall',
    ],
    define_macros = [ ('_REENTRANT',1),
                      #('NO_CALC', 1),
                      #('DEBUG_CREATION',1)
                      ],
    undef_macros = [ 'NDEBUG']
    
    )

module_cmap = Extension(
    'fract4d.fract4d_cmap',
    sources = [
    'fract4d/c/cmap.cpp'
    ],
    include_dirs = [
    'fract4d/c'
    ],
    libraries = [
    #'stdc++'
    ],
    define_macros = [ ('_REENTRANT', 1)]
    )

# GUI extension needs to link against gtk+ and gconf. We use pkg-config
# to find the appropriate set of includes and libs

pkgs = "gtk+-2.0 gconf-2.0"

def call_package_config(package,option):
    '''invoke pkg-config, if it exists, to find the appropriate
    arguments for a library'''
    cmd = "pkg-config %s %s" % (package, option)
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        print >>sys.stderr, "Can't set up. Error running '%s'." % cmd
        print >>sys.stderr, output
        print >>sys.stderr, "Possibly you don't have one of these installed: '%s'." % package
        sys.exit(1)

    return output.split()

gtk_flags = call_package_config(pkgs,"--cflags")
gtk_libs =  call_package_config(pkgs,"--libs")


module2 = Extension(
    'fract4dgui.fract4dguic',
    sources = [
    'fract4dgui/c/guicmodule.cpp',
    ],
    include_dirs = [
    'fract4dgui/c',
    'fract4d/c/'
    ],
    libraries = [
    #'stdc++'
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
       version = gnofract4d_version,
       description = 'A program to draw fractals',
       long_description = \
'''Gnofract 4D is a fractal browser. It can generate many different fractals, 
including some which are hybrids between the Mandelbrot and Julia sets,
and includes a Fractint-compatible parser for your own fractal formulas.''',
       author = 'Edwin Young',
       author_email = 'edwin@bathysphere.org',
       maintainer = 'Edwin Young',
       maintainer_email = 'edwin@bathysphere.org',
       keywords = "fractal Mandelbrot Julia fractint",
       url = 'http://gnofract4d.sourceforge.net/',
       packages = ['fract4d', 'fract4dgui', 'fractutils'],
       ext_modules = [module1, module_cmap, module2],
       scripts = ['gnofract4d'],
       license = 'BSD',
       data_files = [
           # color maps
           ('share/maps/gnofract4d',
            get_files("maps",".map")),

           # formulas
           ('share/formulas/gnofract4d',
            get_files("formulas","frm") + get_files("formulas", "ucl")),

           # documentation
           ('share/gnome/help/gnofract4d/C',
            ['doc/gnofract4d-manual/C/gnofract4d-manual.xml',
             'doc/gnofract4d-manual/C/stdlib.xml']),
           ('share/gnome/help/gnofract4d/C/figures',
            get_files("doc/gnofract4d-manual/C/figures",".png")),

           #icons
           ('share/pixmaps/gnofract4d', get_files('pixmaps','.png')),
            
           # .desktop file
           ('share/gnofract4d', ['gnofract4d.desktop']),

           # MIME type registration
           ('share/mime/packages', ['gnofract4d-mime.xml']),
           
           # doc files
           ('share/doc/gnofract4d-%s/' % gnofract4d_version,
            ['COPYING', 'README']),
           ],
       cmdclass={
           "my_bdist_rpm": my_bdist_rpm.my_bdist_rpm,
           "build" : my_build.my_build,
           "my_build_ext" : my_build_ext.my_build_ext}
       )

# I need to find the file I just built and copy it up out of the build
# location so it's possible to run without installing. Can't find a good
# way to extract the actual target directory out of distutils, hence
# this egregious hack

so_extension = distutils.sysconfig.get_config_var("SO")

lib_targets = {
    "fract4dguic" + so_extension : "fract4dgui",
    "fract4dc" + so_extension : "fract4d",
    "fract4d_cmap" + so_extension : "fract4d"
    }

def copy_libs(dummy,dirpath,namelist):
     for name in namelist:
         target = lib_targets.get(name)
         if target != None:
             shutil.copy(os.path.join(dirpath, name), target)
            
os.path.walk("build",copy_libs,None)

