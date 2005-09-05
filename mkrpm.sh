#!/bin/sh

echo $CC
rm -f MANIFEST
rm -rf build
rm -rf /var/tmp/gnofract4d-*buildroot
rm -f fract4d/*.so fract4d/*.pyc fract4dgui/*.so fract4dgui/*.pyc
$1 ./setup.py clean 
$1 ./setup.py my_build 
$1 ./setup.py my_bdist_rpm --binary-only --requires "gtk2 >= 2.0 pygtk2 >= 1.99 python >= $2 python < $3 gcc >= 2.95" 

