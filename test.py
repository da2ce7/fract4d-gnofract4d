#!/usr/bin/env python

# run all the tests
import os
import sys
import unittest

print "Running all unit tests. This may take several minutes."

def main():
    os.chdir('fract4d')
    os.system('./test.py')
    os.chdir('../fract4dgui')
    os.system('./test.py')
    os.chdir('../fractutils')
    os.system('./test.py')
    
if __name__ == '__main__':
    main()




