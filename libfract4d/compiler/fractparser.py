# Parser for UltraFractal + Fractint input files

import yacc
import fractlexer
import absyn

tokens = fractlexer.tokens

precedence = (

    ('right', 'ASSIGN'),
    ('left', 'BOOL_OR', 'BOOL_AND'),
    ('left', 'EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE','MOD'),
    ('right', 'BOOL_NEG', 'UMINUS')
)


def p_exp_plus(t):
    '''exp : exp PLUS exp
       exp : exp MINUS exp
       exp : exp TIMES exp
       exp : exp DIVIDE exp
       exp : exp MOD exp'''
    t[0] = absyn.Binop(t[2],t[1],t[3])

# implement unary minus as 0 - n
def p_exp_uminus(t):
    'exp : MINUS exp %prec UMINUS'
    t[0] = absyn.Binop("-", absyn.Number(0),t[2])
    
def p_exp_num(t):
    'exp : NUMBER'
    t[0] = absyn.Number(t[1])

def p_exp_expr(t):
    'exp : LPAREN exp RPAREN'
    t[0] = t[2]

# Error rule for syntax errors
def p_error(t):
    print "Syntax error in input!"


# debugging
if __name__ == '__main__':
    # Build the parser
    yacc.yacc()

    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s: continue
        result = yacc.parse(s)
        print result.pretty()

