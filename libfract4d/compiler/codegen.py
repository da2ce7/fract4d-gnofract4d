#!/usr/bin/env python

# Generate C code from a linearized IR trace

import ir
import symbol
import re
import types

# implement naive tree matching. We match an ir tree against a nested list of classes
def match(tree, template):
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
                if not match(child,matchChild):
                    return 0
        return 1
    else:
        return 0
    
template = "[Binop, Const, Const]"

def expand(template):
    return re.sub(r'(\w+)',r'ir.\1',template)
