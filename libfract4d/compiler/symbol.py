#!/usr/bin/env python

# Trivial symbol table implementation
from fracttypes import *
import copy
from UserDict import UserDict
import string
import types
import re
import stdlib

def efl(fname, template, tlist):
    'short-hand for expandFuncList - just reduces the amount of finger-typing'
    list = []
    for t in tlist:            
        f = "Func(%s,stdlib,\"%s\")" % (re.sub("_", str(t), template), fname)
        realf = eval(f)
        list.append(eval(f))
    return list

class Alias:
    def __init__(self,realName):
        self.realName = realName
        self.pos = -1
        self.cname = None
        
def createDefaultDict():
    d = {
        # standard library functions
        
        "sqr": efl("sqr", "[_] , _",  [Int, Float, Complex]),
        "ident": efl("ident", "[_] , _",  [Int, Float, Complex, Bool]),
        "complex" : [ Func([Float, Float], Complex,
                           stdlib, "complex")],
        "conj" : [ Func([Complex], Complex, stdlib, "conj")],
        "flip" : [ Func([Complex], Complex, stdlib, "flip")],
        "real" : [ Func([Complex], Float, stdlib, "real")],
        "imag" : [ Func([Complex], Float, stdlib, "imag")],
        "recip": efl("recip", "[_] , _", [ Float, Complex]),
        "abs" :  efl("abs", "[_], _", [Float, Complex]),
        "cabs":  [ Func([Complex], Float, stdlib, "cabs")],

        "log" :  efl("log",  "[_], _", [Float, Complex]),
        "sqrt" : efl("sqrt", "[_], _", [Float, Complex]),
        "exp" :  efl("exp",  "[_], _", [Float, Complex]),
        
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
        "atan2" :  [ Func([Complex], Float, stdlib, "atan2")],
        "asinh" :  efl("asinh", "[_], _", [Float, Complex]),
        "acosh" :  efl("acosh", "[_], _", [Float, Complex]),
        "atanh" :  efl("atanh", "[_], _", [Float, Complex]),

        # standard operators

        # comparison
        "!=": efl("noteq", "[_,_] , Bool", [Int, Float, Complex, Bool]),
        "==": efl("eq",    "[_,_] , Bool", [Int, Float, Complex, Bool]),
        
        # fixme - issue a warning for complex compares
        ">":  efl("gt",    "[_,_] , Bool", [Int, Float, Complex]),
        ">=": efl("gte",   "[_,_] , Bool", [Int, Float, Complex]),
        "<":  efl("lt",    "[_,_] , Bool", [Int, Float, Complex]),
        "<=": efl("lte",   "[_,_] , Bool", [Int, Float, Complex]),

        # arithmetic
        "%":  efl("mod",   "[_,_] , _", [Int, Float]),

        "/":  [ Func([Float, Float], Float, stdlib, "div"),
                Func([Complex, Float], Complex, stdlib, "div"),
                Func([Complex, Complex], Complex, stdlib, "div"),
                Func([Color, Float], Float, stdlib, "div")],

        "*":  efl("mul",   "[_,_] , _", [Int, Float, Complex]) + \
              [ Func([Color, Float], Float, stdlib, "mul")],

        "+":  efl("add",   "[_,_] , _", [Int, Float, Complex, Color]),
        "-":  efl("sub",   "[_,_] , _", [Int, Float, Complex, Color]),

        "^":  [ Func([Float, Float], Float, stdlib, "pow"),
                Func([Complex, Float], Complex, stdlib, "pow"),
                Func([Complex, Complex], Complex, stdlib, "pow")],
        
        "t__mag":[ Func([Complex], Float, stdlib, "mag")],
        "t__neg": efl("neg", "[_], _", [Int, Float, Complex]),
        
        # unary negation already factored out

        # logical ops
        "&&": [ Func([Bool, Bool], Bool, stdlib, "booland") ],
        "||": [ Func([Bool, Bool], Bool, stdlib, "boolor") ],
        "!" : [ Func([Bool],Bool, stdlib, "boolnot") ],
        
        "t__h_pixel": Alias("pixel"),
        "pixel" : Var(Complex), 
        "t__h_z" : Alias("z"),
        "z"  : Var(Complex),
        "t__h_index": Var(Float),
        "t__h_numiter": Var(Int)
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
        d["t__a_" + name ] = [Func([Complex],Complex, stdlib, "ident") ]

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
        if isinstance(val,types.ListType):
            val = val[0]
        return val.pos != -1

    def is_param(self,key):
        return key[0:5] == 't__a_'
            
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
                    params[name] = sym
        return params

    def order_of_params(self):
        # a hash which maps param name -> order in input list
        p = self.parameters(True)
        karray = p.keys()
        karray.sort()
        op = {}; i = 0
        for k in karray:
            op[k] = i
            i = i + 1
        return op
            
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
