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
        
        self.formula(f)
        
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

    def canonicalizeSections(self,f):        
        '''a nameless section (started by ':') is the same as a loop
           section with the last stm as a bailout section - make this
           change'''

        # a "nameless" section is really an init section
        s = f.childByName("nameless")
        if s:
            oldinit = f.childByName("init")
            if oldinit:
                self.warning(
                    "formula contains a fractint-style implicit int section\
                    and an explicit UltraFractal init section. \
                    Using explict section.")
            else:
                s.leaf = "init"
        
        s = f.childByName("")
        if not s:
            return
        
        bailout = s.children[-1]
        loop = s.children[:-1]
        
        oldbailout = f.childByName("bailout")
        if oldbailout:
            self.warning(
                "formula contains a fractint-style implicit bailout section\
                and an explicit UltraFractal bailout section. \
                Using explict section.")
        else:
            f.children.append(Stmlist("bailout",bailout, bailout.pos))
        
        oldloop = f.childByName("loop")
        if oldloop:
            self.warning(
                "formula contains a fractint-style implicit loop section\
                and an explicit UltraFractal loop section. \
                Using explict section.")
        else:
            f.children.append(Stmlist("loop",loop,loop[0].pos))

        f.children.remove(s)

    def default(self,node):
        self.sections["default"] = 1

    def global_(self,node):
        self.sections["global"] = 1
        for child in node.children:
            self.stm(child)
            
    def stm(self,node):
        if node.type == "decl":
            self.decl(node)

    def decl(self,node):
        try:
            self.symbols[node.leaf] = Var(node.datatype, 0.0) # fixme exp
        except KeyError, e:
            self.error("%s" % e)
    
    def init(self,node):
        self.sections["init"] = 1

    def loop(self, node):
        self.sections["loop"] = 1

    def bailout(self,node):
        self.sections["bailout"] = 1

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
