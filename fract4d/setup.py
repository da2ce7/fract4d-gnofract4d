#!/usr/bin/env python

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
    define_macros = [ ('_REENTRANT',1)
                      #('DEBUG_CREATION',1)
                      ]
    )

setup (name = 'fract4dc',
       version = '1.0',
       description = 'A module for calling fractal functions built on-the-fly by Gnofract4D',
       ext_modules = [module1])
