# fract compiler datatypes

import string

# order is significant - we use X > Y on types
Bool = 0
Int = 1
Float = 2
Complex = 3

Color = 4

suffixOfType = {
    Int : "i",
    Float : "f",
    Complex : "c",
    Bool : "b",
    Color : "C"
    }

_typeOfStr = {
    "int" : Int,
    "float" : Float,
    "complex" : Complex,
    "bool" : Bool,
    "color" : Color,
    }

_strOfType = {
    Int : "int",
    Float : "float",
    Complex : "complex",
    Bool : "bool",
    Color : "color",
    None : "none"
   }

def typeOfStr(tname):
    return _typeOfStr[string.lower(tname)]

def strOfType(t):
    return _strOfType[t]

def default(t):
    return 0.0

class Func:
    def __init__(self,args,ret,pos=-1):
        self.ret = ret
        self.pos = pos
        self.args = args

class Var:
    def __init__(self,type,value,pos=-1):
        self.type = type
        self.value = value
        self.pos = pos
    def __str__(self):
        return "%s %s (%d)" % (strOfType(self.type), self.value, self.pos)
