#!/usr/bin/env python

# test harness for translate module

import translate
import fractparser
import fractlexer
import fracttypes
import ir

import string
import unittest

class TranslateTest(unittest.TestCase):
    def setUp(self):
        self.parser = fractparser.parser

    def tearDown(self):
        pass

    def translate(self,s):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        #print pt.pretty()
        return translate.T(pt.children[0])

    def testFractintSections(self):
        t1 = self.translate("t1 {\na=1,a=2:\nb=2\nc=3}")
        t2 = self.translate('''
             t2 {
                 init: 
                 a=1
                 a=2
                 loop:
                 b=2
                 bailout:
                 c=3
                 }''')
        self.assertEquivalentTranslations(t1,t2)
        self.assertNoErrors(t1)
        self.assertNoErrors(t2)

        t3 = self.translate('''
             t3 {
                 a=1:b=2,c=3
                 init:
                 a=1,a=2
                 loop:
                 b=2
                 bailout:
                 c=3
                 }''')
        self.assertEquivalentTranslations(t1,t3)
        self.assertEqual(len(t3.warnings),7,t3.warnings)

    def testAssign(self):
        # correct declarations
        t9 = self.translate('''t9 {
        init:
        int i
        float f
        complex c
        loop:
        i = 1
        f = 1.0
        }''')
        self.assertNoProbs(t9)

        # basic warnings and errors
        t10 = self.translate('''t10 {
        init: int i, float f, complex c
        loop:
        f = 1 ; upcast - warning
        i = 1.0 ; downcast - error
        }''')
        self.assertWarning(t10,"conversion from int to float on line 4")
        self.assertError(t10, "invalid type float for 1.0 on line 5, expecting int")

    def testIDs(self):
        t11 = self.translate('''t11 {
        init: int a = 1, int b = 2
        loop: a = b
        }''')
        self.assertNoProbs(t11)

        t12 = self.translate('t12 {\ninit: a = b}')
        self.assertWarning(t12, "Uninitialized variable b referenced on line 2")

    def testBinops(self):
        # simple ops with no coercions
        t13 = self.translate('''t13 {
        loop:
        complex a, complex b, complex c
        int ia, int ib, int ic
        a = b + c
        ia = ib + ic
        }''')
        
        #print t13.sections["loop"].pretty()
        self.assertNoProbs(t13)
        result = t13.sections["loop"]
        self.failUnless(isinstance(result.children[-1],ir.Move))
        # some coercions
        t = self.translate('''t_binop_2 {
        loop:
        complex a, complex b, complex c
        int ia, int ib, int ic
        float fa, float fb, float fc
        a = fa + ia
        fb = ib / ic
        }''')
        self.assertNoErrors(t)
        (plus,div) = t.sections["loop"].children[-2:]

        self.assertEqual(div.children[1].datatype, fracttypes.Float)
        self.assertEqual(div.children[1].children[0].children[0].datatype,
                         fracttypes.Int)
        
        print plus.pretty()
        
        
    def testDecls(self):
        t1 = self.translate("t4 {\nglobal:int a\ncomplex b\nbool c = true\n}")
        self.assertNoProbs(t1)
        self.assertVar(t1, "a", fracttypes.Int)
        self.assertVar(t1, "b", fracttypes.Complex)
        t1 = self.translate('''
        t5 {
        init:
        float a = true,complex c = 1.0
        complex x = 2
        }''')
        self.assertNoErrors(t1)
        self.assertVar(t1, "a", fracttypes.Float)
        self.assertVar(t1, "c", fracttypes.Complex)
        self.assertVar(t1, "x", fracttypes.Complex)
        self.assertWarning(t1, "conversion from bool to float on line 4")
        self.assertWarning(t1, "conversion from float to complex on line 4")
        self.assertWarning(t1, "conversion from int to complex on line 5")

    def testMultiDecls(self):
        t1 = self.translate("t6 {\ninit:int a = int b = 2}")
        self.assertVar(t1, "a", fracttypes.Int)
        self.assertVar(t1, "b", fracttypes.Int)
        
    def testBadDecls(self):
        t1 = self.translate("t7 {\nglobal:int z\n}")
        self.assertError(t1,"symbol 'z' is predefined")
        t1 = self.translate("t8 {\nglobal:int a\nfloat A\n}")
        self.assertError(t1,"'A' was already defined on line 2")
        
    def assertError(self,t,str):
        self.assertNotEqual(len(t.errors),0)
        for e in t.errors:
            if string.find(e,str) != -1:
                return
        self.fail(("No error matching '%s' raised, errors were %s" % (str, t.errors)))

    def assertWarning(self,t,str):
        self.assertNotEqual(len(t.warnings),0)
        for e in t.warnings:
            if string.find(e,str) != -1:
                return
        self.fail(("No warning matching '%s' raised, warnings were %s" % (str, t.warnings)))

    def assertNoErrors(self,t):
        self.assertEqual(len(t.errors),0,
                         "Unexpected errors %s" % t.errors)
        
    def assertNoProbs(self, t):
        self.assertEqual(len(t.warnings),0,
                         "Unexpected warnings %s" % t.warnings)
        self.assertNoErrors(t)
        
    def assertVar(self,t, name,type):
        self.assertEquals(t.symbols[name].type,type)

    def assertTreesEqual(self, t1, t2):
        self.failUnless(
            t1.pretty() == t2.pretty(),
            ("%s, %s should be equivalent" % (t1.pretty(), t2.pretty())))

    def assertEquivalentTranslations(self,t1,t2):
        for k in t1.sections.keys():
            self.assertTreesEqual(t1.sections[k],t2.sections[k])
        for k in t2.sections.keys():
            self.assertTreesEqual(t1.sections[k],t2.sections[k])
            
def suite():
    return unittest.makeSuite(TranslateTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

