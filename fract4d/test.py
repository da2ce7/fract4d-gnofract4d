#!/usr/bin/env python

import unittest
import test_fractlexer
import test_fractparser
import test_symbol
import test_translate
import test_canon
import test_codegen
import test_fc
import test_fract4d
import test_colormap
import test_parfile
import test_fractal
import test_3d
import test_gradient
import test_preprocessor

def suite():
    return unittest.TestSuite((
    test_fractlexer.suite(),
    test_fractparser.suite(),
    test_symbol.suite(),
    test_translate.suite(),
    test_canon.suite(),
    test_codegen.suite(),
    test_fc.suite(),
    test_fract4d.suite(),
    test_colormap.suite(),
    test_parfile.suite(),
    test_fractal.suite(),
    test_3d.suite(),
    test_gradient.suite(),
    test_preprocessor.suite()))

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()

