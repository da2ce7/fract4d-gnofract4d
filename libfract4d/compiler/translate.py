#!/usr/bin/env python

# Translate an abstract syntax tree into tree-structured intermediate
# code, performing type checking as a side effect
from absyn import *
import symbol
import fractparser
import exceptions
import ir
from fracttypes import *

class TranslationError(exceptions.Exception):
    def __init__(self,msg):
        self.msg = msg
    
class T:
    def __init__(self,f):
        self.symbols = symbol.T()
        self.errors = []
        self.warnings = []
        self.sections = {}
        self.dumpCanon = 0
        self.dumpDecorated = 0
        self.dumpProbs = 0
        self.dumpTranslation = 0
        self.dumpVars = 0
        try:
            self.formula(f)
        except TranslationError, e:
            self.errors.append(e.msg)

        if self.dumpProbs:
            print self.errors
            print self.warnings
            
        if self.dumpDecorated:
            print f.pretty()

        if self.dumpVars:
            for (name,sym) in self.symbols.items():
                if self.symbols.is_user(name):
                    print name,": ",sym
        
        if self.dumpTranslation:
            print f.leaf + "{"
            for (name,tree) in self.sections.items():
                if tree != None:
                    print " " + name + "("
                    print tree.pretty(2) + " )"
            print "}\n"
                
    def error(self,msg):
        self.errors.append(msg)
    def warning(self,msg):
        self.warnings.append(msg)
        
    def formula(self, f):
        self.symbols.reset()
        if f.children[0].type == "error":
            self.error(f.children[0].leaf)
            return

        self.canonicalizeSections(f)
        
        # lookup sections in order
        s = f.childByName("default")
        if s: self.default(s)
        s = f.childByName("global")
        if s: self.global_(s)
        s = f.childByName("init")
        if s: self.init(s)
        s = f.childByName("loop")
        if s: self.loop(s)
        s = f.childByName("bailout")
        if s: self.bailout(s)
        #  ignore switch and builtin for now

    def dupSectionWarning(self,sect):
        self.warning(
                    "formula contains a fractint-style implicit %s section\
                    and an explicit UltraFractal %s section. \
                    Using explict section." % (sect,sect))
        
    def canonicalizeSections(self,f):        
        '''a nameless section (started by ':') is the same as a loop
           section with the last stm as a bailout section - make this
           change'''

        # a "nameless" section is really an init section
        s = f.childByName("nameless")
        if s:
            oldinit = f.childByName("init")
            if oldinit:
                self.dupSectionWarning("init")
            else:
                s.leaf = "init"
        
        s = f.childByName("")
        if not s:
            return
        
        bailout = [s.children[-1]]
        loop = s.children[:-1]
        
        oldbailout = f.childByName("bailout")
        if oldbailout:
            self.dupSectionWarning("bailout")
        else:
            f.children.append(Stmlist("bailout",bailout, bailout[0].pos))
        
        oldloop = f.childByName("loop")
        if oldloop:
            self.dupSectionWarning("loop")
        else:
            f.children.append(Stmlist("loop",loop,loop[0].pos))

        f.children.remove(s)

        if self.dumpCanon:
            print f.pretty()

    def default(self,node):
        self.sections["default"] = 1

    def global_(self,node):
        self.sections["global"] = self.stmlist(node)

    def stmlist(self, node):
        seq = ir.Seq(map(lambda c: self.stm(c), node.children), node.pos, None)
        return seq
        
    def stm(self,node,expectedType=None):
        if node.type == "decl":
            r = self.decl(node, None)
        elif node.type == "assign":
            r = self.assign(node)
        else:
            r = self.exp(node,expectedType)
        return r
    
    def assign(self, node):
        '''assign a new value to a variable, creating it if required'''
        if not self.symbols.has_key(node.leaf):
            # implicitly create a new var - a warning?
            self.symbols[node.leaf] = Var(fracttypes.Complex,0,node.pos)

        expectedType = self.symbols[node.leaf].type
        e = self.exp(node.children[0],expectedType)
        
        lhs = ir.Name(node.leaf, node.pos, expectedType)
        rhs = e
        return self.coerce(lhs,rhs,node.children[0])
    
    def decl(self,node,expectedType):
        if expectedType != None:
            if expectedType != node.datatype:
                print "bad decl"
                self.badCast(node, expectedType)

        if node.children:
            exp = self.stm(node.children[0],node.datatype)
        else:
            # default initializer
            exp = ir.Const(fracttypes.default(node.datatype),
                           node.pos, node.datatype)

        try:
            self.symbols[node.leaf] = Var(node.datatype, 0.0,node.pos) # fixme exp
            return self.coerce(
                ir.Name(node.leaf, node.pos, node.datatype),
                exp, node)
        
        except KeyError, e:
            self.error("Invalid declaration on line %d: %s" % (node.pos,e))

    def exp(self,node,expectedType):
        if node.type == "const":
            r = self.const(node,expectedType)
        elif node.type == "id":
            r = self.id(node,expectedType)
        elif node.type == "binop":
            r = self.binop(node,expectedType)
        else:
            self.badNode(node,"exp")

        return r

    def binop(self, node, expectedType):
        # todo - detect and special-case logical operations
        for child in node.children:
            self.exp(child,expectedType)
        self.datatype = expectedType

        
    def id(self, node, expectedType):
        try:
            node.datatype = self.symbols[node.leaf].type
        except KeyError, e:
            self.warning(
                "Uninitialized variable %s referenced on line %d" % \
                (node.leaf, node.pos))
            self.symbols[node.leaf] = Var(fracttypes.Complex, 0.0, node.pos)
            node.datatype = fracttypes.Complex

        if expectedType == node.datatype:
            return ir.Var(node.leaf, node.pos, node.datatype)
        else:
            return self.coerce(node, node.pos, expectedType)
        
    def const(self,node,expectedType):
        return ir.Const(node.leaf, node.pos, node.datatype)        
    
    def coerce(self, lhs, rhs, node):
        '''insert code to assign rhs to lhs, even if they are different types,
           or produce an error if conversion is not permitted'''

        ok = 0
        if lhs.datatype == None or rhs.datatype == None:
            raise TranslationError("Internal Compiler Error: coercing an untyped node")
        elif lhs.datatype == rhs.datatype:
            ok = 1
            
        elif rhs.datatype == Bool:
            if lhs.datatype == Int or lhs.datatype == Float: 
                self.warnCast(rhs,lhs.datatype)
                rhs = ir.Cast(rhs,lhs.datatype,rhs.pos)
                ok = 1
            elif lhs.datatype == Complex:
                self.warnCast(rhs,lhs.datatype)
                lhs = ir.Real(lhs,lhs.pos)
                rhs = ir.Cast(rhs,Float,rhs.pos)
                ok = 1
        elif rhs.datatype == Int:
            if lhs.datatype == Bool or lhs.datatype == Float:
                self.warnCast(rhs,lhs.datatype)
                rhs = ir.Cast(rhs,lhs.datatype,rhs.pos)
                ok = 1
            elif lhs.datatype == Complex:
                self.warnCast(rhs,lhs.datatype)
                rhs = ir.Cast(rhs,Float,rhs.pos)
                lhs = ir.Real(lhs,lhs.pos)
                ok = 1
        elif rhs.datatype == Float:
            if lhs.datatype == Bool:
                self.warnCast(rhs, lhs.datatype)
                rhs = ir.Cast(rhs, lhs.datatype, rhs.pos)
                ok = 1
            elif lhs.datatype == Complex:
                self.warnCast(rhs, lhs.datatype)
                lhs = ir.Real(lhs, lhs.pos)
                ok = 1
        elif rhs.datatype == Complex:
            if lhs.datatype == Bool:
                self.warnCast(rhs, lhs.datatype)
                rhs = ir.Cast(rhs, lhs.datatype, rhs.pos)
                ok = 1

        if ok:
            return ir.Move(lhs,rhs,lhs.pos,lhs.datatype)
        
        # if we didn't cast successfully, fall through to here
        self.badCast(node,lhs.datatype)
            
    def init(self,node):
        self.sections["init"] = self.stmlist(node)

    def loop(self, node):
        self.sections["loop"] = self.stmlist(node)

    def bailout(self,node):
        self.sections["bailout"] = self.stmlist(node)

    def badNode(self, node, rule):
        msg = "Internal Compiler Error: Unexpected node '%s' in %s" % \
            (node.type, rule)
        print msg
        raise TranslationError(msg)

    def badCast(self, node, expectedType):
        raise TranslationError(
           ("invalid type %s for %s %s on line %s, expecting %s" %
            (strOfType(node.datatype), node.type, node.leaf, node.pos, strOfType(expectedType))))
    def warnCast(self,node,expectedType):
        msg = "Warning: conversion from %s to %s on line %s" % \
        (strOfType(node.datatype), strOfType(expectedType), node.pos)
        self.warnings.append(msg)
        
parser = fractparser.parser
     
# debugging
if __name__ == '__main__':
    import sys
    
    for arg in sys.argv[1:]:
        s = open(arg,"r").read() # read in a whole file
        result = parser.parse(s)
        for formula in result.children:
            t = T(formula)
            if t.errors != []:
                print "Errors translating %s:" % formula.leaf
                for e in t.errors:
                    print "\t",e
