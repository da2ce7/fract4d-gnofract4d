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
        self.assertParsesEqual(
            "x = 2 * 3 + 1 ^ -7 / 2 - |4 - 1|",
            "x = ((2 * 3) + ((1 ^ (-7)) / 2)) - | 4 - 1|")

    def testBooleanPrecedence(self):
        self.assertParsesEqual(
            "2 * 3 > 1 + 1 && x + 1 <= 4.0 || !d >= 2.0",
            "(((2 * 3) > (1 + 1)) && ((x + 1) <= 4.0)) || ((!d) >= 2.0)")

    def testAssociativity(self):
        self.assertParsesEqual(
            "a = b = c",
            "a = (b = c)")
        self.assertParsesEqual(
            "a + b + c - d - e",
            "(((a+b)+c)-d)-e")

    def testSimpleMandelbrot(self):
        t1 = self.parser.parse('''
MyMandelbrot {
init:
    z = 0
loop:
    z = z * z + #pixel
bailout:
    |z| < 4
default:
    title = "My Mandelbrot"
}
''')
        self.assertIsValidParse(t1)

    def assertIsValidParse(self,t1):
        self.failUnless(absyn.CheckTree(t1))
        errors = [ x for x in t1 if x.type == "error"]
        self.assertEqual(errors,[])
        
    def assertParsesEqual(self, s1, s2):
        t1 = self.parser.parse(self.makeMinimalFormula(s1))
        t2 = self.parser.parse(self.makeMinimalFormula(s2))
        self.assertTreesEqual(t1,t2)
        
    def assertTreesEqual(self, t1, t2):
        # linearize both trees and check that they're equivalent
        eqs = [ (x.leaf == y.leaf and x.type == y.type) for (x,y) in zip(t1, t2) ]
        # are any nodes not equal?
        self.assertEqual(eqs.count(0),0, "should be no false matches")

    # shorthand for minimal formula defn containing exp
    def makeMinimalFormula(self,exp):
        return '''t2 {
init:
%s
}
''' % exp
    
def suite():
    return unittest.makeSuite(ParserTest,'test')

if __name__ == '__main__':
    unittest.main()

        
