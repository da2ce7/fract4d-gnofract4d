#!/bin/sh

# Weird hack to build separate RPMs for different Python versions, due to
# incompatible API formats. (Fsckers).

# if you want to build your own RPM using this script, 
# change the path to Python2.3 to something which works for you

# python 2.2 version
unset BUILD_PYTHON_VERSION
unset BUILD_PYTHON

rm -rf build
rm -f fract4d/*.so fract4d/*.pyc fract4dgui/*.so fract4dgui/*.pyc
./setup.py clean
./setup.py build
./setup.py sdist
./setup.py bdist_rpm --binary-only

mv dist/gnofract4d-2.2-1.i386.rpm dist/gnofract4d-python22-2.2-1.i386.rpm 

# Python 2.3 version
export BUILD_PYTHON_VERSION=2.3
export BUILD_PYTHON=/usr/bin/python2.3

rm -rf build
rm -f fract4d/*.so fract4d/*.pyc fract4dgui/*.so fract4dgui/*.pyc
$BUILD_PYTHON setup.py clean
$BUILD_PYTHON setup.py build
$BUILD_PYTHON setup.py bdist_rpm --binary-only --requires "gtk2 >= 2.0 pygtk2 >= 1.99 python >= 2.3 python < 2.4 gcc >= 2.95"

mv dist/gnofract4d-2.2-1.i386.rpm dist/gnofract4d-python23-2.2-1.i386.rpm 

unset BUILD_PYTHON_VERSION
unset BUILD_PYTHON
