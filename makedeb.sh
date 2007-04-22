#!/bin/bash
# This script should tie everything together to create a .deb. Extract
# the tarball for this in the directory where you've untarred the source and 
# run this script from there.

dh_make -n -s
cp ./debian-custom/* ./debian
debuild -rfakeroot
