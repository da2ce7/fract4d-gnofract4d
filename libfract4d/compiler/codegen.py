#!/usr/bin/env python

# Generate C code from a linearized IR trace

import ir
import symbol
import re
import types
import fracttypes



# action routines
def binop_const_exp(t):
    pass

def binop_exp_const(t):
    pass

def binop_exp_exp(t):
    pass

def expand_templates(list):
    return map(lambda x : [expand(x[0]), x[1]], list)

def expand(template):
    return re.sub(r'(\w+)',r'ir.\1',template)

# a list of templates and associated actions
# this must be ordered with largest, most efficient templates first
templates = expand_templates([
    [ "[Binop, Const, Exp]", binop_const_exp],
    [ "[Binop, Exp, Const]", binop_exp_const],
    [ "[Binop, Exp, Exp]" , binop_exp_exp]
    ])

# matching machinery

# implement naive tree matching. We match an ir tree against a nested list of classes
def match_template(tree, template):
    if tree == None:
        return template == None

    if template == None:
        return 0

    if isinstance(template,types.ListType):
        object = template[0]
        children = template[1:]
    else:
        object = template
        children = []
        
    if isinstance(tree, object):
        if children != []:
            if tree.children == None: return 0 
            for (child, matchChild) in zip(tree.children,children):
                if not match_template(child,matchChild):
                    return 0
        return 1
    else:
        return 0

def match(tree):
    for (template,action) in templates:
        if match_template(tree,template):
            return action
        
    # every possible tree ought to be matched by *something* 
    msg = "Internal Compiler Error: unmatched tree %s" % tree.pretty()
    raise fracttypes.TranslationError(msg)


