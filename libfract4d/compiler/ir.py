# Intermediate representation. The Translate module converts an Absyn tree
# into an IR tree.

# this representation copied largely from Appel Chapter 7

import types
import string
import fracttypes
import re


def d(depth,s=""):
    return " " * depth + s

class T:
    def __init__(self, datatype):
        self.datatype = datatype
    

# exp and subtypes
# an exp computes a value

class Exp(T):
    def __init__(self, datatype):
        T.__init__(self,datatype)

class Const(Exp):
    def __init__(self, value, datatype):
        Exp.__init__(self, datatype)
        self.value = value
    def pretty(self,depth=0):
        return d(depth) + "Const(%s)\n" % self.value 
    
class Name(Exp):
    def __init__(self, label, datatype):
        Exp.__init__(self, datatype)
        self.label = label
    def pretty(self,depth=0):
        return d(depth) + "Name(" + self.label + ")\n"
    
class Temp(Exp):
    def __init__(self, temp, datatype):
        Exp.__init__(self, datatype)
        self.temp = temp
    def pretty(self, depth=0):
        return d(depth) + "Temp(" + self.temp + ")\n"
    
class Binop(Exp):
    def __init__(self, op, left, right, datatype):
        Exp.__init__(self, datatype)
        (self.op, self.left, self.right) = (op,left,right)
    def pretty(self, depth=0):
        return d(depth) + "Binop(" + self.op + "\n" + \
               left.pretty(depth+1) + \
               right.pretty(depth+1) + d(depth) + ")\n"
    
class Var(Exp):
    def __init__(self, name, datatype):
        Exp.__init__(self,datatype)
        self.name = name
    def pretty(self, depth=0):
        return d(depth) + "Var(" + self.name + ")\n"
    
class Call(Exp):
    def __init__(self, func, args, datatype):
        Exp.__init__(self,datatype)
        self.func = func
        self.args = args
    def pretty(self, depth=0):
        r = d(depth) + "Call(" + self.func + "\n"
        for arg in self.args:
            r += arg.pretty(depth+1)
        r += d(depth,")\n")
        return r
        
class ESeq(Exp):
    def __init__(self, stm, exp, datatype):
        Exp.__init__(self, datatype)
        self.stm = stm
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "ESeq(\n" + \
               self.stm.pretty(depth+1) + self.exp.pretty(depth+1) + \
               d(depth,")\n")
    
# stm and subtypes
# side effects + flow control

class Stm(T):
    def __init__(self, datatype): 
        T.__init__(self, datatype)

class Move(Stm):
    def __init__(self, dest, exp, datatype):
        Stm.__init__(self, datatype)
        self.dest = dest
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "Move(\n" + \
               self.dest.pretty(depth+1) + self.exp.pretty(depth+1) + \
               d(depth,")\n")
    
class SExp(Stm):
    def __init__(self, exp, datatype):
        Stm.__init__(self, datatype)
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "SExp(" + \
              self.exp.pretty(depth+1) + d(depth,")\n")
    
class Jump(Stm):
    def __init__(self,dest, datatype):
        Stm.__init__(self,datatype)
        self.dest = dest
    def pretty(self, depth=0):
        return d(depth) + "Jump(" + self.dest + d(depth,")\n")
    
class CJump(Stm):
    def __init__(self,op,exp1,exp2,trueDest, falseDest, datatype):
        Stm.__init__(self,datatype)
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
    def __init__(self,stms, datatype):
        Stm.__init__(self,datatype)
        self.stms = stms
    def pretty(self, depth=0):
        r = d(depth) + "Seq(\n"
        for stm in self.stms:
            r += stm.pretty(depth+1)
        r += d(depth, ")\n")
        return r

class Label(Stm):
    def __init__(self,name, datatype):
        Stm.__init__(self,datatype)
        self.name = name
    def pretty(self, depth=0):
        r = d(depth) + "Label(" + self.name + ")\n"
