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
String = 5
Hyper = 6

typeList = [ Bool, Int, Float, Complex, Color, String, Hyper]

suffixOfType = {
    Int : "i",
    Float : "f",
    Complex : "c",
    Bool : "b",
    Color : "C",
    String : "S",
    Hyper : "H"
    }

_typeOfStr = {
    "int" : Int,
    "float" : Float,
    "complex" : Complex,
    "bool" : Bool,
    "color" : Color,
    "string" : String,
    "hyper" : Hyper
    }

_strOfType = {
    Int : "int",
    Float : "float",
    Complex : "complex",
    Bool : "bool",
    Color : "color",
    None : "none",
    String : "string",
    Hyper : "hyper"
   }

_defaultOfType = {
    Int : 0,
    Float : 0.0,
    Complex : [0.0, 0.0],
    Bool : 0,
    Color : [0,0,0,0],
    String : "",
    Hyper : [0.0, 0.0, 0.0, 0.0]
    }

_cTypeOfType = {
    Int : "int",
    Float : "double",
    Complex : "double",
    Hyper : "double",
    Bool : "int",
    Color : "<Error>",
    String : "<Error>"
    }

def typeOfStr(tname):
    if not tname: return None
    return _typeOfStr[string.lower(tname)]

def strOfType(t):
    return _strOfType[t]

def ctype(t):
    return _cTypeOfType[t]

def default_value(t):
    return _defaultOfType[t]

_canBeCast = [
    # rows are from, columns are to
    # Bool Int Float Complex Color String Hyper
    [ 1,   1,  1,    1,      0,    0,     1 ], # Bool
    [ 1,   1,  1,    1,      0,    0,     1 ], # Int
    [ 1,   0,  1,    1,      0,    0,     1 ], # Float
    [ 1,   0,  0,    1,      0,    0,     1 ], # Complex
    [ 0,   0,  0,    0,      1,    0,     0 ], # Color
    [ 0,   0,  0,    0,      0,    1,     0 ], # String
    [ 1,   0,  0,    0,      0,    0,     1 ]
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
    def __init__(self,args,ret,module,fname,pos=-1):
        self.args = args
        self.ret = ret
        self.pos = pos
        self.set_func(module,fname)

    def __copy__(self):
        c = Func(self.args,self.ret,self.module,self.fname,self.pos)
        return c
    
    def first(self):
        return self
        
    def set_func(self,module,fname):
        # compute the name of the stdlib function to call
        # this is sort of equivalent to C++ overload resolution
        if fname == None:
            self.genFunc = None
        else:
            typed_fname = fname + "_"
            for arg in self.args:
                typed_fname = typed_fname + strOfType(arg)[0]
            typed_fname = typed_fname + "_" + strOfType(self.ret)[0]
        
            #print typed_fname
            self.genFunc = module.__dict__.get(typed_fname,typed_fname)
        #print "set name to ", fname
        #if fname == "sin":
        #    import inspect
        #    print inspect.stack()
            
        self.cname = fname
        self.module = module
        self.fname = fname
        
    def matchesArgs(self, potentialArgs):
        if len(potentialArgs) != len(self.args):
            return False
        i = 0
        for arg in self.args:
            if not canBeCast(potentialArgs[i],arg):
                return False
            i = i + 1
        return True 

class Var:
    def __init__(self,type_,value=None,pos=-1,**kwds):
        assert(type_ != None)
        assert(isinstance(pos,types.IntType))
        self.type = type_
        if value == None:
            self.value = default_value(type_)
        else:
            self.value = value
        self.pos = pos
        self.cname = None
        self.is_temp = False
        self.__doc__ = kwds.get("doc")

    def struct_name(self):
        if self.is_temp:
            return "pfo->" + self.cname
        else:
            return self.cname
    
    def first(self):
        return self
        
    def __str__(self):
        return "%s %s (%d)" % (strOfType(self.type), self.value, self.pos)

# a convenient place to put this.
class TranslationError(exceptions.Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return "TranslationError(%s)" % self.msg
    
