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
        self.dumpTranslation = 1
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
        seq = ir.Seq(map(lambda c: self.stm(c), node.children), node, None)
        return seq
        
    def stm(self,node):
        if node.type == "decl":
            r = self.decl(node)
        elif node.type == "assign":
            r = self.assign(node)
        else:
            r = self.exp(node)
        return r
    
    def assign(self, node):
        '''assign a new value to a variable, creating it if required'''
        if not self.symbols.has_key(node.leaf):
            # implicitly create a new var - a warning?
            self.symbols[node.leaf] = Var(fracttypes.Complex,0,node)

        expectedType = self.symbols[node.leaf].type
        rhs = self.exp(node.children[0])
        
        lhs = ir.Name(node.leaf, node, node.datatype)
        return ir.Move(lhs,self.coerce(rhs,expectedType),node,expectedType)

    def findOp(self, opnode, list):
        overloadList = self.symbols[opnode.leaf]
        typelist = map(lambda ir : ir.datatype , list)
        for ol in overloadList:
            if ol.matchesArgs(typelist):
                return ol
        raise TranslationError(
            "Invalid argument types %s for %s on line %s" % \
            (typelist, opnode.leaf, opnode.pos))
            
    def decl(self,node):
        if node.children:
            exp = self.stm(node.children[0])
        else:
            # default initializer
            exp = ir.Const(fracttypes.default(node.datatype),
                           node, node.datatype)

        try:
            # fixme - get exp right instead of 0.0
            self.symbols[node.leaf] = Var(node.datatype, 0.0, node.pos)
            return ir.Move(
                ir.Name(node.leaf, node, node.datatype),                
                self.coerce(exp, node.datatype),
                node, node.datatype)
        
        except KeyError, e:
            self.error("Invalid declaration on line %d: %s" % (node.pos,e))

    def exp(self,node):
        if node.type == "const":
            r = self.const(node)
        elif node.type == "id":
            r = self.id(node)
        elif node.type == "binop":
            r = self.binop(node)
        else:
            self.badNode(node,"exp")

        return r

    def binop(self, node):
        # todo - detect and special-case logical operations
        children = map(lambda n : self.exp(n) , node.children)        
        op = self.findOp(node,children)
        return ir.Binop(node.leaf,
                        self.coerceList(op.args,children),
                        node,op.ret)
    
    def id(self, node):
        try:
            node.datatype = self.symbols[node.leaf].type
        except KeyError, e:
            self.warning(
                "Uninitialized variable %s referenced on line %d" % \
                (node.leaf, node.pos))
            self.symbols[node.leaf] = Var(fracttypes.Complex, 0.0, node.pos)
            node.datatype = fracttypes.Complex

        return ir.Var(node.leaf, node, node.datatype)
        
    def const(self,node):
        return ir.Const(node.leaf, node, node.datatype)        

    def coerceList(self,expList,typeList):
        return map( lambda (exp,ty) : self.coerce(exp,ty) ,
                    zip(typeList, expList))
    
    def coerce(self, exp, expectedType):
        '''insert code to cast exp to expectedType 
           or produce an error if conversion is not permitted'''

        if exp.datatype == None or expectedType == None:
            raise TranslationError("Internal Compiler Error: coercing an untyped node")
        elif exp.datatype == expectedType:
            return exp

        if fracttypes.canBeCast(exp.datatype, expectedType):
            self.warnCast(exp, expectedType)
            return ir.Cast(exp, exp.node, expectedType)
        else:
            self.badCast(exp,expectedType)
            
    def init(self,node):
        self.sections["init"] = self.stmlist(node)

    def loop(self, node):
        self.sections["loop"] = self.stmlist(node)

    def bailout(self,node):
        self.sections["bailout"] = self.stmlist(node)

    def badNode(self, node, rule):
        msg = "Internal Compiler Error: Unexpected node '%s' in %s" % \
            (node.type, rule)
        raise TranslationError(msg)

    def badCast(self, exp, expectedType):
        raise TranslationError(
           ("invalid type %s for %s on line %s, expecting %s" %
            (strOfType(exp.datatype), exp.node.leaf, exp.node.pos, strOfType(expectedType))))
    def warnCast(self,exp,expectedType):
        msg = "Warning: conversion from %s to %s on line %s" % \
        (strOfType(exp.datatype), strOfType(expectedType), exp.node.pos)
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
