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
        typed_fname = fname + "_"
        for ch in template:
            if ch == "_":
                typed_fname = typed_fname + strOfType(t)[0]
        if stdlib.__dict__.get(typed_fname,None) == None:
            typed_fname = None
        else:
            typed_fname = "stdlib." + typed_fname
        f = "Func(%s,%s)" % (re.sub("_", str(t), template), typed_fname)
        list.append(eval(f))
    return list

class Alias:
    def __init__(self,realName):
        self.realName = realName
        self.pos = -1

def createDefaultDict():
    d = {
        # standard library functions
        
        "sqr": efl("sqr", "[_] , _",  [Int, Float, Complex]),
        "complex" : [ Func([Float, Float], Complex,
                           stdlib.complex_ffc)],
        
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
        "/":  efl("div",   "[_,_] , _", [Float, Complex]) + \
              [ Func([Color, Float], Float, None)],
        "*":  efl("mul",   "[_,_] , _", [Int, Float, Complex]) + \
              [ Func([Color, Float], Float, None)],
        "+":  efl("add",   "[_,_] , _", [Int, Float, Complex, Color]),
        "-":  efl("sub",   "[_,_] , _", [Int, Float, Complex, Color]),
        "^":  efl("pow",   "[_,_] , _", [Float, Complex]),
        "mag":[ Func([Complex], Float, None)],
        
        # unary negation already factored out

        # logical ops
        "&&": [ Func([Bool, Bool], Bool, None) ],
        "||": [ Func([Bool, Bool], Bool, None) ],
        "!" : [ Func([Bool],Bool, None) ],
        
        "#pixel": Alias("pixel"),
        "pixel" : Var(Complex), 
        "#z" : Alias("z"),
        "z"  : Var(Complex), 

        }
    return d


def mangle(k):
    return string.lower(k)
               
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self):
        UserDict.__init__(self)
        self.reset()
        self.nextlabel = 0
        self.nextTemp = 0
        
    def has_key(self,key):
        return self.data.has_key(mangle(key))

    def is_user(self,key):
        val = self.data[mangle(key)]
        if isinstance(val,types.ListType):
            val = val[0]
        return val.pos != -1
    
    def __getitem__(self,key):
        val = self.data[mangle(key)]
        if isinstance(val,Alias):
            key = val.realName
            val = self.data[mangle(key)]            
        return val
    
    def __setitem__(self,key,value):
        k = mangle(key)
        if self.data.has_key(k):
            if T.default_dict.has_key(k):
                msg = "is predefined"
            else:
                l = self.data[k].pos
                msg = ("was already defined on line %d" % l)
            
            raise KeyError, ("symbol '%s' %s" % (key,msg))

        if string.find(k,"t__",0,3)==0:
            raise KeyError, \
                ("symbol '%s': no symbol starting with t__ is allowed" % key)

        self.data[mangle(key)] = value
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = copy.copy(T.default_dict)

    def newLabel(self):
        label = "label%d" % self.nextlabel
        self.nextlabel += 1
        return label

    def newTemp(self,type):
        name = "t__temp%d" % self.nextTemp
        self.nextTemp += 1
        # bypass normal setitem because that checks for t__
        self.data[name] = Var(type) 
        return name
