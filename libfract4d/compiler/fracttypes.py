# fract compiler datatypes

import string
import exceptions
import types

# order is significant - we use X > Y on types
Bool = 0
Int = 1
Float = 2
Complex = 3
Color = 4

typeList = [ Bool, Int, Float, Complex, Color]

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

_defaultOfType = {
    Int : 0,
    Float : 0.0,
    Complex : [0.0, 0.0],
    Bool : 0,
    Color : [0,0,0,0]
    }

_cTypeOfType = {
    Int : "int",
    Float : "double",
    Complex : "double",
    Bool : "int",
    Color : "<Error>"
    }

def typeOfStr(tname):
    return _typeOfStr[string.lower(tname)]

def strOfType(t):
    return _strOfType[t]

def ctype(t):
    return _cTypeOfType[t]

def default_value(t):
    return _defaultOfType[t]

_canBeCast = [
    # Bool Int Float Complex Color
    [ 1,   1,  1,    1,      0], # Bool
    [ 1,   1,  1,    1,      0], # Int
    [ 1,   0,  1,    1,      0], # Float
    [ 1,   0,  0,    1,      0], # Complex
    [ 0,   0,  0,    0,      1]  # Color
    ]

def canBeCast(t1,t2):
    ' can t1 be cast to t2?'
    if t1 == None or t2 == None:
        return 0
    try:
        return _canBeCast[t1][t2]
    except Exception, e:
        #print t1,t2
        raise
    
class Func:
    def __init__(self,args,ret,codegen,pos=-1):
        self.ret = ret
        self.pos = pos
        self.args = args
        self.codegen = codegen
        
    def matchesArgs(self, potentialArgs):
        if len(potentialArgs) != len(self.args):
            return 0
        i = 0
        for arg in self.args:
            if not canBeCast(potentialArgs[i],arg):
                return 0
            i = i + 1
        return 1            

class Var:
    def __init__(self,type_,value=None,pos=-1):
        assert(type_ != None)
        assert(isinstance(pos,types.IntType))
        self.type = type_
        if value == None:
            self.value = default_value(type_)
        else:
            self.value = value
        self.pos = pos
    def __str__(self):
        return "%s %s (%d)" % (strOfType(self.type), self.value, self.pos)

# a convenient place to put this.
class TranslationError(exceptions.Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return "TranslationError(%s)" % self.msg
    
