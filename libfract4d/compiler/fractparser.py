#!/usr/bin/env python
# Parser for UltraFractal + Fractint input files

import yacc
import fractlexer
import absyn

tokens = fractlexer.tokens

precedence = (
    ('left', 'COMMA'),
    ('right', 'ASSIGN'),
    ('left', 'BOOL_OR', 'BOOL_AND'),
    ('left', 'EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE','MOD'),
    ('right', 'BOOL_NEG', 'UMINUS', 'POWER')
)

def p_formula(t):
     'formula : FORM_ID NEWLINE sectlist FORM_END NEWLINE'
     t[0] = absyn.Formula(t[1],t[3])

def p_formula_2(t):
     'formula : FORM_ID NEWLINE stmlist sectlist FORM_END NEWLINE'
     sectlist = [ absyn.Stmlist("nameless",t[3]) ] + t[4]
     t[0] = absyn.Formula(t[1],sectlist)

def p_sectlist_2(t):
     'sectlist : section sectlist'
     t[0] = [ t[1] ] + t[2]

def p_sectlist_empty(t):
     'sectlist : empty'
     t[0] = [] # absyn.Empty() ]
     
def p_section_stm(t):
     'section : SECT_STM NEWLINE stmlist'
     t[0] = absyn.Stmlist(t[1],t[3])

def p_stmlist_stm(t):
    'stmlist : stm'
    t[0] = [ t[1] ]

def p_stmlist_2(t):
    'stmlist : stm NEWLINE stmlist'
    t[0] = [t[1]] + t[3]
    
def p_stm_exp(t):
    'stm : exp'
    t[0] = t[1]

def p_stm_empty(t):
    'stm : empty'
    t[0] = t[1]
    
def p_empty(t):
    'empty :'
    t[0] = absyn.Empty()
    
def p_stm_decl(t):
    'stm : ID ID'
    t[0] = absyn.Decl(t[1], t[2])

def p_stm_decl_assign(t):
    'stm : ID ID ASSIGN exp'
    t[0] = absyn.Decl(t[1],t[2],t[4])

def p_exp_binop(t):
    '''exp : exp PLUS exp
       exp : exp MINUS exp
       exp : exp TIMES exp
       exp : exp DIVIDE exp
       exp : exp MOD exp
       exp : exp POWER exp
       exp : exp BOOL_OR exp
       exp : exp BOOL_AND exp
       exp : exp EQ exp
       exp : exp NEQ exp
       exp : exp LT exp
       exp : exp LTE exp
       exp : exp GT exp
       exp : exp GTE exp
       '''
    t[0] = absyn.Binop(t[2],t[1],t[3])

def p_exp_assign(t):
    'exp : ID ASSIGN exp'
    t[0] = absyn.Assign(t[1],t[3])
    
# implement unary minus as 0 - n
def p_exp_uminus(t):
    'exp : MINUS exp %prec UMINUS'
    t[0] = absyn.Binop("-", absyn.Number(0),t[2])

def p_exp_mag(t):
    'exp : MAG exp MAG'
    t[0] = absyn.Mag(t[2])

def p_exp_neg(t):
    'exp : BOOL_NEG exp'
    t[0] = absyn.Neg(t[2])

def p_exp_num(t):
    'exp : NUMBER'
    t[0] = absyn.Number(t[1])

def p_exp_id(t):
    'exp : ID'
    t[0] = absyn.ID(t[1])

def p_exp_funcall(t):
    'exp : ID LPAREN arglist RPAREN'
    t[0] = absyn.Funcall(t[1],t[3])

def p_exp_funcall_noargs(t):
    'exp : ID LPAREN RPAREN'
    t[0] = absyn.Funcall(t[1], None)
    
def p_exp_parexp(t):
    'exp : LPAREN exp RPAREN'
    t[0] = t[2]

def p_arglist_exp(t):
    'arglist : exp'
    t[0] = [ t[1] ]

def p_arglist_2(t):
    'arglist : arglist COMMA arglist' 
    t[0] = t[1] + t[3]
    
# Error rule for syntax errors
def p_error(t):
    print "Syntax error in input!" + t.type


# debugging
if __name__ == '__main__':
    import sys
    # Build the parser
    yacc.yacc()

    for arg in sys.argv[1:]:
        s = open(arg,"r").read() # read in a whole file
        result = yacc.parse(s)
        print result.pretty()

    if len(sys.argv) == 1:
        while 1:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s: continue
            if s[0] == '#':
                s = open(s[1:],"r").read() # read in a whole file
                print s
            else:
                s += "\n"
            result = yacc.parse(s)
            print result.pretty()

