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
        "sqr_c": Func(Complex)
        }
    return d


def mangle(k):
    if isinstance(k,types.StringType):
        return string.lower(k)
    
    s = string.lower(k[0]) + "_"
    for t in k[1]:
        s += strOfType[t]
    return s
           
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self):
        UserDict.__init__(self)
        self.data = copy.deepcopy(T.default_dict)
    def __getitem__(self,key):
        return self.data[mangle(key)]
    def __setitem__(self,key,value):
        k = mangle(key)
        if self.data.has_key(k):
            raise KeyError, ("can't override existing key %s" % k)
        self.data[mangle(key)] = value
    def __delitem__(self,key):
        del self.data[mangle(key)]


