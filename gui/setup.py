#!/usr/bin/env python

import shutil
import commands
import sys

from distutils.core import setup, Extension

gtk_pkg = "gtk+-2.0"

def call_package_config(package,option):
    '''invoke pkg-config, if it exists, to find the appropriate
    arguments for a library'''
    cmd = "pkg-config %s %s" % (package, option)
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        print >>sys.stderr, "Can't set up. Error running pkg-config."
        print >>sys.stderr, output
        sys.exit(1)

    return output.split()

def strip_option(arg):
    ' change -lfoo into foo'
    if arg[0] == "-" and len(arg) > 2:
        arg = arg[2:]
    return arg

gtk_flags = call_package_config(gtk_pkg,"--cflags")
gtk_libs = map(strip_option,call_package_config(gtk_pkg,"--libs"))


module1 = Extension(
    'fract4dguic',
    sources = [
    'c/guicmodule.cpp',
    ],
    include_dirs = [
    'c',
    '../fract4d/c/'
    ],
    libraries = [
    'stdc++'
    ] + gtk_libs,
    extra_compile_args = [
    ] + gtk_flags,
    
    define_macros = [ ('_REENTRANT',1),
                      #('DEBUG_CREATION',1)
                      ],
    undef_macros = [ 'NDEBUG']
    
    )

setup (name = 'fract4dguic',
       version = '1.0',
       description = "Helper functions for the gui which need to be in C because they aren't available from PyGTK. Not generally useful.",
       ext_modules = [module1])

# to make testing easier and allow us to run without installing,
# copy new module to current dir

#FIXME find file properly
shutil.copy("build/lib.linux-i686-2.2/fract4dguic.so","fract4dguic.so") 

