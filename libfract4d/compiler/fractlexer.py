# ------------------------------------------------------------
# fractlexer.py
#
# tokenizer for UltraFractal formula files
# The lexer proper only applies to the *contents* of the {}
# fractal blocks - we use a top-level regex to split the
# file up into a set of formulae and parse them on demand.
# ------------------------------------------------------------
import lex
import sys
import re

# List of token names.   This is always required
tokens = (
   'NUMBER',
   'ID',

   'PLUS',
   'MINUS',
   
   'TIMES',
   'DIVIDE',
   'MOD', 
   
   'LPAREN', 
   'RPAREN', 
   'LARRAY',
   'RARRAY',
   'MAG', 
   'POWER',

   'BOOL_NEG',
   'BOOL_OR',
   'BOOL_AND',

   'EQ',
   'NEQ',
   'LT',
   'LTE',
   'GT',
   'GTE',

   'ASSIGN',

   'COMMENT',
   'NEWLINE',
   'ESCAPED_NL',
   'COLON',
   'COMMA',
   'STRING'
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'%'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
#t_LBRACE  = r'\{'
#t_RBRACE  = r'\}'
t_LARRAY  = r'\['
t_RARRAY  = r'\]'
t_MAG     = r'\|'
t_POWER   = r'\^'
t_BOOL_NEG= r'!'
t_BOOL_OR = r'\|\|'
t_BOOL_AND= r'&&'
t_EQ      = r'=='
t_NEQ     = r'!='
t_LT      = r'<'
t_LTE     = r'<='
t_GT      = r'>'
t_GTE     = r'>c='
t_ASSIGN  = r'='
t_COLON   = r':'
t_COMMA   = r','


def t_NUMBER(t):
    r'(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?'
    try:
        t.value = float(t.value) # FIXME: detect integers
    except ValueError:
        print "Line %d: Real number %s is too large!" % (t.lineno, t.value)
        t.value = 0
    return t
    
def t_ID(t):
    r'[@#]?[a-zA-Z_][a-zA-Z0-9]*'
    # look up ID
    return t

# don't produce tokens for newlines preceded by \
def t_ESCAPED_NL(t):
    r'\\\r?\n'
    t.lineno += 1

def t_COMMENT(t):
    r';[^\n]*'
    
def t_NEWLINE(t):
    r'\n'
    t.lineno += 1 # track line numbers
    return t

def t_STRING(t):
    r'\"[^\"]*"' # embedded quotes not supported in UF?
    t.value = re.sub(r'\\\r?\n[ \t\v]*',"",t.value) # hide \-split lines
    return t
    
# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t\r'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.skip(1)

# debugging
if __name__ == '__main__':
    # Build the lexer
    lex.lex()

    # Test it out
    data = open(sys.argv[1],"r").read()

    formulaFinder = re.compile(
        r'([^\{\(\)\}\r\n]+)\s*(\([\w]+\))?\s*\{([^\}]+)\}', re.DOTALL)
    formulae = re.findall(formulaFinder,data)
    for formula in formulae:
        # should be a 3-item tuple: name symmetry body
        print formula[0]
        if formula[1] <> "":
           print "symmetry:", formula[1]
        
        # Give the lexer some input
        lex.input(formula[2])

        # Tokenize
        while 1:
            tok = lex.token()
            if not tok: break      # No more input
            print tok
