#!/bin/sh
pushd dist
mkisofs -o gf4d.iso *.gz *.rpm
popd dist
