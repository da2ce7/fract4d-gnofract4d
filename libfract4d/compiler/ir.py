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
    def __init__(self, pos, datatype):
        self.datatype = datatype
        self.pos = pos

# exp and subtypes
# an exp computes a value

class Exp(T):
    def __init__(self, pos, datatype):
        T.__init__(self, pos, datatype)

class Const(Exp):
    def __init__(self, value, pos, datatype):
        Exp.__init__(self, pos, datatype)
        self.value = value
    def pretty(self,depth=0):
        return d(depth) + "Const(%s)\n" % self.value 
    
class Name(Exp):
    def __init__(self, label, pos, datatype):
        Exp.__init__(self, pos, datatype)
        self.label = label
    def pretty(self,depth=0):
        return d(depth) + "Name(" + self.label + ")\n"
    
class Temp(Exp):
    def __init__(self, temp, pos, datatype):
        Exp.__init__(self, pos, datatype)
        self.temp = temp
    def pretty(self, depth=0):
        return d(depth) + "Temp(" + self.temp + ")\n"
    
class Binop(Exp):
    def __init__(self, op, left, right, pos, datatype):
        Exp.__init__(self, pos, datatype)
        (self.op, self.left, self.right) = (op,left,right)
    def pretty(self, depth=0):
        return d(depth) + "Binop(" + self.op + "\n" + \
               left.pretty(depth+1) + \
               right.pretty(depth+1) + d(depth) + ")\n"
    
class Var(Exp):
    def __init__(self, name, pos, datatype):
        Exp.__init__(self, pos, datatype)
        self.name = name
    def pretty(self, depth=0):
        return d(depth) + "Var(" + self.name + ")\n"

class Real(Exp):
    def __init__(self, cexp, pos):
        Exp.__init__(self,pos, fracttypes.Float)
        self.cexp = cexp
    def pretty(self,depth=0):
        return d(depth) + "Real(" + self.cexp.pretty(depth+1) + d(depth,")\n")

class Cast(Exp):
    def __init__(self, exp, pos, datatype):
        Exp.__init__(self,pos, datatype)
        self.exp = exp
    def pretty(self,depth=0):
        return d(depth) + "Cast(" + self.cexp.pretty(depth+1) + d(depth,")\n")
    
class Call(Exp):
    def __init__(self, func, args, pos, datatype):
        Exp.__init__(self, pos, datatype)
        self.func = func
        self.args = args
    def pretty(self, depth=0):
        r = d(depth) + "Call(" + self.func + "\n"
        for arg in self.args:
            r += arg.pretty(depth+1)
        r += d(depth,")\n")
        return r
        
class ESeq(Exp):
    def __init__(self, stm, exp, pos, datatype):
        Exp.__init__(self, pos, datatype)
        self.stm = stm
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "ESeq(\n" + \
               self.stm.pretty(depth+1) + self.exp.pretty(depth+1) + \
               d(depth,")\n")
    
# stm and subtypes
# side effects + flow control

class Stm(T):
    def __init__(self, pos, datatype): 
        T.__init__(self, pos, datatype)

class Move(Stm):
    def __init__(self, dest, exp, pos, datatype):
        Stm.__init__(self, pos, datatype)
        self.dest = dest
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "Move(\n" + \
               self.dest.pretty(depth+1) + self.exp.pretty(depth+1) + \
               d(depth,")\n")
    
class SExp(Stm):
    def __init__(self, exp, pos, datatype):
        Stm.__init__(self, pos, datatype)
        self.exp = exp
    def pretty(self, depth=0):
        return d(depth) + "SExp(" + \
              self.exp.pretty(depth+1) + d(depth,")\n")
    
class Jump(Stm):
    def __init__(self,dest, pos, datatype):
        Stm.__init__(self, pos, datatype)
        self.dest = dest
    def pretty(self, depth=0):
        return d(depth) + "Jump(" + self.dest + d(depth,")\n")
    
class CJump(Stm):
    def __init__(self,op,exp1,exp2,trueDest, falseDest, pos, datatype):
        Stm.__init__(self, pos, datatype)
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
    def __init__(self,stms, pos, datatype):
        Stm.__init__(self, pos, datatype)
        self.stms = stms
    def pretty(self, depth=0):
        r = d(depth) + "Seq(\n"
        for stm in self.stms:
            r += stm.pretty(depth+1)
        r += d(depth, ")\n")
        return r

class Label(Stm):
    def __init__(self,name, pos, datatype):
        Stm.__init__(self, pos, datatype)
        self.name = name
    def pretty(self, depth=0):
        r = d(depth) + "Label(" + self.name + ")\n"
