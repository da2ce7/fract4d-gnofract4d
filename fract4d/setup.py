#!/usr/bin/env python

import shutil
from distutils.core import setup, Extension

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
                      ]
    )

setup (name = 'fract4dc',
       version = '1.0',
       description = 'A module for calling fractal functions built on-the-fly by Gnofract4D',
       ext_modules = [module1])

# to make testing easier and allow us to run without installing,
# copy new module to current dir

#FIXME find file properly
shutil.copy("build/lib.linux-i686-2.2/fract4dc.so","fract4dc.so") 

