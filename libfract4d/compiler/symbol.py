#!/usr/bin/env python

# Trivial symbol table implementation
from fracttypes import *
import copy
from UserDict import UserDict
import string
import types

def createDefaultDict():
    d = {
        "sqr": [ Func([Int],Int),
                 Func([Float], Float),
                 Func([Complex], Complex)],
        "#pixel": Var(Complex,0.0), # fixme, value 
        "#z" : Var(Complex,0.0),
        "z"  : Var(Complex,0.0) # same as #z
        }
    return d


def mangle(k):
    return string.lower(k)
               
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self):
        UserDict.__init__(self)
        self.reset()

    def has_key(self,key):
        return self.data.has_key(mangle(key))

    def is_user(self,key):
        return not self.data[mangle(key)].pos == -1
    
    def __getitem__(self,key):
        return self.data[mangle(key)]
    def __setitem__(self,key,value):
        k = mangle(key)
        if self.data.has_key(k):
            if T.default_dict.has_key(k):
                msg = "is predefined"
            else:
                l = self.data[k].pos
                msg = ("was already defined on line %d" % l)
            
            raise KeyError, ("symbol '%s' %s" % (key,msg))

        self.data[mangle(key)] = value
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = copy.deepcopy(T.default_dict)

