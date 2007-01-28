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
Gradient = 7

class Type(object):
    def __init__(self,**kwds):
        self.suffix = kwds["suffix"]
        self.printf = kwds.get("printf") # optional
        self.typename = kwds["typename"]
        self.default = kwds["default"]
        self.slots = kwds.get("slots",1)
        self.cname = kwds["cname"]
        self.typeid = kwds["id"]
        
# these have to be in the indexes given by the constants above
typeObjectList = [
    Type(id=Bool, suffix="b",printf="%d",typename="bool",
         default=0,cname="int"),
    
    Type(id=Int,suffix="i",printf="%d",typename="int",
         default=0,cname="int"),

    Type(id=Float,suffix="f",printf="%g",typename="float",
         default=0.0,cname="double"),

    Type(id=Complex,suffix="c",typename="complex",
         default=[0.0,0.0],slots=2,cname="double"),

    Type(id=Color,suffix="C",typename="color",
         default=[0.0,0.0,0.0,0.0],slots=4, cname="double"),

    Type(id=String,suffix="S",typename="string",
         default="",slots=0,cname="<Error>"),

    Type(id=Hyper,suffix="h",typename="hyper",
         default=[0.0,0.0,0.0,0.0],slots=4,cname="double"),
    
    Type(id=Gradient,suffix="G",typename="gradient",
         default=0,cname="void *")
    ]

typeList = [ Bool, Int, Float, Complex, Color, String, Hyper, Gradient]

suffixOfType = {
    Int : "i",
    Float : "f",
    Complex : "c",
    Bool : "b",
    Color : "C",
    String : "S",
    Hyper : "h",
    Gradient : "G"
    }

_typeOfStr = {
    "int" : Int,
    "float" : Float,
    "complex" : Complex,
    "bool" : Bool,
    "color" : Color,
    "string" : String,
    "hyper" : Hyper,
    "grad" : Gradient
    }

_strOfType = {
    Int : "int",
    Float : "float",
    Complex : "complex",
    Bool : "bool",
    Color : "color",
    None : "none",
    String : "string",
    Hyper : "hyper",
    Gradient : "grad"
   }

_defaultOfType = {
    Int : 0,
    Float : 0.0,
    Complex : [0.0, 0.0],
    Bool : 0,
    Color : [0.0, 0.0, 0.0, 0.0],
    String : "",
    Hyper : [0.0, 0.0, 0.0, 0.0],
    Gradient : 0
    }

_slotsForType = {
    Int: 1,
    Float : 1,
    Complex: 2,
    Bool : 1,
    Color : 4,
    String : 0,
    Hyper: 4,
    Gradient: 1
    }

def typeOfStr(tname):
    if not tname: return None
    return _typeOfStr[string.lower(tname)]

def strOfType(t):
    return _strOfType[t]

def default_value(t):
    return typeObjectList[t].default

def slotsForType(t):
    return _slotsForType[t]

_canBeCast = [
    # rows are from, columns are to
    # Bool Int Float Complex Color String Hyper Gradient 
    [ 1,   1,  1,    1,      0,    0,     1,    0 ], # Bool
    [ 1,   1,  1,    1,      0,    0,     1,    0 ], # Int
    [ 1,   0,  1,    1,      0,    0,     1,    0 ], # Float
    [ 1,   0,  0,    1,      0,    0,     1,    0 ], # Complex
    [ 0,   0,  0,    0,      1,    0,     0,    0 ], # Color
    [ 0,   0,  0,    0,      0,    1,     0,    0 ], # String
    [ 1,   0,  0,    0,      0,    0,     1,    0 ], # Hyper
    [ 0,   0,  0,    0,      0,    0,     0,    1 ]  # Gradient
    ]

def canBeCast(t1,t2):
    ' can t1 be cast to t2?'
    if t1 == None or t2 == None:
        return 0
    return _canBeCast[t1][t2]

# a convenient place to put this.
class TranslationError(exceptions.Exception):
    def __init__(self,msg):
        exceptions.Exception.__init__(self,msg)
        self.msg = msg

class InternalCompilerError(TranslationError):
    def __init__(self,msg):
        TranslationError.__init__("Internal Compiler Error:" + msg)
    
import stdlib

class Func:
    def __init__(self,args,ret,fname,pos=-1):
        self.args = args
        self.ret = ret
        self.pos = pos
        self.set_func(fname)
        
    def __copy__(self):
        c = Func(self.args,self.ret,self.fname,self.pos)
        return c
    
    def first(self):
        return self
        
    def set_func(self,fname):
        # compute the name of the stdlib function to call
        # this is sort of equivalent to C++ overload resolution
        if fname == None:
            self.genFunc = None
        else:
            typed_fname = fname + "_"
            for arg in self.args:
                typed_fname = typed_fname + suffixOfType[arg]
            typed_fname = typed_fname + "_" + suffixOfType[self.ret]
        
            #print typed_fname
            self.genFunc = stdlib.__dict__.get(typed_fname,typed_fname)

        self.cname = fname
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
    def __init__(self,type,value=None,pos=-1,**kwds):
        #assert(type_ != None)
        #assert(isinstance(pos,types.IntType))
        self._set_type(type)
        if value == None:
            self.value = self._typeobj.default
        else:
            self.value = value
        self.pos = pos
        self.cname = None
        self.__doc__ = kwds.get("doc")
        self.declared = False
        self.param_slot = -1
        
    def _get_is_temp(self):
        return False
    is_temp = property(_get_is_temp)

    def _get_type(self):
        return self._typeobj.typeid

    def _set_type(self,t):
        self._typeobj = typeObjectList[t]

    type = property(_get_type, _set_type)

    def _get_ctype(self):
        return self._typeobj.cname

    ctype = property(_get_ctype)
    
    def struct_name(self):
        if self.is_temp:
            return "pfo->" + self.cname
        else:
            return self.cname
    
    def first(self):
        return self
        
    def __str__(self):
        return "%s %s (%d)" % (strOfType(self.type), self.value, self.pos)

    def init_vals(self):
        if self.type == Complex:
            ord = self.param_slot
            if ord == -1:
                re_val = "%.17f" % self.value[0]
                im_val = "%.17f" % self.value[1]
            else:
                re_val = "t__pfo->p[%d].doubleval" % ord
                im_val = "t__pfo->p[%d].doubleval" % (ord+1)
            
            return [re_val,im_val]
        else:
            raise Exception("not done")
        
class Temp(Var):
    def __init__(self,type_,name):
        Var.__init__(self,type_)
        self.cname = name

    def _get_is_temp(self):
        return True

    is_temp = property(_get_is_temp)

