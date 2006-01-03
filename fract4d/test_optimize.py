#!/usr/bin/env python

# test graph

import unittest
import copy
import stdlib

from instructions import *
import optimize

class Test(unittest.TestCase):
    def setUp(self):
        self.o = optimize.T()
        self.a = TempArg("a")
        self.b = TempArg("b")
        self.c = TempArg("c")
        
    def tearDown(self):
        pass

    def testFlowGraph(self):
        insns = [
            Move(ConstFloatArg(1.0),self.a),
            Move(ConstFloatArg(2.0),self.b),
            Binop("*", [self.a, self.b], [self.c])
            ]

        g = optimize.FlowGraph()
        g.build(insns)

        self.assertEqual(g.define[0], [self.a])
        self.assertEqual(g.define[1], [self.b])
        self.assertEqual(g.define[2], [self.c])
        self.assertEqual(g.use[2], [self.a, self.b])
        
    def testPeephole(self):
        tests = [
            # can't be optimized
            (Binop("*", [ ConstFloatArg(2.0), TempArg("a")], [TempArg("b")]),None),
            (Binop("*", [ TempArg("a"), ConstFloatArg(2.0)], [TempArg("b")]),None),
            (Binop("*", [ TempArg("a"), TempArg("b")], [TempArg("c")]),None),

            # constant folding
            (Binop("*", [ ConstFloatArg(2.0), ConstFloatArg(2.0)], [TempArg("b")]),
             Move(ConstFloatArg(4.0), TempArg("b"))),
            (Binop("-", [ ConstFloatArg(12.0), ConstFloatArg(14.0)], [TempArg("b")]),
             Move(ConstFloatArg(-2.0), TempArg("b"))),
            (Binop("+", [ ConstFloatArg(3.0), ConstFloatArg(2.0)], [TempArg("b")]),
             Move(ConstFloatArg(5.0), TempArg("b"))),
            (Binop("/", [ ConstFloatArg(2.0), ConstFloatArg(0.2)], [TempArg("b")]),
             Move(ConstFloatArg(10.0), TempArg("b"))),

            # multiplication by 1
            (Binop("*", [ ConstFloatArg(1.0), TempArg("a")], [TempArg("c")]),
             Move(TempArg("a"), TempArg("c"))),
            (Binop("*", [ TempArg("a"), ConstFloatArg(1.0)], [TempArg("c")]),
             Move(TempArg("a"), TempArg("c"))),

            # multiplication by 0
            (Binop("*", [ ConstFloatArg(0.0), TempArg("a")], [TempArg("c")]),
             Move(ConstFloatArg(0.0), TempArg("c"))),
            (Binop("*", [ TempArg("a"), ConstFloatArg(0.0)], [TempArg("c")]),
             Move(ConstFloatArg(0.0), TempArg("c")))
            
            ]

        (allin, allexp) = ([],[])
        for (input, expected) in tests:
            allin.append(input)
            if expected == None:
                expected = input
            allexp.append(expected)
            out = self.o.peephole_binop(input)
            self.assertEqual(str(out), str(expected))
            
        out = self.o.optimize(optimize.Peephole, allin)
        for (input, output, expected) in zip(allin, out, allexp):
            self.assertEqual(
                str(output), str(expected),
                "%s should produce %s, not %s" % (input, expected, output))
                
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

