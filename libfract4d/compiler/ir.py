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


