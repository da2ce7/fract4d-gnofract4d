import unittest
import fractparser
import absyn
import re
import fractlexer

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = fractparser.parser
        fractlexer.lexer.lineno = 1
        #self.parser.lexer.lineno = 1

    def tearDown(self):
        self.parser.restart()
        
    def testEmpty(self):
        tree = self.parser.parse("\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()

    def testEmptyFormula(self):
        tree = self.parser.parse("t1 {\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        formula = tree.children[0]
        self.failUnless(formula.type == "formula" and formula.leaf == "t1")
        #print tree.pretty()

    def testErrorThenFormula(self):
        tree = self.parser.parse("gibberish~\nt1 {\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()
        formula = tree.children[0]
        self.failUnless(formula.type == "formula" and formula.leaf == "t1")

    def testErrorInFormula(self):
        tree = self.parser.parse("t1 {\n ~\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()
        formula = tree.children[0]
        self.failUnless(formula.type == "formula")
        err = formula.children[0]
        self.failUnless(err.type == "error")
        self.assertNotEqual(re.search("line 2",err.leaf),None,
                            "bad error mesage line number") 

    def testPrecedence(self):
        tree = self.parser.parse('''t2 {
init:
x = 2 * 3 + 1 ^ -7 / 2 - |4 - 1|
}
''')
        explicit_tree = self.parser.parse('''t2 {
init:
x = ((2 * 3) + ((1 ^ -7) / 2)) - | 4 - 1|
}
''')
        self.assertTreesEqual(tree, explicit_tree)

    def testBooleanPrecedence(self):
        tree = self.parser.parse('''t2 {
init:
2 * 3 > 1 + 1 && x + 1 <= 4.0 || !d >= 2.0
}
''')
        explicit_tree = self.parser.parse('''t2 {
init:
(((2 * 3) > (1 + 1)) && ((x + 1) <= 4.0)) || ((!d) >= 2.0)
}
''')
        self.assertTreesEqual(tree,explicit_tree)
        
    def assertTreesEqual(self, t1, t2):
        # linearize both trees and check that they're equivalent
        eqs = [ (x.leaf == y.leaf and x.type == y.type) for (x,y) in zip(t1, t2) ]
        # are any nodes not equal?
        self.assertEqual(eqs.count(0),0, "should be no false matches")


def suite():
    return unittest.makeSuite(ParserTest,'test')

if __name__ == '__main__':
    unittest.main()

        
