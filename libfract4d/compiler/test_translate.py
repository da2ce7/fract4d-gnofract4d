#!/usr/bin/env python

# test harness for translate module

import translate
import unittest
import fractparser
import fractlexer

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
                            
    def assertEquivalentTranslations(self,t1,t2):
        for k in t1.sections.keys():
            self.assertEqual(t1.sections[k],t2.sections[k])
        for k in t2.sections.keys():
            self.assertEqual(t1.sections[k],t2.sections[k])
            
def suite():
    return unittest.makeSuite(TranslateTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

