#!/bin/sh

# Weird hack to build separate RPMs for different Python versions, due to
# incompatible Python API formats. (Fsckers).

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

mv dist/gnofract4d-2.3-1.i386.rpm dist/gnofract4d-python22-2.3-1.i386.rpm 

# Python 2.3 version
export BUILD_PYTHON_VERSION=2.3
export BUILD_PYTHON=/usr/bin/python2.3

rm -rf build
rm -f fract4d/*.so fract4d/*.pyc fract4dgui/*.so fract4dgui/*.pyc
$BUILD_PYTHON setup.py clean
$BUILD_PYTHON setup.py build
$BUILD_PYTHON setup.py bdist_rpm --binary-only --requires "gtk2 >= 2.0 pygtk2 >= 1.99 python >= 2.3 python < 2.4 gcc >= 2.95"

mv dist/gnofract4d-2.3-1.i386.rpm dist/gnofract4d-python23-2.3-1.i386.rpm 

# Python 2.4 version
# export BUILD_PYTHON_VERSION=2.4
# export BUILD_PYTHON=/usr/local/bin/python2.4

# rm -rf build
# rm -f fract4d/*.so fract4d/*.pyc fract4dgui/*.so fract4dgui/*.pyc
# $BUILD_PYTHON setup.py clean
# $BUILD_PYTHON setup.py build
# $BUILD_PYTHON setup.py bdist_rpm --binary-only --requires "gtk2 >= 2.0 pygtk2 >= 1.99 python >= 2.4 python < 2.5 gcc >= 2.95"

# mv dist/gnofract4d-2.3-1.i386.rpm dist/gnofract4d-python24-2.3-1.i386.rpm 

unset BUILD_PYTHON_VERSION
unset BUILD_PYTHON

# make ISO image for testing on different OSes
pushd dist
mkisofs -J -R -o gf4d.iso *.gz *.rpm
popd dist
