#!/bin/sh
pushd dist
mkisofs -J -R -o gf4d.iso *.gz *.rpm
popd dist
