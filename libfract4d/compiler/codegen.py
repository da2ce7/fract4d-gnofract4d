#!/usr/bin/env python

# Generate C code from a linearized IR trace

import ir
import symbol
import re
import types
import fracttypes
from fracttypes import Bool, Int, Float, Complex

def reals(l):
    # [[a + ib], [c+id]] => [ a, c]
    return map(lambda x : x[0],filter(lambda x : x != [],l))

def imags(l):
    return map(lambda x : x[1],filter(lambda x : x != [],l))

def format_string(t,index,pos):
    # compute a format string for a binop's child at position pos
    if isinstance(t,ir.Const):
        if t.datatype == Int or t.datatype == Bool:
            return ("%d" % t.value,pos)
        elif t.datatype == Float:
            return ("%.17f" % t.value,pos)
        elif t.datatype == Complex:
            return ("%.17f" % t.value[index],pos)
        else:
            raise KeyError, "Invalid type %s" % t.datatype.__class__.__name__
    else:
        return ("%%(s%d)s" % pos,pos+1)

class Insn:
    'An instruction to be written to output stream'
    def __init__(self,assem):
        self.assem = assem # string format of instruction
    def format(self,lookup = None):
        if lookup == None:
            lookup = {}
            i = 0
            if self.src != None:
                for src in self.src:
                    sname = "s%d" % i
                    lookup[sname] = src
                    i = i+1
                i = 0
            if self.dst != None:
                for dst in self.dst:
                    dname = "d%d" % i
                    lookup[dname] = dst
                    i = i+1
        try:
            return self.assem % lookup
        except Exception, exn:
            msg = "%s with %s" % (self, lookup)
            raise fracttypes.TranslationError(
                "Internal Compiler Error: can't format " + msg)


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
    def __init__(self, label):
        Insn.__init__(self,"%s:" % label)
        self.label = label
    def format(self, lookup=None):
        return "%s" % self
    def __str__(self):
        return "%s:" % self.label
    
class Move(Insn):
    ' A move instruction'
    def __init__(self,format,src,dst):
        Insn.__init__(self,"%%(d0)s = %s;" % format)
        self.src = src
        self.dst = dst
    def __str__(self):
        return "MOVE(%s,%s,%s)" % (self.assem, self.src, self.dst)
    
class T:
    'code generator'
    def __init__(self,symbols,dump=None):
        self.symbols = symbols
        self.out = []
        # a list of templates and associated actions
        # this must be ordered with largest, most efficient templates first
        # thus performing a crude 'maximal munch' instruction generation
        self.templates = self.expand_templates([
            [ "[Binop]" , T.binop],
            [ "[Var]" , T.var],
            [ "[Const]", T.const],
            [ "[Label]", T.label],
            [ "[Move]", T.move],
            [ "[Jump]", T.jump],
            [ "[Cast]", T.cast],
            [ "[Unop]", T.unop]
            ])


    def emit_binop(self,op,s0,index1,s1,index2,srcs,type):
        dst = self.symbols.newTemp(type)

        (f1,pos) = format_string(s0,index1,0)
        (f2,pos) = format_string(s1,index2,pos)

        assem = "%%(d0)s = %s %s %s;" % (f1, op, f2)
        self.out.append(Oper(assem, srcs ,[ dst ]))
        return dst

    def emit_move(self, s0, index1, src, dst):
        (f1,pos) = format_string(s0,index1,0)
        self.out.append(Move(f1,src,dst))
        
    def output_symbols(self):
        out = []
        for (key,sym) in self.symbols.items():
            if isinstance(sym,fracttypes.Var):
                t = fracttypes.ctype(sym.type)
                val = sym.value
                if sym.type == fracttypes.Complex:
                    out += [ "%s %s_re = %.17f;" % (t,key,val[0]),
                             "%s %s_im = %.17f;" % (t,key,val[1])]
                elif sym.type == fracttypes.Float:
                    out.append("%s %s = %.17f;" % (t,key,val))
                else:
                    out.append("%s %s = %d;" % (t,key,val))
            else:
                #print "Weird symbol %s: %s" %( key,sym)
                pass
        return out
    
    # action routines
    def cast(self,t):
        child = t.children[0]
        src = self.generate_code(child)

        dst = None
        if t.datatype == Complex:
            (d0,d1) = (self.symbols.newTemp(Float), self.symbols.newTemp(Float))
            if child.datatype == Int or child.datatype == Bool:
                (f1,pos) = format_string(child,-1,0)
                assem = "%%(d0)s = ((double)%s);" % f1
                self.out.append(Oper(assem,src, [d0]))
                assem = "%(d0)s = 0.0;"
                self.out.append(Oper(assem,src, [d1]))
                dst = [d0, d1]
            elif child.datatype == Float:
                (f1,pos) = format_string(child,-1,0)
                assem = "%%(d0)s = %s;" % f1
                self.out.append(Oper(assem,src, [d0]))
                assem = "%(d0)s = 0.0;"
                self.out.append(Oper(assem,src, [d1]))
                dst = [d0, d1]
        elif t.datatype == Float:
            d0 = self.symbols.newTemp(Float)
            if child.datatype == Int or child.datatype == Bool:
                (f1,pos) = format_string(child,-1,0)
                assem = "%%(d0)s = ((double)%s);" % f1
                self.out.append(Oper(assem,src, [d0]))
                dst = [d0]
        elif t.datatype == Int:
            if child.datatype == Bool:
                # needn't do anything
                dst = src
        elif t.datatype == Bool:            
            # FIXME implement these
            pass
        
        if dst == None:
            msg = "Invalid Cast from %s to %s" % (child.datatype, t.datatype)
            raise TranslationError(msg)
        
        return dst
                
    def move(self,t):
        dst = self.generate_code(t.children[0])
        src = self.generate_code(t.children[1])
        if t.datatype == Complex:
            self.emit_move(t.children[1],0,[src[0]],[dst[0]])
            self.emit_move(t.children[1],1,[src[1]],[dst[1]])
        else:
            self.emit_move(t.children[1],-1,src,dst)
        return dst
    
    def label(self,t):
        assert(t.children == [])
        self.out.append(Label(t.name))

    def jump(self,t):
        assem = "goto %s;" % t.dest
        self.out.append(Oper(assem,[],[],[t.dest]))

    def unop(self,t):
        s0 = t.children[0]
        src = self.generate_code(s0)
        if t.op == "mag":
            # x_re * x_re + x_im * x_im
            re_2 = self.emit_binop('*',s0,0,s0,0,[src[0],src[0]],Float)
            im_2 = self.emit_binop('*',s0,1,s0,1,[src[1],src[1]],Float)
            dst = [ self.emit_binop('+',re_2,-1,im_2,-1,[re_2,im_2],Float)]
        else:
            msg = "Unsupported unary operation %s" % t.op
            raise TranslationError(msg)

        return dst
    
    def binop(self,t):
        s0 = t.children[0]
        s1 = t.children[1]
        srcs = [self.generate_code(s0), self.generate_code(s1)]
        if t.datatype == fracttypes.Complex:
            if t.op=="+" or t.op == "-":
                dst = [
                    self.emit_binop(t.op,s0,0, s1,0, reals(srcs), Float),
                    self.emit_binop(t.op,s0,1, s1,1, imags(srcs), Float)]
            elif t.op=="*":
                # (a+ib) * (c+id) = ac - bd + i(bc + ad)
                r = reals(srcs) ; i = imags(srcs)
                ac = self.emit_binop(t.op, s0, 0, s1, 0, r, Float)
                bd = self.emit_binop(t.op, s0, 1, s1, 1, i, Float)
                bc = self.emit_binop(t.op, s0, 1, s1, 0, r, Float)
                ad = self.emit_binop(t.op, s0, 0, s1, 1, i, Float)
                dst = [
                    self.emit_binop('-', ac, -1, bd, -1, [ac, bd], Float),
                    self.emit_binop('+', bc, -1, ad, -1, [bc, ad], Float)]
            elif t.op==">" or t.op==">=" or t.op=="<" or t.op == "<=":
                # compare real parts only
                dst = [
                    self.emit_binop(t.op,s0,0,s1,0, reals(srcs), Bool)]
            elif t.op=="==" or t.op=="!=":
                # compare both
                d1 = self.emit_binop(t.op,s0, 0, s1, 0, reals(srcs), Bool)
                d2 = self.emit_binop(t.op,s0, 1, s1, 1, imags(srcs), Bool)
                if t.op=="==":
                    combine_op = "&&"
                else:
                    combine_op = "||"
                dst = [
                    self.emit_binop(combine_op, d1, -1, d2, -1, [d1,d2], Bool)]
            else:
                # need to implement /, compares, etc
                msg = "Unsupported binary operation %s" % t.op
                raise fracttypes.TranslationError(msg)
        else:
            dst = [
                self.emit_binop(t.op,s0,-1,s1,-1,reals(srcs),t.datatype)]
        return dst
    
    def const(self,t):
        return []
    
    def var(self,t):
        if t.datatype == fracttypes.Complex:
            return [ t.name + "_re", t.name + "_im"]
        else:
            return [ t.name ]
    
    # matching machinery
    def generate_all_code(self,treelist):
        for tree in treelist:
            self.generate_code(tree)
        
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
        msg = "Internal Compiler Error: unmatched tree %s" % tree
        raise fracttypes.TranslationError(msg)


