#!/usr/bin/env python

# Generate C code from a linearized IR trace

import ir
import symbol
import re
import types
import fracttypes

class Insn:
    'An instruction to be written to output stream'
    def __init__(self,assem):
        self.assem = assem # string format of instruction

class Oper(Insn):
    ' An operation'
    def __init__(self,assem, src, dst, jumps=[]):
        Insn.__init__(self,assem)
        self.src = src
        self.dst = dst
        self.jumps = jumps
    def __str__(self):
        return "OPER(%s,%s,%s,%s)" % (self.assem, self.src, self.dst, self.jumps)
    
class Label(Insn):
    'A label which can be jumped to'
    def __init__(self,assem, label):
        Insn.__init__(self,assem)
        self.label = label
    def __str__(self):
        return "%s:",self.label
    
class Move(Insn):
    ' A move instruction'
    def __init__(self,assem,src,dst):
        Insn.__init__(self,assem)
        self.src = src
        self.dst = dst
    def __str__(self):
        return "MOVE(%s,%s,%s)" % (self.assem, self.src, self.dst)
    
class T:
    'code generator'
    def __init__(self,symbols):
        self.symbols = symbols
        self.out = []
        # a list of templates and associated actions
        # this must be ordered with largest, most efficient templates first
        # thus performing a crude 'maximal munch' instruction generation
        self.templates = self.expand_templates([
            [ "[Binop, Const, Exp]", T.binop_const_exp],
            [ "[Binop, Exp, Const]", T.binop_exp_const],
            [ "[Binop, Exp, Exp]" , T.binop_exp_exp],
            [ "[Var]" , T.var]
            ])

    # action routines
    def binop_const_exp(self,t):
        s0 = t.children[0]
        s1 = t.children[1]
        dst = self.symbols.newTemp(t.datatype)
        assem = "%%(d0)s = %d %s %%(s1)s" % (s0.value, t.op)
        print assem
        self.out.append(Oper(assem, [ self.generate_code(s1) ] , [dst]))
        return dst
    
    def binop_exp_const(self,t):
        pass

    def binop_exp_exp(self,t):
        pass

    def var(self,t):
        return t.name
    
    # matching machinery
    def generate_code(self,tree):
        action = self.match(tree)
        return apply(action,(self,tree))

    def expand_templates(self,list):
        return map(lambda x : [self.expand(x[0]), x[1]], list)

    def expand(self, template):
        return eval(re.sub(r'(\w+)',r'ir.\1',template))

    # implement naive tree matching. We match an ir tree against a nested list of classes
    def match_template(self, tree, template):
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
                    if not self.match_template(child,matchChild):
                        return 0
            return 1
        else:
            return 0

    def match(self,tree):
        for (template,action) in self.templates:
            if self.match_template(tree,template):
                return action
        
        # every possible tree ought to be matched by *something* 
        msg = "Internal Compiler Error: unmatched tree %s" % tree.pretty()
        raise fracttypes.TranslationError(msg)


