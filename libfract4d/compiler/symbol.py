#!/usr/bin/env python

# Trivial symbol table implementation
from fracttypes import *
import copy
from UserDict import UserDict
import string

def createDefaultDict():
    d = {
        "sqr_i": Func(Int),
        "sqr_f": Func(Float),
        "sqr_c": Func(Complex)
        }
    return d


def mangle((name,types)):
    s = string.lower(name) + "_"
    for t in types:
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
        self.data[mangle(key)] = value
    def __delitem__(self,key):
        del self.data[mangle(key)]


