#!/bin/sh

# Weird hack to build separate RPMs for different Python versions, due to
# incompatible Python API formats. (Fsckers).

# if you want to build your own RPM using this script, 
# change the paths to different python versions to something which works for you

# python 2.2 version
export BUILD_PYTHON_VERSION=2.2
export BUILD_PYTHON=/usr/local/bin/python2.2
export MIN=2.2
export MAX=2.3

./mkrpm.sh $BUILD_PYTHON $MIN $MAX
mv dist/gnofract4d-2.10-1.i386.rpm dist/gnofract4d-python22-2.10-1.i386.rpm 

# Python 2.3 version
export BUILD_PYTHON_VERSION=2.3
export BUILD_PYTHON=/usr/bin/python2.3
export MIN=2.3
export MAX=2.4

./mkrpm.sh $BUILD_PYTHON $MIN $MAX
mv dist/gnofract4d-2.10-1.i386.rpm dist/gnofract4d-python23-2.10-1.i386.rpm 

# Python 2.4 version
export BUILD_PYTHON_VERSION=2.4
export BUILD_PYTHON=/usr/local/bin/python2.4
export MIN=2.4
export MAX=2.5

./mkrpm.sh $BUILD_PYTHON $MIN $MAX
mv dist/gnofract4d-2.10-1.i386.rpm dist/gnofract4d-python24-2.10-1.i386.rpm 


# source version
./setup.py sdist

# make ISO image for testing on different OSes
pushd dist
mkisofs -J -R -o gf4d.iso *.gz *.rpm
popd dist

unset BUILD_PYTHON_VERSION
unset BUILD_PYTHON
