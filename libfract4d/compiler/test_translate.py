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

    def translate(self,s,dump=None):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        #print pt.pretty()
        return translate.T(pt.children[0], dump)

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
        #for stm in t2.sections["c_loop"]: print stm.pretty()
        
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
        self.assertEqual(len(t3.warnings),8,t3.warnings)

    def testBailout(self):
        # empty bailout
        t = self.translate('''t_bail_1 {
        bailout:
        }''')

        self.assertWarning(t, "No bailout expression found" )
        self.assertNoErrors(t)

        # uncastable bailout
        t = self.translate('''t_bail_2 {
        bailout:
        if 1 > 2
        endif
        }''')

        self.assertError(t, "invalid type none")
        
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

        self.assertFuncOnList(lambda x,y : x.__class__.__name__ == y,
                              [x for x in plus],
                              ["Move","Name","Cast","Binop","Var","Cast","Var"])


    def testIf(self):
        t = self.translate('''t_if_1 {
        loop:
        if a > b
        a = 2
        else
        a = 3
        endif
        }''', {"dumpBlocks":1})

        self.assertNoErrors(t)
        ifseq = t.sections["loop"].children[0]

        self.failUnless(ifseq.children[0].op == ">" and \
                        ifseq.children[0].trueDest == "label0" and \
                        ifseq.children[0].falseDest == "label1")

        self.failUnless(ifseq.children[1].children[0].name == "label0" and \
                        ifseq.children[1].children[-1].dest == "label2" and \
                        ifseq.children[2].children[0].name == "label1" and \
                        ifseq.children[3].name == "label2")

        t = self.translate('''t_if_2 {
        loop:
        if a
        a = 2
        endif
        }''')

        self.assertNoErrors(t)
        ifseq = t.sections["loop"].children[0]
        self.failUnless(ifseq.children[0].op == "!=")
        
        self.failUnless(ifseq.children[1].children[0].name == "label0" and \
                        ifseq.children[1].children[-1].dest == "label2" and \
                        ifseq.children[2].children[0].name == "label1" and \
                        ifseq.children[3].name == "label2")

        self.failUnless(len(ifseq.children[2].children)==1)

        expectedLabs = ['CJ:label0,label1', 'L:label0', 'J:label2', 'L:label1', 'CJ:label3,label4', 'L:label3', 'J:label5', 'L:label4', 'L:label5', 'L:label2']

        t = self.translate('''t_if_3 {
        loop:
        if a == 1
           a = 2
        elseif a == 2
           a = 3
        else
           a = 4
        endif
        }''')

        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["loop"])
        self.assertJumpsAndLabs(t, expectedLabs)

        t = self.translate('''t_if_4 {
        loop:
        if a == 1
        else
           if a == 2
              a = 4
           endif
        endif
        }''')

        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["loop"])
        self.assertJumpsAndLabs(t, expectedLabs)

    def testBooleans(self):
        t = self.translate('''t_bool_0 {
        init:
        a == 1 && b == 2
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])

        t = self.translate('''t_bool_1 {
        init:
        a == 1 || b == 2
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])
        
        t = self.translate('''t_bool_2 {
        init:
        if a == 1 && b == 2
           a = 2
        endif
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])

        t = self.translate('''t_bool_3 {
        init:
        if a == 1 || b == 2
           a = 2
        endif
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])
        
    def testMandel(self):
        t = self.translate('''t_mandel_1 {
        loop:
        z = z * z + c
        bailout:
        |z| < 4.0
        }''')

        self.assertNoErrors(t)

        t = self.translate('''t_mandel_2 {
        : z = z * z + c, |z| < 4.0
        }''')

        self.assertNoErrors(t)
                    
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
        self.assertNoErrors(t1)
        
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
        for (name, item) in t.sections.items():
            if name[0:2] == "c_":
                for stm in item:
                    self.assertESeqsNotNested(stm,1)
                self.assertValidTrace(item)

    def assertValidTrace(self,trace):
        # must have each cjump followed by false case
        expecting = None
        for stm in trace:
            if expecting != None:
                self.failUnless(isinstance(stm,ir.Label))
                self.assertEqual(stm.name,expecting)
                expecting = None
            elif isinstance(stm, ir.CJump):
                expecting = stm.falseDest

    def assertNoProbs(self, t):
        self.assertEqual(len(t.warnings),0,
                         "Unexpected warnings %s" % t.warnings)
        self.assertNoErrors(t)
        
    def assertVar(self,t, name,type):
        self.assertEquals(t.symbols[name].type,type)

    def assertNode(self,name,n):
        self.failUnless(isinstance(n,ir.T), ("%s(%s) is not a node" % (n, name)))
        
    def assertTreesEqual(self, name, t1, t2):
        if name[0:2] == "c_":
            # canonicalized trees are a list, not a Seq()
            for (s1,s2) in zip(t1,t2):
                self.assertNode(name,s1)
                self.assertNode(name,s2)
                self.failUnless(
                    s1.pretty() == s2.pretty(),
                    ("%s, %s should be equivalent (section %s)" %
                     (s1.pretty(), s2.pretty(), name)))
        else:
            self.assertNode(name,t1)
            self.assertNode(name,t2)

            self.failUnless(
                t1.pretty() == t2.pretty(),
                ("%s, %s should be equivalent" % (t1.pretty(), t2.pretty())))

    def assertEquivalentTranslations(self,t1,t2):
        for (k,item) in t1.sections.items():
            self.assertTreesEqual(k,item,t2.sections[k])
        for (k,item) in t2.sections.items():
            self.assertTreesEqual(k,t1.sections[k], item)

    def assertFuncOnList(self,f,nodes,types):
        self.assertEqual(len(nodes),len(types))
        for (n,t) in zip(nodes,types):
            self.failUnless(f(n,t))

    def assertESeqsNotNested(self,t,parentAllowsESeq):
        'check that no ESeqs are left below other nodes'
        if isinstance(t,ir.ESeq):
            if parentAllowsESeq:
                for child in t.children:
                    self.assertESeqsNotNested(child,0)
            else:
                self.fail("tree not well-formed after linearize: %s" % t.pretty())
        else:
            for child in t.children:
                self.assertESeqsNotNested(child,0)

    def assertJumpsAndLabs(self,t,expected):
        jumps_and_labs = []
        for n in t.sections["loop"].children[0]:
            if isinstance(n,ir.Jump):
                jumps_and_labs.append("J:%s" % n.dest)
            elif isinstance(n,ir.CJump):
                jumps_and_labs.append("CJ:%s,%s" % (n.trueDest, n.falseDest))
            elif isinstance(n,ir.Label):                
                jumps_and_labs.append("L:%s" % n.name)

        self.assertEqual(jumps_and_labs, expected)

    def assertJumpsMatchLabs(self,t):
        'check that each jump has a corresponding label somewhere'
        jumpTargets = {}
        jumpLabels = {}
        for n in t:
            if isinstance(n,ir.Jump):
                jumpTargets[n.dest] = 1
            elif isinstance(n,ir.CJump):
                jumpTargets[n.trueDest] = jumpTargets[n.falseDest] = 1
            elif isinstance(n,ir.Label):                
                jumpLabels[n.name] = 1

        for target in jumpTargets.keys():
            self.failUnless(jumpLabels.has_key(target),
                            "jump to unknown target %s" % target )

def suite():
    return unittest.makeSuite(TranslateTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

