import unittest
import fractlexer

class LexerTest(unittest.TestCase):
    def setUp(self):
        self.lexer = fractlexer.lexer
        self.lexer.lineno = 1
        
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
            #print tok
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
   title = "foo;bar\\
   baz"
}
''')
        self.failUnless(tokens[0].type == tokens[1].type == "NEWLINE","first 2 should be newlines")

        str = [ tok for tok in tokens if tok.type == "STRING"]
        self.failUnless(len(str) == 1 and str[0].value == "foo;barbaz", "string literal parsing problem" and str[0].lineno == 14)

        sections = [ tok for tok in tokens if tok.type == "SECT_STM"]
        self.assertEqual(len(sections),3, "wrong number of sections")
        self.assertEqual(sections[0].lineno, 4, "line counting wrong")
        self.assertEqual(sections[2].lineno, 10, "line counting wrong")

    def testBadChars(self):
        tokens = self.tokensFromString("$ hello ~\n ` ' goodbye")
        self.failUnless(tokens[0].type == "error" and tokens[0].value == "$")
        self.failUnless(tokens[4].type == "error" and
                        tokens[4].value == "`" and
                        tokens[4].lineno == 2)

    def testFormIDs(self):
        tokens = self.tokensFromString('''
=05 { }
0008 { }
-fred- { }
''')
        for token in tokens:
            self.failUnless(token.type == "FORM_ID" or
                            token.type == "FORM_END" or
                            token.type == "NEWLINE")

    def testCommentFormula(self):
        tokens = self.tokensFromString('''
;Comment {

@#$%554""}
myComment {}
''')
        tokens = filter(lambda tok : tok.type != "NEWLINE", tokens)
        self.failUnless(tokens[0].type == "FORM_ID" and
                        tokens[0].value == "myComment" and
                        tokens[0].lineno == 5)

    def testKeywords(self):
        ts = self.tokensFromString('if a elseif b else c')
        self.failUnless(ts[0].type == "IF" and
                        ts[2].type == "ELSEIF" and
                        ts[4].type == "ELSE" and
                        ts[1].type == ts[3].type == ts[5].type == "ID")
def suite():
    return unittest.makeSuite(LexerTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
