#!/bin/sh

# Weird hack to build separate RPMs for different Python versions, due to
# incompatible Python API formats. (Fsckers).

# if you want to build your own RPM using this script, 
# change the paths to different python versions to something which works for you
# use an pre-g++-3.4 compiler to build binary distributions - 3.4 changes the 
# ABI again (groan) and hardly any of the distributions targeted have it

export CC=/usr/local/bin/gcc33
export CXX=/usr/local/bin/g++33

# python 2.2 version
export BUILD_PYTHON_VERSION=2.2
export BUILD_PYTHON=/usr/bin/python2.2
export MIN=2.2
export MAX=2.3
 
./mkrpm.sh $BUILD_PYTHON $MIN $MAX
mv dist/gnofract4d-2.11-1.i386.rpm dist/gnofract4d-python22-2.11-1.i386.rpm 

# Python 2.3 version
export BUILD_PYTHON_VERSION=2.3
export BUILD_PYTHON=/usr/bin/python2.3
export MIN=2.3
export MAX=2.4

./mkrpm.sh $BUILD_PYTHON $MIN $MAX
mv dist/gnofract4d-2.11-1.i386.rpm dist/gnofract4d-python23-2.11-1.i386.rpm 

# use 3.4 again for Python 2.4, since the only distribution I know 
# which uses it is FC4, which also only has g++3.4 installed
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++

# Python 2.4 version
export BUILD_PYTHON_VERSION=2.4
export BUILD_PYTHON=/usr/bin/python2.4
export MIN=2.4
export MAX=2.5

./mkrpm.sh $BUILD_PYTHON $MIN $MAX
mv dist/gnofract4d-2.11-1.i386.rpm dist/gnofract4d-python24-2.11-1.i386.rpm 

unset BUILD_PYTHON_VERSION
unset BUILD_PYTHON
unset CC
unset CXX

# source version
./setup.py sdist

# make ISO image for testing on different OSes
pushd dist
mkisofs -J -R -o gf4d.iso *2.11*.gz *2.11*.rpm
popd dist



