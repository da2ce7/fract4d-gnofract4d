# Intermediate representation. The Translate module converts an Absyn tree
# into an IR tree.

import types
import string
import fracttypes
import re


def d(depth,s=""):
    return " " * depth + s

class T:
    def __init__(self, node, datatype):
        self.datatype = datatype
        self.node = node # the absyn node we were constructed from
        self.children = None
    def pretty_children(self,depth):
        r = []
        if self.children != None:
            for child in self.children:
                if child == None:
                    r.append(d(depth+1,"<<None>>"))
                else:
                    r.append(child.pretty(depth+1))
        return string.join(r,"")
    
# exp and subtypes
# an exp computes a value

class Exp(T):
    def __init__(self, node, datatype):
        T.__init__(self, node, datatype)

class Const(Exp):
    def __init__(self, value, node, datatype):
        Exp.__init__(self, node, datatype)
        self.value = value
    def pretty(self,depth=0):
        return d(depth) + "Const(%s)\n" % self.value 
    
class Name(Exp):
    def __init__(self, label, node, datatype):
        Exp.__init__(self, node, datatype)
        self.label = label
    def pretty(self,depth=0):
        return d(depth) + "Name(" + self.label + ")\n"
    
class Temp(Exp):
    def __init__(self, temp, node, datatype):
        Exp.__init__(self, node, datatype)
        self.temp = temp
    def pretty(self, depth=0):
        return d(depth) + "Temp(" + self.temp + ")\n"

class Binop(Exp):
    def __init__(self, op, children, node, datatype):
        Exp.__init__(self, node, datatype)
        (self.op, self.children) = (op,children)
    def pretty(self, depth=0):
        return d(depth) + "Binop(" + self.op + "\n" + \
               self.pretty_children(depth) + \
               d(depth,")\n")
    
class Var(Exp):
    def __init__(self, name, node, datatype):
        Exp.__init__(self, node, datatype)
        self.name = name
    def pretty(self, depth=0):
        return d(depth) + "Var(" + self.name + ")\n"

class Real(Exp):
    def __init__(self, cexp, node):
        Exp.__init__(self,node, fracttypes.Float)
        self.cexp = cexp
    def pretty(self,depth=0):
        return d(depth) + "Real(\n" + self.cexp.pretty(depth+1) + d(depth,")\n")

class Cast(Exp):
    def __init__(self, exp, node, datatype):
        Exp.__init__(self,node, datatype)
        self.children = [exp]
    def pretty(self,depth=0):
        cast_str = "Cast<%s,%s>(\n" % \
                   (fracttypes.strOfType(self.children[0].datatype),
                    fracttypes.strOfType(self.datatype))  
        return d(depth) + \
               cast_str + \
               self.pretty_children(depth) + d(depth,")\n")
    
class Call(Exp):
    def __init__(self, func, args, node, datatype):
        Exp.__init__(self, node, datatype)
        self.func = func
        self.children = args
    def pretty(self, depth=0):
        r = d(depth) + "Call(" + self.func + "\n"
        r += self.pretty_children(depth) 
        r += d(depth,")\n")
        return r
        
class ESeq(Exp):
    def __init__(self, stm, exp, node, datatype):
        Exp.__init__(self, node, datatype)
        self.stm = stm
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "ESeq(\n" + \
               self.stm.pretty(depth+1) + self.exp.pretty(depth+1) + \
               d(depth,")\n")
    
# stm and subtypes
# side effects + flow control

class Stm(T):
    def __init__(self, node, datatype): 
        T.__init__(self, node, datatype)

class Move(Stm):
    def __init__(self, dest, exp, node, datatype):
        Stm.__init__(self, node, datatype)
        self.children = [dest,exp]
    def pretty(self, depth=0):
        return d(depth) + "Move(\n" + \
               self.pretty_children(depth) + \
               d(depth,")\n")
    
class SExp(Stm):
    def __init__(self, exp, node, datatype):
        Stm.__init__(self, node, datatype)
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "SExp(" + \
              self.exp.pretty(depth+1) + d(depth,")\n")
    
class Jump(Stm):
    def __init__(self,dest, node, datatype):
        Stm.__init__(self, node, datatype)
        self.dest = dest
    def pretty(self, depth=0):
        return d(depth) + "Jump(" + self.dest + d(depth,")\n")
    
class CJump(Stm):
    def __init__(self,op,exp1,exp2,trueDest, falseDest, node, datatype):
        Stm.__init__(self, node, datatype)
        self.op = op
        self.exp1 = exp1
        self.exp2 = exp2
        self.trueDest = trueDest
        self.falseDest = falseDest
        
    def pretty(self, depth=0):
        return d(depth) + "CJump(" + self.op + "\n" + \
               self.exp1.pretty(depth+1) + \
               self.exp2.pretty(depth+1) + \
               self.trueDest.pretty(depth+1) + \
               self.falseDest.pretty(depth+1) + d(depth,")\n")
        
class Seq(Stm):
    def __init__(self,stms, node, datatype):
        Stm.__init__(self, node, datatype)
        self.children = stms
    def pretty(self, depth=0):
        r = d(depth) + "Seq(\n" + self.pretty_children(depth) + d(depth, ")\n")
        return r

class Label(Stm):
    def __init__(self,name, node, datatype):
        Stm.__init__(self, node, datatype)
        self.name = name
    def pretty(self, depth=0):
        r = d(depth) + "Label(" + self.name + ")\n"
