#!/usr/bin/env python
# import Gnofract4d 1.4-1.9 .fct files

import string
import re
import os


class T:
    def __init__(self,compiler):
        # set up defaults
        self.params = [
            0.0, 0.0, 0.0, 0.0, # center
            4.0, # size
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # angles
            ]
        i = 0
        self.bailout = 4.0
        self.funcName = "Mandelbrot"
        self.maxiter = 256
        self.endsect = "[endsection]"
        self.antialias = 1

        # utilities - this fakes a C-style enum
        paramnames = [ "XCENTER", "YCENTER", "ZCENTER", "WCENTER",
                      "MAGNITUDE",
                      "XYANGLE", "XZANGLE", "XWANGLE",
                      "YZANGLE", "YWANGLE", "ZWANGLE"]
        for name in paramnames:
            self.__dict__[name] = i
            i += 1
        
        self.tr = string.maketrans("[]","__")

        # formula support
        self.formula = None
        self.cfuncs = [None,None]
        self.compiler = compiler
        self.outputfile = None
        self.set_inner("gf4d.cfrm","zero")
        self.set_outer("gf4d.cfrm","default")

    def __del__(self):
        if self.outputfile:
            os.remove(self.outputfile)

    def set_formula(self,formulafile,func):
        self.formula = self.compiler.get_formula(formulafile,func)
        if self.formula == None:
            raise ValueError("no such formula: %s:%s" % (formulafile, func))
        
    def set_inner(self,funcfile,func):
        self.cfuncs[0] = self.compiler.get_colorfunc(funcfile,func,"cf0")
        if self.cfuncs[0] == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, func))

    def set_outer(self,funcfile,func):
        self.cfuncs[1] = self.compiler.get_colorfunc(funcfile,func,"cf1")
        if self.cfuncs[1] == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, func))

    def compile(self):
        if self.formula == None:
            raise ValueError("no formula")
        cg = self.compiler.compile(self.formula)
        self.compiler.compile(self.cfuncs[0])
        self.compiler.compile(self.cfuncs[1])

        self.formula.merge(self.cfuncs[0],"cf0_")
        self.formula.merge(self.cfuncs[1],"cf1_")        
        self.outputfile = self.compiler.generate_code(self.formula, cg)
        return self.outputfile

    def parseVal(self,name,val,f,sect=""):
        # try to find a method matching name        
        meth = "parse_" + sect + name.translate(self.tr)
        try:
            self.__class__.__dict__[meth](self,val,f)
        except KeyError:
            #print "ignoring unknown attribute %s" % meth
            pass
        
    def set_param(self,n,val):
        self.params[n] = float(val)

    def parse__function_(self,val,f):
        line = f.readline()
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:
                if name == self.endsect: break
                self.parseVal(name,val,f,"func_")
            line = f.readline()

    def parse_func_function(self,val,f):
        self.funcName = val
        self.set_formula("gf4d.frm",self.funcName)
        
    def parse_x(self,val,f):
        self.set_param(self.XCENTER,val)

    def parse_y(self,val,f):
        self.set_param(self.YCENTER,val)

    def parse_z(self,val,f):
        self.set_param(self.ZCENTER,val)

    def parse_w(self,val,f):
        self.set_param(self.WCENTER,val)

    def parse_size(self,val,f):
        self.set_param(self.MAGNITUDE,val)

    def parse_xy(self,val,f):
        self.set_param(self.XYANGLE,val)

    def parse_xz(self,val,f):
        self.set_param(self.XZANGLE,val)

    def parse_xw(self,val,f):
        self.set_param(self.XWANGLE,val)

    def parse_yz(self,val,f):
        self.set_param(self.YZANGLE,val)

    def parse_yw(self,val,f):
        self.set_param(self.YWANGLE,val)

    def parse_zw(self,val,f):
        self.set_param(self.ZWANGLE,val)

    def parse_bailout(self,val,f):
        self.bailout = float(val)

    def parse_maxiter(self,val,f):
        self.maxiter = int(val)

    def parse_antialias(self,val,f):
        self.antialias = int(val)

    def nameval(self,line):
        x = line.rstrip().split("=",1)
        if len(x) == 0: return (None,None)
        if len(x) < 2:
            val = None
        else:
            val = x[1]
        return (x[0],val)
    
    def loadFctFile(self,f):
        line = f.readline()
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:             
                self.parseVal(name,val,f)
            
            line = f.readline()
