#!/usr/bin/env python

# Trivial symbol table implementation

import copy
from UserDict import UserDict
from UserList import UserList
import string
import types
import re
import math

from fracttypes import *
import stdlib

class OverloadList(UserList):
    def __init__(self,list,**kwds):
        UserList.__init__(self,list)
        self.pos = -1
        self._is_operator = kwds.get("operator")
        self.__doc__ = kwds.get("doc")
        
    def first(self):
        return self[0]

    def is_operator(self):
        return self._is_operator
    
def efl(fname, template, tlist,**kwds):
    'short-hand for expandFuncList - just reduces the amount of finger-typing'
    list = []
    for t in tlist:            
        f = "Func(%s,stdlib,\"%s\")" % (re.sub("_", str(t), template), fname)
        realf = eval(f)
        list.append(eval(f))
    return OverloadList(list,**kwds)

class Alias:
    def __init__(self,realName):
        self.realName = realName
        self.pos = -1
        self.cname = None

    
def createDefaultDict():
    d = {
        # standard library functions
        
        "sqr": efl("sqr", "[_] , _",  [Int, Float, Complex],
                   doc="Square the argument. sqr(x) is equivalent to x*x."),
        
        "ident": efl("ident", "[_] , _",  [Int, Float, Complex, Bool],
                     doc='''Do nothing. ident(x) is equivalent to x.
                     This function is useless in normal formulas but
                     comes in useful as a value for a function parameter
                     to a formula.'''),
        
        "complex" : OverloadList(
        [ Func([Float, Float], Complex, stdlib, "complex")],
        doc='''Construct a complex number from two real parts.
        complex(a,b) is equivalent to (a,b).'''),
        
        "conj" : OverloadList([ Func([Complex], Complex, stdlib, "conj")],
                              doc="The complex conjugate. conj(a,b) is equivalent to (a,-b)"),
        
        "flip" : OverloadList([ Func([Complex], Complex, stdlib, "flip")]),
        "real" : OverloadList([ Func([Complex], Float, stdlib, "real")]),
        "real2" : OverloadList([ Func([Complex], Float, stdlib, "real2")]),        
        "imag" : OverloadList([ Func([Complex], Float, stdlib, "imag")]),
        "imag2" : OverloadList([ Func([Complex], Float, stdlib, "imag2")]),
        "recip": efl("recip", "[_] , _", [ Float, Complex]),
        "abs" :  efl("abs", "[_], _", [Float, Complex]),
        "cabs":  OverloadList([ Func([Complex], Float, stdlib, "cabs")]),

        "log" :  efl("log",  "[_], _", [Float, Complex]),
        "sqrt" : efl("sqrt", "[_], _", [Float, Complex]),
        "exp" :  efl("exp",  "[_], _", [Float, Complex]),

        "manhattan" : OverloadList([ Func([Complex], Float, stdlib, "manhattan")]),
        "manhattanish" : OverloadList([ Func([Complex], Float, stdlib, "manhattanish")]),
        "manhattanish2" : OverloadList([ Func([Complex], Float, stdlib, "manhattanish2")]),
        "max2" : OverloadList([ Func([Complex], Float, stdlib, "max2")]),
        "min2" : OverloadList([ Func([Complex], Float, stdlib, "min2")]),
        
        "sin" :  efl("sin", "[_], _", [Float, Complex]),
        "cos" :  efl("cos", "[_], _", [Float, Complex]),
        "tan" :  efl("tan", "[_], _", [Float, Complex]),
        "cotan": efl("cotan","[_], _", [Float, Complex]),
        "sinh" :  efl("sinh", "[_], _", [Float, Complex]),
        "cosh" :  efl("cosh", "[_], _", [Float, Complex]),
        "tanh" :  efl("tanh", "[_], _", [Float, Complex]),
        "cotanh": efl("cotanh", "[_], _", [Float, Complex]),
        
        "asin" :  efl("asin", "[_], _", [Float, Complex]),
        "acos" :  efl("acos", "[_], _", [Float, Complex]),
        "atan" :  efl("atan", "[_], _", [Float, Complex]),
        "atan2" :  OverloadList([ Func([Complex], Float, stdlib, "atan2")]),
        "asinh" :  efl("asinh", "[_], _", [Float, Complex]),
        "acosh" :  efl("acosh", "[_], _", [Float, Complex]),
        "atanh" :  efl("atanh", "[_], _", [Float, Complex]),

        # standard operators

        # comparison
        "!=": efl("noteq", "[_,_] , Bool", [Int, Float, Complex, Bool],
                  operator=True,precedence=3,
                  doc="Inequality operator. Compare two values and return true if they are different. The values are converted to the same type first if necessary."
                  ),
        "==": efl("eq",    "[_,_] , Bool", [Int, Float, Complex, Bool]),
        
        # fixme - issue a warning for complex compares
        ">":  efl("gt",    "[_,_] , Bool", [Int, Float, Complex]),
        ">=": efl("gte",   "[_,_] , Bool", [Int, Float, Complex]),
        "<":  efl("lt",    "[_,_] , Bool", [Int, Float, Complex]),
        "<=": efl("lte",   "[_,_] , Bool", [Int, Float, Complex]),

        # arithmetic
        "%":  efl("mod",   "[_,_] , _", [Int, Float],operator=True),

        "/":  OverloadList([
                Func([Float, Float], Float, stdlib, "div"),
                Func([Complex, Float], Complex, stdlib, "div"),
                Func([Complex, Complex], Complex, stdlib, "div"),
                #Func([Color, Float], Float, stdlib, "div")
                ],operator=True),

        "*":  efl("mul",   "[_,_] , _", [Int, Float, Complex]), #+ \
              #[ Func([Color, Float], Float, stdlib, "mul")],

        "+":  efl("add",   "[_,_] , _", [Int, Float, Complex, Color]),
        "-":  efl("sub",   "[_,_] , _", [Int, Float, Complex, Color]),

        "^": OverloadList([ Func([Float, Float], Float, stdlib, "pow"),
                Func([Complex, Float], Complex, stdlib, "pow"),
                Func([Complex, Complex], Complex, stdlib, "pow")]),
        
        "cmag": OverloadList([ Func([Complex], Float, stdlib, "cmag")]),
        "t__neg": efl("neg", "[_], _", [Int, Float, Complex]),
        
        # un,ary negation already factored out

        # logical ops
        "&&": OverloadList([ Func([Bool, Bool], Bool, stdlib, None) ]),
        "||": OverloadList([ Func([Bool, Bool], Bool, stdlib, None) ]),
        "!" : OverloadList([ Func([Bool],Bool, stdlib, None) ]),

        # predefined magic variables
        "t__h_pixel": Alias("pixel"),
        "pixel" : Var(Complex,doc="The (Z,W) coordinates of the current point."), 
        "t__h_z" : Alias("z"),
        "z"  : Var(Complex),
        "t__h_index": Var(Float),
        "t__h_numiter": Var(Int),
        "t__h_maxiter": Alias("maxiter"),
        "maxiter" : Var(Int),
        "t__h_pi" : Var(Float,math.pi),
        "t__h_tolerance" : Var(Float)
        }
    
    # predefined parameters
    for f in xrange(1,7):
        name = "p%d" % f
        d[name] = Alias("t__a_" + name)
        d["t__a_" + name]  = Var(Complex)
    # predefined functions
    for f in xrange(1,5):
        name = "fn%d" % f
        d[name] = Alias("t__a_" + name)
        d["t__a_" + name ] = OverloadList([Func([Complex],Complex, stdlib, "ident") ])

    for (k,v) in d.items():
        if hasattr(v,"cname") and v.cname == None:
            v.cname = k
            
    return d


def mangle(k):
    l = string.lower(k)
    if l[0] == '#':
        l = "t__h_" + l[1:]
    elif l[0] == '@':
        l = "t__a_" + l[1:]
    return l
               
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self,prefix=""):
        UserDict.__init__(self)
        self.reset()
        self.nextlabel = 0
        self.nextTemp = 0
        self.prefix = prefix

    def merge(self,other):
        # self = union(self,other)
        # any clashes are won by self
        for k in other.data.keys():
            if self.data.get(k) == None:
                self.data[k] = other.data[k]
            elif hasattr(self.data[k],"cname") and \
                 hasattr(other.data[k],"cname") and \
                 self.data[k].cname != other.data[k].cname:
                    # FIXME can cause new clashes
                    self.data[other.prefix + k] = other.data[k]
                
    def has_key(self,key):
        if self.data.has_key(mangle(key)):
            return True        
        return self.default_dict.has_key(mangle(key))

    def is_user(self,key):
        val = self.data.get(mangle(key),None)
        if val == None:
            val = self.default_dict.get(mangle(key))
        return val.pos != -1

    def is_param(self,key):
        return key[0:5] == 't__a_'

    def is_private(self,key):
        return key[0:3] == "t__"
    
    def realName(self,key):
        ' returns mangled key even if var not present for test purposes'
        k = mangle(key)
        val = self.data.get(k,None)
        if val == None:
            val = self.default_dict.get(k)
        if isinstance(val,Alias):
            val = self.default_dict.get(val.realName)
        if val != None:
            if val.cname == None:
                #print k
                raise Exception("argh" + k)
            return val.cname
        return k
    
    def __getitem__(self,key):
        val = self.data.get(mangle(key),None)
        if val == None:
            val = self.default_dict[mangle(key)]
            if isinstance(val,Alias):
                key = val.realName
                val = self.default_dict[mangle(key)]
            self.data[mangle(key)] = val
            
        return val
    
    def __setitem__(self,key,value):
        k = mangle(key)
        if self.data.has_key(k):
            l = self.data[k].pos
            msg = ("was already defined on line %d" % l)
            raise KeyError, ("symbol '%s' %s" % (key,msg))
        elif T.default_dict.has_key(k):
            msg = "is predefined"
            raise KeyError, ("symbol '%s' %s" % (key,msg))
        elif string.find(k,"t__",0,3)==0 and not key[0]=='@':
            raise KeyError, \
                  ("symbol '%s': no symbol starting with t__ is allowed" % key)
        elif key[0]=='#':
            raise KeyError, \
                  ("symbol '%s': only predefined symbols can begin with '#'" %key)
        self.data[k] = value
        if hasattr(value,"cname") and value.cname == None:
            value.cname=self.prefix + k
        
    def parameters(self,varOnly=False):
        params = {}
        for (name,sym) in self.data.items():
            if self.is_param(name):
                if not varOnly or isinstance(sym,Var):
                    params[name] = sym.first()

        return params

    def demangle(self,name):
        # remove most obvious mangling.
        # because of case-folding, demangle(mangle(s)) != s
        if name[:3] == "t__":
            name = name[3:]

        if name[:2] == "a_":
            name = "@" + name[2:]
        elif name[:2] == "h_":
            name = "#" + name[2:]
            
        return name
    
    def func_names(self):
        params = self.parameters()

        func_names = []
        for (name,param) in params.items():
            if isinstance(param,Func):
                func_names.append(self.demangle(name))
        return func_names

    def available_param_functions(self,ret,args):
        # a list of all function names which take a complex
        # and return one (for GUI to select a function)
        flist = []
        for (name,func) in self.default_dict.items():
            try:
                for f in func:
                    if f.ret == ret and f.args == args and \
                           not self.is_private(name):
                        flist.append(name)
            except TypeError:
                # wasn't a list
                pass
            
        return flist
    
    def order_of_params(self):
        # a hash which maps param name -> order in input list
        p = self.parameters(True)
        karray = p.keys()
        karray.sort()
        op = {}; i = 0
        for k in karray:
            op[k] = i
            if p[k].type == Complex:
                i += 2
            else:
                i += 1
        op["__SIZE__"]=i

        return op

    def default_params(self):
        op = self.order_of_params()
        defaults = [0.0] * op["__SIZE__"]
        for (k,i) in op.items():
            param = self.get(k,None)
            if not param: continue
            defval = getattr(param,"default",None)
            if not defval: continue
            if param.type == Complex:
                defaults[i] = defval.value[0].value
                defaults[i+1] = defval.value[1].value
            else:
                defaults[i] = defval.value
        return defaults

    def set_std_func(self,func,fname):
        # repoint parameter @func to use fname next time we compile
        func.set_func(stdlib,fname)
        
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = {} 

    def newLabel(self):
        label = "%slabel%d" % (self.prefix, self.nextlabel)
        self.nextlabel += 1
        return label

    def newTemp(self,type):
        name = "t__%stemp%d" % (self.prefix, self.nextTemp)
        self.nextTemp += 1
        # bypass normal setitem because that checks for t__
        v = Var(type)
        v.cname = name
        self.data[name] = v
        
        return name
