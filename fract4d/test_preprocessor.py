#!/usr/bin/env python

import unittest
import preprocessor

class Test(unittest.TestCase):
    def testEmpty(self):
        pp = preprocessor.T('')

    def testIfdef(self):
        pp = preprocessor.T('''
        $IFDEF wibble
        >>><<<
        $ENDIF
        wobble
        ''')

        self.assertEqual(pp.out(), '''
        wobble
        ''')

    def testIfWithoutEndif(self):
        try:
            pp = preprocessor.T('''
            $IFDEF foople
            ''')
            self.fail("Should have raised an exception")
        except preprocessor.Error, err:
            self.assertEqual(str(err), "2: $IFDEF without $ENDIF")

    def testEndifWithoutIf(self):
        try:
            pp = preprocessor.T('''
            $IFDEF foogle

            $IFDEF bargle
            $ENDIF
            $ENDIF
            $ENDIF
            ''')
            self.fail("Should have raised an exception")
        except preprocessor.Error, err:
            self.assertEqual(str(err), "7: $ENDIF without $IFDEF")

    def testIfdefWithoutVar(self):
        try:
            pp = preprocessor.T('''
            $IFDEF
            foo
            $ENDIF
            ''')
            self.fail("Should have raised an exception")
        except preprocessor.Error, err:
            self.assertEqual(str(err), "2: $IFDEF without variable")

    def testDefine(self):
        pp = preprocessor.T('$define foo\nbar')

        self.assertEqual(pp.out(), "bar")

    def testDefineWithoutVar(self):
        try:
            pp = preprocessor.T('$define !!!\n')
            self.fail("Should have raised an exception")
        except preprocessor.Error, err:
            self.assertEqual(str(err), "1: $DEFINE without variable")

    def testDefineWorks(self):
        pp = preprocessor.T('''
        $define wibble
        $IFDEF wibble
        >>><<<
        $ENDIF
        wobble
        ''')

        self.assertEqual(pp.out(), '''
        >>><<<
        wobble
        ''')

    def testNestedIfdef(self):
        pp = preprocessor.T('''
        $define bar
        $IFDEF foo
           foo
           $IFDEF bar
           foobar
           $ENDIF
        $ENDIF
        $IFDEF bar
           bar
           $IFDEF foo
           barfoo
           $ENDIF
        $ENDIF
        ''')

        self.assertEqual(pp.out(), '''
           bar
        ''')
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

        
