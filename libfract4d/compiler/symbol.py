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
        "ident": efl("ident", "[_] , _",  [Int, Float, Complex, Bool]),
        "complex" : [ Func([Float, Float], Complex,
                           stdlib, "complex")],
        "conj" : [ Func([Complex], Complex, stdlib, "conj")],
        "flip" : [ Func([Complex], Complex, stdlib, "flip")],
        "real" : [ Func([Complex], Float, stdlib, "real")],
        "imag" : [ Func([Complex], Float, stdlib, "imag")],
        "recip": efl("recip", "[_] , _", [ Float, Complex]),
        
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
        "^":  efl("pow",   "[_,_] , _", [Float, Complex]),
        "mag":[ Func([Complex], Float, stdlib, "mag")],
        
        # unary negation already factored out

        # logical ops
        "&&": [ Func([Bool, Bool], Bool, stdlib, "booland") ],
        "||": [ Func([Bool, Bool], Bool, stdlib, "boolor") ],
        "!" : [ Func([Bool],Bool, stdlib, "boolnot") ],
        
        "t__h_pixel": Alias("pixel"),
        "pixel" : Var(Complex), 
        "t__h_z" : Alias("z"),
        "z"  : Var(Complex),        
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
        d["t__a_" + name ] = [
            Func([Float],Float, stdlib, name),
            Func([Complex],Complex, stdlib, name) ]
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
    def __init__(self):
        UserDict.__init__(self)
        self.reset()
        self.nextlabel = 0
        self.nextTemp = 0
        
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
            val = self.default_dict.get(k,None)
        if isinstance(val,Alias):
            k = val.realName
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
                  ("symbol '%s': only predefined symbols can begin with '#'" % key)
        
        
        self.data[k] = value
        
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = {} #copy.copy(T.default_dict)

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
