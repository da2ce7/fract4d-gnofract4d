# Intermediate representation. The Translate module converts an Absyn tree
# into an IR tree.

import types
import string
import fracttypes
import re

class T:
    def __init__(self, datatype):
        self.datatype = datatype

class Exp(T):
    def __init__(self, datatype):
        T.__init__(self,datatype)



