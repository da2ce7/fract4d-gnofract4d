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

    def testErrorAfterFormula(self):
        tree = self.parse("t1{\n}\ngibberish")
        self.failUnless(absyn.CheckTree(tree))
            
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

        t1 = self.parse(self.makeMinimalFormula('''
        IF x==1
        x=2
        eLSe
        x=3
        Endif'''))
        self.assertIsValidParse(t1)
        
    def testBadIfStatements(self):
        self.assertIsBadFormula(self.makeMinimalFormula("if = 7"),
                                "unexpected assign '='", 3)
        self.assertIsBadFormula(self.makeMinimalFormula("if x == 2\n1+1"),
                                "unexpected form_end '}'", 5)
        self.assertIsBadFormula(self.makeMinimalFormula("endif"),
                                "unexpected endif 'endif'",3)

    def testDecls(self):
        t1 = self.parse(self.makeMinimalFormula(
        '''bool a
        bool b = true
        bool c=false
        int d
        int e= 2
        float f
        float g = 2.0
        complex h
        complex i = 3 + 1i + i
        complex j = (2,3)
        color k'''))
        self.assertIsValidParse(t1)
        i = t1.children[0].children[0]
        for node in i.children:
            self.assertEqual(node.type, "decl")
        complex_decl = [n for n in i.children[8]]
        self.assertListTypesMatch(
            complex_decl,
            ["decl","binop","binop","const","complex","const","const","id"])

    def testArrays(self):
        # arrays aren't supported yet - make sure errors are nice
        self.assertIsBadFormula(self.makeMinimalFormula("float array[10]"),
                                "arrays are not supported",3)
        
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
        self.assertIsBadFormula(self.makeMinimalFormula('"'),
                                "unexpected '\"'",3)
    def testParamBlocks(self):
        t1 = self.parse('''
        t1 {
        default:
        complex param x
        title = "fish"
        default=(0.0,0)
        endparam
        param y
        enum = "foo" "bar"
        endparam
        }
        ''')
        self.assertIsValidParse(t1)

    def testFuncBlocks(self):
        t1 = self.parse('''
        t1 {
        default:
        func fn1
           caption = "fn1"
           default = cabs()
        endfunc
        }
        ''')
        self.assertIsValidParse(t1)

    def testHeading(self):
        t1 = self.parse('''
        t1{
        default:
        heading
         caption = "fish face heading"
        endheading
        }
        ''')
        self.assertIsValidParse(t1)
        
    def testRepeat(self):
        t1 = self.parse(self.makeMinimalFormula(
        '''repeat
        z = z ^ 2
        until |z| > 2000.0
        '''))
        self.assertIsValidParse(t1)

    def testWhile(self):
        t1 = self.parse(self.makeMinimalFormula(
        '''while 1 > 0
             z = z + 2
             while x > y
               foo = bar
             endwhile
           endwhile
           '''))
        self.assertIsValidParse(t1)
        ns = [n for n in t1.children[0].children[0].children[0]]
            
        self.assertListTypesMatch(
            [n for n in t1.children[0].children[0].children[0]],
            ["while", "binop", "const", "const",
             "stmlist",
                 "assign", "binop", "id", "const",
                 "while", "binop", "id", "id",
                 "stmlist",
                     "assign", "id"              
            ])

    # this comes from anon.ufm, which appears broken -UF doesn't
    # parse it either
    def testTrailingExpressions(self):
        f = '''
TZ0509-03 {
;
;from TieraZon2 fl-05-09.fll
init:
  z = -(3 * #pixel) / 5
loop:
  z = z - (z * z^4 + z^4 * #pixel - sin(z) - z) / (5 * z^4 + 4 * z^3 *
#pixel -
cos(z) - z)
bailout:
  |z| < 4
}
'''
        self.assertIsBadFormula(f,"unexpected newline",8)

    def testSections(self):
        t1 = self.parse('''t1{
        Init:
        loop:
        :
        bailout:
        Transform:
        final:
        global:
        switch:
        DEFAULT:
        builtin:
        }
        ''')
        self.assertIsValidParse(t1)
        #print t1.pretty()
        self.assertListTypesMatch(
            t1.children[0].children,
            ["stmlist"]*7 + ["setlist"] * 3)

        # test we work with old-style fractint sections
        t2 = self.parse('''InvMandel (XAXIS) {; Mark Peterson
  c = z = 1 / pixel:
   z = sqr(z) + c
    |z| <= 4
  }
  ''')
        #print t2.pretty()
        
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

    def testComma(self):
        self.assertParsesEqual("a=1,b=2","a=1\nb=2")
        
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


    def assertListTypesMatch(self,nodes,types):
        self.assertEqual(len(nodes),len(types))
        for (n,t) in zip(nodes,types):
            self.assertEqual(n.type,t)
        
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
        self.failUnless(
            t1.DeepCmp(t2)==0,
            ("%s, %s should be equivalent" % (t1.pretty(), t2.pretty())))

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

        
