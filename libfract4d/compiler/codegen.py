#!/usr/bin/env python

# Generate C code from a linearized IR trace

import ir
import symbol
import re
import types
import fracttypes
from fracttypes import Bool, Int, Float, Complex

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
    def format(self,lookup = None):
        if lookup == None:
            lookup = {}
            i = 0
            for src in self.src:
                sname = "s%d" % i
                lookup[sname] = src
                i = i+1
            i = 0
            for dst in self.dst:
                dname = "d%d" % i
                lookup[dname] = dst
                i = i+1
        return self.assem % lookup
    
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

    def emit_binop_const_exp(self,op,val,srcs,type):
        dst = self.symbols.newTemp(type)
        assem = "%%(d0)s = %d %s %%(s0)s" % (val, op)
        self.out.append(Oper(assem, srcs ,[ dst ]))
        return dst
    
    # action routines
    def binop_const_exp(self,t):
        s0 = t.children[0]
        s1 = t.children[1]
        srcs = self.generate_code(s1)
        if t.datatype == fracttypes.Complex:
            if t.op=="+" or t.op == "-":
                dst = [
                    self.emit_binop_const_exp(t.op,s0.value[0], [srcs[0]], Float),
                    self.emit_binop_const_exp(t.op,s0.value[1], [srcs[1]], Float)]
            if t.op=="*":
                # (a+ib) * (c+id) = ac - bd + i(bc + ad)
                (a,b,c,d) = (s0.value[0], s0.value[1], srcs[0], srcs[1])
                self.emit_binop_const_exp(t.op,a, [b], [d0], Float)
        else:
            dst = [
                self.emit_binop_const_exp(t.op,s0.value,srcs,t.datatype)]
        return dst
    
    def binop_exp_const(self,t):
        pass

    def binop_exp_exp(self,t):
        pass

    def var(self,t):
        if t.datatype == fracttypes.Complex:
            return [ t.name + "_re", t.name + "_im"]
        else:
            return [ t.name ]
    
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


