
# datatypes

Int = 0
Float = 1
Complex = 2
Bool = 3
Color = 4

strOfType = {
    Int : "i",
    Float : "f",
    Complex : "c",
    Bool : "b",
    Color : "C"
    }

class Func:
    def __init__(self,ret):
        self.ret = ret

class Var:
    def __init__(self,type,value):
        self.type = type
        self.value = value


