# fract compiler datatypes

import string

Int = 0
Float = 1
Complex = 2
Bool = 3
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
    "color" : Color
    }

def typeOfStr(tname):
    return _typeOfStr[string.lower(tname)]

class Func:
    def __init__(self,ret,pos=-1):
        self.ret = ret
        self.pos = pos

class Var:
    def __init__(self,type,value,pos=-1):
        self.type = type
        self.value = value
        self.pos = pos

