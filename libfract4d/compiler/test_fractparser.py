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
                            "bad error message line number") 

    def testErrorBeforeAndInFormula(self):
        tree = self.parse("gibberish\nt1 {\n ~\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()
        formula = tree.children[0]
        self.failUnless(formula.type == "formula")
        err = formula.children[0]
        self.failUnless(err.type == "error")
        self.assertNotEqual(re.search("line 3",err.leaf),None,
                            "bad error message line number") 
        
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

    def testIfStatement(self):
        t1 = self.parse(self.makeMinimalFormula("if x==1\nx=2\nendif"))
        self.assertIsValidParse(t1)
        
        t1 = self.parse(self.makeMinimalFormula('''
        if x==1
        x=2
        else
        x=3
        endif'''))
        self.assertIsValidParse(t1)
        
        t1 = self.parse(self.makeMinimalFormula('''
        if x==1
        x=2
        elseif (x==2) && (y==7)
        x=3
        y=5
        endif'''))
        self.assertIsValidParse(t1)
        
        t1 = self.parse(self.makeMinimalFormula('''
        if x == 2
        endif'''))
        self.assertIsValidParse(t1)                        

        t1 = self.parse(self.makeMinimalFormula('''
        if x == 2
        if y == 4
           z = 17
        elseif p != q
           w = 4
        else
           v=#pixel
        endif
        elseif 4 + 6
        else
        endif'''))
        #print t1.pretty()
        self.assertIsValidParse(t1)                        

    def testBadIfStatements(self):
        self.assertIsBadFormula(self.makeMinimalFormula("if = 7"),
                                "unexpected assign '='", 3)
        self.assertIsBadFormula(self.makeMinimalFormula("if x == 2\n1+1"),
                                "unexpected form_end '}'", 5)
        self.assertIsBadFormula(self.makeMinimalFormula("endif"),
                                "unexpected endif 'endif'",3)

    def testDecls(self):
        t1 = self.parse(self.makeMinimalFormula('''
        bool a
        bool b = true
        bool c=false
        int d
        int e= 2
        float f
        float g = 2.0
        complex h
        complex i = (2,3)
        color j'''))
        #print t1.pretty()
        self.assertIsValidParse(t1)

    def testStrings(self):
        t1 = self.parse('''
        t1 {
        default:
        x = ""
        y = "hi"
        z = "hello" "world" "long list"
        }
        ''')
        self.assertIsValidParse(t1)
        self.assertEqual(len(self.allNodesOfType(t1,"string")),5)
        
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
        self.assertIsBadFormula(self.makeMinimalFormula("2 + 3 +"),
                                 "unexpected newline",3)
        self.assertIsBadFormula(self.makeMinimalFormula("3 4"),
                                 "unexpected number '4.0'",3)

        # not a great error message...
        self.assertIsBadFormula(self.makeMinimalFormula("("),
                                "unexpected newline",3)
        
        # not currently an error, because we think Init is part of
        # a fractint-style implicit-init section
        #self.assertIsBadFormula("t1 {\nInit:\nx\n}\n",
        #                        "unknown section name 'Init'",2)

        
    def assertIsBadFormula(self,s,message,line):
        t1 = self.parse(s)
        #print t1.pretty()
        self.failUnless(absyn.CheckTree(t1), "invalid tree created")
        formula = t1.children[0]
        self.failUnless(formula.type == "formula")
        err = formula.children[0]
        self.failUnless(err.type == "error", "error not found")
        #print err.leaf
        self.assertNotEqual(re.search(message,err.leaf),None,
                            ("bad error message text '%s'", err.leaf))
        self.assertNotEqual(re.search(("line %s" % line),err.leaf),None,
                            ("bad error message line number in '%s'", err.leaf)) 
        
    def assertIsValidParse(self,t1):
        self.failUnless(absyn.CheckTree(t1))
        errors = self.allNodesOfType(t1,"error")
        for e in errors: print "%s" % e
        self.assertEqual(errors,[])
        
    def assertParsesEqual(self, s1, s2):
        t1 = self.parse(self.makeMinimalFormula(s1))
        t2 = self.parse(self.makeMinimalFormula(s2))
        self.assertTreesEqual(t1,t2)
        
    def assertTreesEqual(self, t1, t2):
        self.failUnless(t1.DeepCmp(t2)==0, "should be equivalent")

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

        
