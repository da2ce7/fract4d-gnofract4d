import unittest
import fractparser
import absyn

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = fractparser.parser
        #self.parser.lexer.lineno = 1

    def tearDown(self):
        self.parser.restart()
        
    def testEmpty(self):
        tree = self.parser.parse("\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()

    def testFormula(self):
        tree = self.parser.parse("t1 {\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        formula = tree.children[0]
        self.failUnless(formula.type == "formula" and formula.leaf == "t1")
        #print tree.pretty()

    def testErrorThenFormula(self):
        tree = self.parser.parse("gibberish~\nt1 {\n}\n")
        self.failUnless(absyn.CheckTree(tree))
        #print tree.pretty()
        self.failUnless(formula.type == "formula" and formula.leaf == "t1")

        
def suite():
    return unittest.makeSuite(ParserTest,'test')

if __name__ == '__main__':
    unittest.main()

        
