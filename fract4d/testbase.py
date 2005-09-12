#!/usr/bin/env python

# a base class other test classes inherit from - some shared functionality

import unittest
import string
import types

import ir
import fracttypes

class TestBase(unittest.TestCase):
    def assertNearlyEqual(self,a,b,epsilon=1.0e-12):
        # check that each element is within epsilon of expected value
        for (ra,rb) in zip(a,b):
            if isinstance(ra, types.ListType) or isinstance(ra, types.TupleType):
                for (ca,cb) in zip(ra,rb):
                    d = abs(ca-cb)
                    self.failUnless(d < epsilon, "%s - %s = %s, > %s" % (ca,cb,d,epsilon))
            else:
                d = abs(ra-rb)
                self.failUnless(d < epsilon, "%s - %s = %s, > %s" % (ra,rb,d,epsilon))

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

    def assertNoErrors(self,t, info=""):
        self.assertEqual(len(t.errors),0,
                         "Unexpected errors %s in %s" % (t.errors, info))
        for (name, item) in t.canon_sections.items():
            for stm in item:
                #print stm.pretty()
                self.assertESeqsNotNested(stm,1)
            self.assertValidTrace(item)
        self.assertWellTyped(t)
        
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
        if isinstance(t1,types.ListType):
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
                self.fail("tree not well-formed after linearize")
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

    def assertBlocksAreWellFormed(self,blocks):
        for b in blocks:
            self.assertBlockIsWellFormed(b)

    def assertBlockIsWellFormed(self,block,startLabel=None, endLabel=None):
        self.assertStartsWithLabel(block,startLabel)
        self.assertEndsWithJump(block,endLabel)
        for stm in block[1:-1]:
            if isinstance(stm,ir.Jump) or \
                   isinstance(stm,ir.CJump) or \
                   isinstance(stm,ir.Label):
                self.fail("%s not allowed mid-basic-block", stm.pretty())
    

    def assertStartsWithLabel(self, block, name=None):
        self.failUnless(isinstance(block[0], ir.Label))
        if name != None:
            self.assertEqual(block[0].name, name)

    def assertEndsWithJump(self,block, name=None):
        self.failUnless(isinstance(block[-1], ir.Jump) or \
                        isinstance(block[-1], ir.CJump))
        if name != None:
            self.assertEqual(block[-1].dest, name)

    def assertWellTyped(self,t):
        for (key,s) in t.sections.items():
            for node in s:
                if isinstance(node,ir.T):
                    ob = node
                    dt = node.datatype
                elif isinstance(node,types.StringType):
                    try:
                        sym = t.symbols[node]
                    except KeyError, err:
                        self.fail("%s not a symbol in %s" % (node, s.pretty()))
                    self.failUnless(isinstance(sym,fracttypes.Var),
                                    "weird symbol %s : %s(%s)" %
                                    (node, sym, sym.__class__.__name__))
                    ob = sym
                    dt = ob.type
                else:
                    self.fail("%s(%s) not an ir Node" % (node, node.__class__.__name__))

                if isinstance(ob,ir.Stm):
                    self.assertEqual(dt,None,"bad type %s for %s" % (dt, ob))
                else:
                    self.failUnless(dt in fracttypes.typeList,
                                    "bad type %s for %s" % (dt, ob))
