import unittest
import fractlexer

class LexerTest(unittest.TestCase):
    def setUp(self):
        self.lexer = fractlexer.lexer

    # utility function - open file f, lex it, and return a list of
    # all the tokens therein
    
    def tokensFromFile(self, f):
        data = open(f,"r").read()
        return self.tokensFromString(self, data)

    def tokensFromString(self, data):
        # Give the lexer some input
        self.lexer.input(data)

        toklist = []
        # Tokenize
        while 1:
            tok = self.lexer.token()
            if not tok: break      # No more input
            toklist.append(tok)

        return toklist
    
    def testEmpty(self):
        self.assertEqual(self.tokensFromString(""),[])

    def testBasics(self):
        tokens = self.tokensFromString(
            '''; Formulas from Andre Vandergoten
; (2 + #hash foo ^|+| "hello" a coment containing expressions
AAA-5-grt{
init:
   z = #pixel
loop:
   if @soort ==  0
      z = z^@power/@een(#pixel)
   endif  
bailout:
   |z|>@bailout
default:
   title = "foo;bar\
   baz"
}
''')
        self.failUnless(tokens[0].type == tokens[1].type == "NEWLINE","first 2 should be newlines")
            
def suite():
    return unittest.makeSuite(LexerTest,'test')

if __name__ == '__main__':
    unittest.main()
