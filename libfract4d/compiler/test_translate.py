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
        t1 = self.translate("t1 {\na=1:b=2,c=3}")
        t2 = self.translate('''
             t1 {
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
             t1 {
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
        t1 = self.translate("t1 {\nglobal:int a\ncomplex b\n}")
        self.assertVar(t1, "a", fracttypes.Int)
        self.assertVar(t1, "b", fracttypes.Complex)
        self.assertNoProbs(t1)
        
    def testBadDecls(self):
        t1 = self.translate("t1 {\nglobal:int z\n}")
        self.assertError(t1,"existing symbol z")
        t1 = self.translate("t1 {\nglobal:int a\nfloat A\n}")
        self.assertError(t1,"existing symbol A")
        
    def assertError(self,t,str):
        self.assertNotEqual(len(t.errors),0)
        for e in t.errors:
            if string.find(e,str):
                return
        self.fail(("No error matching %s raised" % str))
        
    def assertNoProbs(self, t):
        self.assertEqual(len(t.warnings),0)
        self.assertEqual(len(t.errors),0)
        
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

