#!/usr/bin/env python

# Trivial symbol table implementation
from fracttypes import *
import copy
from UserDict import UserDict
import string
import types

def createDefaultDict():
    d = {
        "sqr_i": Func(Int),
        "sqr_f": Func(Float),
        "sqr_c": Func(Complex),
        "#pixel": Var(Complex,0.0), # fixme, value 
        "#z" : Var(Complex,0.0),
        "z"  : Var(Complex,0.0) # same as #z
        }
    return d


def mangle(k):
    if isinstance(k,types.StringType):
        return string.lower(k)
    
    s = string.lower(k[0]) + "_"
    for t in k[1]:
        s += suffixOfType[t]
    return s
           
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self):
        UserDict.__init__(self)
        self.reset()
        
    def __getitem__(self,key):
        return self.data[mangle(key)]
    def __setitem__(self,key,value):
        k = mangle(key)
        if self.data.has_key(k):
            l = self.data[k].pos
            if l==-1:
                msg = "is predefined"
            else:
                msg = ("already defined on line %d" % l)
            
            raise KeyError, ("symbol %s %s" % (k,msg))

        self.data[mangle(key)] = value
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = copy.deepcopy(T.default_dict)

