#!/usr/bin/env python

# Translate an abstract syntax tree into tree-structured intermediate
# code, performing type checking as a side effect
from absyn import *
import symbol
import fractparser
import exceptions
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
        try:
            self.formula(f)
        except TranslationError, e:
            self.errors.append(e.msg)
        
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
        #print f.pretty()
        
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

    def default(self,node):
        self.sections["default"] = 1

    def global_(self,node):
        self.sections["global"] = 1
        for child in node.children:
            self.stm(child)
            
    def stm(self,node,expectedType=None):
        if node.type == "decl":
            self.decl(node, None)
        elif node.type == "assign":
            self.assign(node)
        else:
            self.exp(node,expectedType)

    def assign(self, node):
        print "skip assign for now"
        
    def decl(self,node,expectedType):
        if expectedType != None:
            if expectedType != node.datatype:
                print "bad decl"
                self.badCast(node, expectedType)

        if node.children:
            self.stm(node.children[0],node.datatype)
        try:
            self.symbols[node.leaf] = Var(node.datatype, 0.0,node.pos) # fixme exp
        except KeyError, e:
            self.error("Invalid declaration on line %d: %s" % (node.pos,e))

    def exp(self,node,expectedType):
        if node.type == "const":
            self.const(node,expectedType)
        else:
            self.badNode(node,"exp")

    def const(self,node,expectedType):
        node = self.coerce(node, expectedType)

    def coerce(self, node, expectedType):
        if node.datatype == None:
            raise TranslationError("Internal Compiler Error: coercing an untyped node %s" % node)
        elif node.datatype == expectedType:
            return node
        elif node.datatype == Bool:
            # allowed widenings
            if expectedType == Int or expectedType == Float or expectedType == Complex:
                self.warnCast(node,expectedType)
                # fixme - rewrite exp with coercion
                return node
        elif node.datatype == Int:
            if expectedType == Bool or expectedType == Float or expectedType == Complex:
                self.warnCast(node,expectedType)
                return node
        elif node.datatype == Float:
            if expectedType == Bool or expectedType == Complex:
                self.warnCast(node, expectedType)
                return node
        elif node.datatype == Complex:
            if expectedType == Bool:
                self.warnCast(node, expectedType)
                return node
            
        # if we didn't cast successfully, fall through to here
        self.badCast(node,expectedType)
            
    def init(self,node):
        self.sections["init"] = 1
        for child in node.children:
            self.stm(child)

    def loop(self, node):
        self.sections["loop"] = 1
        for child in node.children:
            self.stm(child)

    def bailout(self,node):
        self.sections["bailout"] = 1
        for child in node.children:
            self.stm(child)

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
