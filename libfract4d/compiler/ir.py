# Intermediate representation. The Translate module converts an Absyn tree
# into an IR tree.

# this representation copied largely from Appel Chapter 7

import types
import string
import fracttypes
import re

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

class Name(Exp):
    def __init__(self, label, datatype):
        Exp.__init__(self, datatype)
        self.label = label
    
class Temp(Exp):
    def __init__(self, temp, datatype):
        Exp.__init__(self, datatype)
        self.temp = temp
    
class Binop(Exp):
    def __init__(self, op, left, right, datatype):
        Exp.__init__(self, datatype)
        (self.op, self.left, self.right) = (op,left,right)

class Var(Exp):
    def __init__(self, name, datatype):
        Exp.__init__(self,datatype)
        self.name = name
        
class Call(Exp):
    def __init__(self, func, args, datatype):
        Exp.__init__(self,datatype)
        self.func = func
        self.args = args

class ESeq(Exp):
    def __init__(self, stm, exp, datatype):
        Exp.__init__(self, datatype)
        self.stm = stm
        self.exp = exp

# stm and subtypes
# side effects + flow control

class Stm(T):
    def __init__(self, datatype): 
        T.__init__(self, datatype)

class Move(Stm):
    def __init__(self, dest, exp, datatype):
        Stm.__init__(self, datatype)
        self.dest = dest
        sel.exp = exp

class SExp(Stm):
    def __init__(self, exp, datatype):
        Stm.__init__(self, datatype)
        self.exp = exp

class Jump(Stm):
    def __init__(self,dest, datatype):
        Stm.__init__(self,datatype)
        self.dest = dest

class CJump(Stm):
    def __init__(self,op,exp1,exp2,trueDest, falseDest, datatype):
        Stm.__init__(self,datatype)
        self.op = op
        self.exp1 = exp1
        self.exp2 = exp2
        self.trueDest = trueDest
        self.falseDest = falseDest

class Seq(Stm):
    def __init__(self,stms, datatype):
        Stm.__init__(self,datatype)
        self.stms = stms

class Label(Stm):
    def __init__(self,name, datatype):
        Stm.__init__(self,datatype)
        self.name = name

