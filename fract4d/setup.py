#!/usr/bin/env python

import shutil
from distutils.core import setup, Extension
import distutils.sysconfig
import os

module1 = Extension(
    'fract4dc',
    sources = [
    'c/fract4dmodule.cpp',
    'c/cmap.c',
    'c/pointFunc.cpp',
    'c/fractFunc.cpp',
    'c/STFractWorker.cpp',
    'c/MTFractWorker.cpp',
    'c/image.cpp'
    ],
    include_dirs = [
    'c'
    ],
    libraries = [
    'stdc++'
    ],
    extra_compile_args = [
    '-O0'
    ],
    define_macros = [ ('_REENTRANT',1),
                      #('DEBUG_CREATION',1)
                      ],
    undef_macros = [ 'NDEBUG']
    
    )

setup (name = 'fract4dc',
       version = '1.0',
       description = 'A module for calling fractal functions built on-the-fly by Gnofract4D',
       ext_modules = [module1])

# I need to find the file I just built and copy it up out of the build
# location so it's possible to run without installing. Can't find a good
# way to extract the actual target directory out of distutils, hence
# this egregious hack

so_extension = distutils.sysconfig.get_config_var("SO")

def copy_libs(dummy,dirpath,namelist):
    for name in namelist:
        if name.endswith(so_extension):
            shutil.copy(os.path.join(dirpath, name), name)
            
os.path.walk("build",copy_libs,None)


