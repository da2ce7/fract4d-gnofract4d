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

    def parse(self,s):
        fractlexer.lexer.lineno = 1
        return self.parser.parse(s)
    
    def tearDown(self):
        self.parser.restart()
        
    def testEmpty(self):
        tree = self.parse("\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()

    def testEmptyFormula(self):
        tree = self.parse("t1 {\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        formula = tree.children[0]
        self.failUnless(formula.type == "formula" and formula.leaf == "t1")
        #print tree.pretty()

    def testErrorThenFormula(self):
        tree = self.parse("gibberish~\nt1 {\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()
        formula = tree.children[0]
        self.failUnless(formula.type == "formula" and formula.leaf == "t1")

    def testErrorInFormula(self):
        tree = self.parse("t1 {\n ~\n}\n")
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
        self.assertParsesEqual(
            "a^b^c",
            "a^(b^c)")

    def testSimpleMandelbrot(self):
        t1 = self.parse('''
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

    def testParseErrors(self):
        self.assertIsBadFormula("t1 {\ninit:\n2 + 3 +\n}\n",
                                "unexpected newline",3)
        self.assertIsBadFormula("t1 {\ninit:\n3 4\n}\n",
                                "unexpected number '4.0'",3)
        
    def assertIsBadFormula(self,s,message,line):
        t1 = self.parse(s)
        self.failUnless(absyn.CheckTree(t1), "parse error not detected")
        formula = t1.children[0]
        self.failUnless(formula.type == "formula")
        err = formula.children[0]
        self.failUnless(err.type == "error")
        #print err.leaf
        self.assertNotEqual(re.search(message,err.leaf),None,
                            ("bad error message text '%s'", err.leaf))
        self.assertNotEqual(re.search(("line %s" % line),err.leaf),None,
                            ("bad error mesage line number in '%s'", err.leaf)) 
        
    def assertIsValidParse(self,t1):
        self.failUnless(absyn.CheckTree(t1))
        errors = self.allNodesOfType(t1,"error")
        self.assertEqual(errors,[])
        
    def assertParsesEqual(self, s1, s2):
        t1 = self.parse(self.makeMinimalFormula(s1))
        t2 = self.parse(self.makeMinimalFormula(s2))
        self.assertTreesEqual(t1,t2)
        
    def assertTreesEqual(self, t1, t2):
        self.assertEqual(t1,t2, "should be equivalent")

    def allNodesOfType(self, t1, type):
        return [ n for n in t1 if n.type == type]
        
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
    unittest.main(defaultTest='suite')

        
