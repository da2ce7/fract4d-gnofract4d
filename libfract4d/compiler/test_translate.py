#!/usr/bin/env python

# test harness for translate module

import translate
import unittest
import fractparser
import fractlexer
import fracttypes
import string

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
        t1 = self.translate("t1 {\na=1:\nb=2\nc=3}")
        t2 = self.translate('''
             t2 {
                 init: 
                 a=1
                 loop:
                 b=2
                 bailout:
                 c=3
                 }''')
        self.assertEquivalentTranslations(t1,t2)
        self.assertNoProbs(t1)
        self.assertNoProbs(t2)

        t3 = self.translate('''
             t3 {
                 a=1:b=2,c=3
                 init:
                 a=1
                 loop:
                 b=2
                 bailout:
                 c=3
                 }''')
        self.assertEquivalentTranslations(t1,t3)
        self.assertEqual(len(t3.warnings),3)

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
        
    def assertEquivalentTranslations(self,t1,t2):
        for k in t1.sections.keys():
            self.assertEqual(t1.sections[k],t2.sections[k])
        for k in t2.sections.keys():
            self.assertEqual(t1.sections[k],t2.sections[k])
            
def suite():
    return unittest.makeSuite(TranslateTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

