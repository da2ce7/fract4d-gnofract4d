#!/bin/sh

rm -f MANIFEST
rm -rf build
rm -f fract4d/*.so fract4d/*.pyc fract4dgui/*.so fract4dgui/*.pyc
$BUILD_PYTHON ./setup.py clean
$BUILD_PYTHON ./setup.py build
$BUILD_PYTHON ./setup.py my_bdist_rpm --binary-only --requires "gtk2 >= 2.0 pygtk2 >= 2.0 python >= $1 python < $2 gcc >= 2.95"

