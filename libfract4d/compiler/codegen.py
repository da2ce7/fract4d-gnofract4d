#!/usr/bin/env python

# Generate C code from a linearized IR trace

import string

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

def filter_nulls(l):
    return [x for x in l if x != []]

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

class ComplexArg:
    ' a pair of args'
    def __init__(self,re,im):
        self.re = re
        self.im = im
    def format(self):
        [self.re.format(), self.i.format()]
        
class ConstFloatArg:
    def __init__(self,value):
        self.value = value
    def format(self):
        return "%.17f" % self.value

class ConstIntArg:
    def __init__(self,value):
        self.value = value
    def format(self):
        return "%d" % self.value

class TempArg:
    def __init__(self,value):
        self.value = value
    def format(self):
        return self.value

def create_arg_from_val(type,val):
    if type == Int or type == Bool:
        return ConstIntArg(val)
    elif type == Float:
        return ConstFloatArg(val)
    elif type == Complex:
        return ComplexArg(ConstFloatArg(val[0]),ConstFloatArg(val[1]))
    else:
        raise TranslationError("Unknown constant type %s", type)
    
def create_arg(t):
    return create_arg_from_val(t.datatype,t.value)
    
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
                    lookup[sname] = src.format()
                    i = i+1
                i = 0
            if self.dst != None:
                for dst in self.dst:
                    dname = "d%d" % i
                    lookup[dname] = dst.format()
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

class Decl(Insn):
    ' a variable declaration'
    def __init__(self,assem):
        Insn.__init__(self,assem)
        self.src = None
        self.dst = None
        
class Formatter:
    ' fed to print to fill the output template'
    def __init__(self, codegen, tree, lookup):
        self.codegen = codegen
        self.lookup = lookup
        self.tree = tree
    def __getitem__(self,key):
        try:
            out = self.tree.output_sections[key]
            str_output = string.join(map(lambda x : x.format(), out),"\n")
            return str_output

        except KeyError, err:
            #print "missed %s" % key
            return self.lookup.get(key,"")

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
            [ "[Unop]", T.unop],
            [ "[Var]" , T.var],
            [ "[Const]", T.const],
            [ "[Label]", T.label],
            [ "[Move]", T.move],
            [ "[Jump]", T.jump],
            [ "[Cast]", T.cast],
            ])
        self.output_template = '''
#include <stdio.h>
int main()
{
/* variable declarations */
%(decls)s
int nMaxIters = 16, nIters = 0;
%(init)s
t__end_init:
while(nIters < nMaxIters)
{
    %(loop)s
    t__end_loop:
    %(loop_inserts)s
    %(bailout)s
    t__end_bailout:
    %(bailout_inserts)s
    if(%(bailout_var)s) break;
    nIters++;
}
%(done_inserts)s
return 0;
}'''

    def emit_binop(self,op,srcs,type):
        dst = TempArg(self.symbols.newTemp(type))

        assem = "%(d0)s = %(s0)s " + op + " %(s1)s;"
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
                    out += [ Decl("%s %s_re = %.17f;" % (t,key,val[0])),
                             Decl("%s %s_im = %.17f;" % (t,key,val[1]))]
                elif sym.type == fracttypes.Float:
                    out.append(Decl("%s %s = %.17f;" % (t,key,val)))
                else:
                    out.append(Decl("%s %s = %d;" % (t,key,val)))
            else:
                #print "Weird symbol %s: %s" %( key,sym)
                pass
        return out

    def output_section(self,t,section):
        self.out = []
        self.generate_all_code(t.canon_sections[section])
        t.output_sections[section] = self.out
    
    def output_all(self,t):
        for k in t.canon_sections.keys():
            self.output_section(t,k)
        # must be done afterwards or temps are missing
        t.output_sections["decls"] = self.output_symbols()
        
    def output_c(self,t,inserts={}):
        # find bailout variable
        bailout_insn = t.output_sections["bailout"][-2]
        inserts["bailout_var"] = bailout_insn.dst[0]
        f = Formatter(self,t,inserts)
        return self.output_template % f
        
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
                bc = self.emit_binop(t.op, s0, 1, s1, 0, [r[0],i[1]], Float)
                ad = self.emit_binop(t.op, s0, 0, s1, 1, [r[1],i[0]], Float)
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
            dst = self.emit_binop(t.op,srcs,t.datatype)
            
        return dst
    
    def const(self,t):
        return create_arg(t)
    
    def var(self,t):
        if t.datatype == fracttypes.Complex:
            return ComplexArg(TempArg(t.name + "_re"),TempArg(t.name + "_im"))
        else:
            return TempArg(t.name)
    
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


