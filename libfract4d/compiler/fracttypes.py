
# datatypes

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
    def __init__(self,ret):
        self.ret = ret

class Var:
    def __init__(self,type,value):
        self.type = type
        self.value = value


