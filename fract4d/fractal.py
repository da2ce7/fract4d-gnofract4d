#!/usr/bin/env python
# import Gnofract4d 1.4-1.9 .fct files

import string
import re
import os
import sys
import struct
import math

import fract4dc

#typedef enum
#
#   BAILOUT_MAG = 0,
#   BAILOUT_MANH,
#   BAILOUT_MANH2,
#   BAILOUT_OR,
#   BAILOUT_AND,
#   BAILOUT_REAL,
#   BAILOUT_IMAG,
#   BAILOUT_DIFF
# e_bailFunc;

rgb_re = re.compile(r'\s*(\d+)\s+(\d+)\s+(\d+)')
cmplx_re = re.compile(r'\((.*?),(.*?)\)')

# generally useful funcs for reading in .fct files
class FctUtils:
    def __init__(self):
        self.endsect = "[endsection]"
        self.tr = string.maketrans("[] ","___")
        
    def parseVal(self,name,val,f,sect=""):
        # try to find a method matching name        
        methname = "parse_" + sect + name.translate(self.tr)
        meth = None
        try:
            meth = eval("self.%s" % methname)
        except Exception:
            print "ignoring unknown attribute %s" % methname

        if meth:
            return meth(val,f)

    def nameval(self,line):
        x = line.rstrip().split("=",1)
        if len(x) == 0: return (None,None)
        if len(x) < 2:
            val = None
        else:
            val = x[1]
        return (x[0],val)

class Colorizer(FctUtils):
    def __init__(self):
        FctUtils.__init__(self)
        self.name = "default"
        self.colorlist = []
        self.solid = (0,0,0,255)
        
    def load(self,f):
        line = f.readline()
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:
                if name == self.endsect: break
                self.parseVal(name,val,f)
            line = f.readline()

    def parse_colorizer(self,val,f):
        t = int(val)
        if t == 0:
            # FIXME
            #raise ValueError("Sorry, color ranges not currently supported")
            pass
        elif t == 1:
            pass
        else:
            raise ValueError("Unknown colorizer type %d" % t)
        
    def parse_colordata(self,val,f):
        nc =len(val)//6
        i = 0
        self.colorlist = []
        while i < nc:
            pos = i*6
            (r,g,b) = (int(val[pos:pos+2],16),
                       int(val[pos+2:pos+4],16),
                       int(val[pos+4:pos+6],16))
            if i == 0:
                # first color is inside solid color
                self.solid = (r,g,b,255)
            else:
                c = (float(i-1)/(nc-2),r,g,b,255)
                self.colorlist.append(c)
            i+= 1
        
    def parse_file(self,val,f):
        mapfile = open(val)
        print mapfile
        i = 0
        for line in mapfile:
            m = rgb_re.match(line)
            if m != None:
                (r,g,b) = (int(m.group(1)),
                           int(m.group(2)),
                           int(m.group(3)))
 
                if i == 0:
                    # first color is inside solid color
                    self.solid = (r,g,b,255)
                else:
                    self.colorlist.append((i-1/255.0,r,g,b,255))
            i += 1

        
class T(FctUtils):
    def __init__(self,compiler,site=None):
        FctUtils.__init__(self)
        
        # utilities - this fakes a C-style enum
        paramnames = ["XCENTER", "YCENTER", "ZCENTER", "WCENTER",
                      "MAGNITUDE",
                      "XYANGLE", "XZANGLE", "XWANGLE",
                      "YZANGLE", "YWANGLE", "ZWANGLE"]
        i = 0
        for name in paramnames:
            self.__dict__[name] = i
            i += 1
        
        # formula support
        self.formula = None
        self.cfuncs = [None,None]
        self.compiler = compiler
        self.outputfile = None
        self.funcFile = "gf4d.frm"
        self.set_formula("gf4d.frm","Mandelbrot")
        self.set_inner("gf4d.cfrm","zero")
        self.set_outer("gf4d.cfrm","default")

        self.reset()

        # interaction with fract4d library
        self.site = site or fract4dc.site_create(self)

        # default is just white outside
        self.colorlist = [
            (1.0, 255, 255, 255, 255)
            ]

        self.solids = [(0,0,0,255),(0,0,0,255)]
        
        # colorfunc lookup
        self.colorfunc_names = [
            "default", 
            "continuous_potential",
            "zero",
            "ejection_distance",
            "decomposition",
            "external_angle"]

    def __del__(self):
        if self.outputfile:
            os.remove(self.outputfile)

    def reset(self):
        # set global default values, then override from formula
        # set up defaults
        self.params = [
            0.0, 0.0, 0.0, 0.0, # center
            4.0, # size
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # angles
            ]
        self.initparams = []

        self.bailout = 4.0
        self.funcName = "Mandelbrot"
        self.maxiter = 256
        self.antialias = 1
        self.rot_by = math.pi/2
        self.title = self.funcName
        
        self.set_formula_defaults()
        
    def set_formula_defaults(self):
        if self.formula == None:
            return

        self.initparams = self.formula.symbols.default_params()
        
        for (name,val) in self.formula.defaults.items():
            # FIXME helpfile,helptopic,method,periodicity,precision,
            #render,skew,stretch
            if name == "maxiter":
                self.maxiter = int(val.value)
            elif name == "center" or name == "xycenter":
                self.params[self.XCENTER] = float(val.value[0].value)
                self.params[self.YCENTER] = float(val.value[1].value)
            elif name == "zwcenter":
                self.params[self.ZCENTER] = float(val.value[0].value)
                self.params[self.WCENTER] = float(val.value[1].value)
            elif name == "angle":
                self.params[self.XYANGLE] = float(val.value)
            elif name == "magn":
                self.params[self.MAGNITUDE] = float(val.value)
            elif name == "title":
                self.title = val.value
            else:
                if hasattr(self,name.upper()):
                    self.params[getattr(self,name.upper())] = float(val.value)
                else:
                    print "ignored unknown parameter %s" % name
        
    def set_formula(self,formulafile,func):
        self.formula = self.compiler.get_formula(formulafile,func)
        if self.formula == None:
            raise ValueError("no such formula: %s:%s" % (formulafile, func))

        self.initparams = self.formula.symbols.default_params()

    def set_inner(self,funcfile,func):
        self.cfuncs[1] = self.compiler.get_colorfunc(funcfile,func,"cf1")
        if self.cfuncs[1] == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, func))

    def set_outer(self,funcfile,func):
        self.cfuncs[0] = self.compiler.get_colorfunc(funcfile,func,"cf0")
        if self.cfuncs[0] == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, func))

    def compile(self):
        if self.formula == None:
            raise ValueError("no formula")
        cg = self.compiler.compile(self.formula)
        self.compiler.compile(self.cfuncs[0])
        self.compiler.compile(self.cfuncs[1])

        self.formula.merge(self.cfuncs[0],"cf0_")        
        self.formula.merge(self.cfuncs[1],"cf1_")        
        outputfile = os.path.abspath(self.compiler.generate_code(self.formula, cg))
        #print "compiled %s" % outputfile
        if outputfile != None:
            if self.outputfile != outputfile:
                self.outputfile = outputfile
                self.handle = fract4dc.pf_load(self.outputfile)
                self.pfunc = fract4dc.pf_create(self.handle)

        return self.outputfile

    def mul_vs(self,v,s):
        return map(lambda x : x * s, v)
    
    def relocate(self,dx,dy,zoom):
        m = fract4dc.rot_matrix(self.params)

        deltax = self.mul_vs(m[0],dx)        
        deltay = self.mul_vs(m[1],dy)

        #print "dx: %s dy: %s" % (deltax,deltay)
        
        self.params[self.XCENTER] += deltax[0] + deltay[0]
        self.params[self.YCENTER] += deltax[1] + deltay[1]
        self.params[self.ZCENTER] += deltax[2] + deltay[2]
        self.params[self.WCENTER] += deltax[3] + deltay[3]
        self.params[self.MAGNITUDE] *= zoom

    def flip_to_julia(self):
        self.params[self.XZANGLE] += self.rot_by
        self.params[self.YWANGLE] += self.rot_by
        self.rot_by = - self.rot_by
        
    # status callbacks
    def status_changed(self,val):
        pass
    
    def progress_changed(self,d):
        pass
    
    def is_interrupted(self):
        return False

    def iters_changed(self,iters):
        #print "iters changed to %d" % iters
        self.maxiter = iters
    
    def image_changed(self,x1,y1,x2,y2):
        pass

    def _pixel_changed(self,params,x,y,aa,maxIters,nNoPeriodIters,dist,fate,nIters,r,g,b,a):
        # remove underscore to debug fractal generation
        print "pixel: (%g,%g,%g,%g) %d %d %d %d %d %g %d %d (%d %d %d %d)" % \
              (params[0],params[1],params[2],params[3],x,y,aa,maxIters,nNoPeriodIters,dist,fate,nIters,r,g,b,a)
                      
    def draw(self,image):
        handle = fract4dc.pf_load(self.outputfile)
        pfunc = fract4dc.pf_create(handle)
        cmap = fract4dc.cmap_create(self.colorlist)
        (r,g,b,a) = self.solids[0]
        fract4dc.cmap_set_solid(cmap,0,r,g,b,a)
        
        fract4dc.pf_init(pfunc,0.001,self.initparams)

        fract4dc.calc(self.params,self.antialias,self.maxiter,1,
                     pfunc,cmap,1,image,self.site)

        
    def set_param(self,n,val):
        self.params[n] = float(val)

    def parse_gnofract4d_parameter_file(self,val,f):
        pass

    def parse_version(self,val,f):
        pass
    
    def parse__function_(self,val,f):
        line = f.readline()
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:
                if name == self.endsect: break
                self.parseVal(name,val,f,"func_")
            line = f.readline()

    def parse_func_formulafile(self,val,f):
        self.funcFile = val
        self.compiler.load_formula_file(self.funcFile)
        
    def parse_func_function(self,val,f):
        self.funcName = val
        self.set_formula(self.funcFile,self.funcName)

    def set_named_param(self,name,val):
        #print "named param %s : %s" % (name, val)
        op = self.formula.symbols.order_of_params()
        ord = op.get(self.formula.symbols.realName(name))
        if ord == None:
            print "Ignoring unknown param %s" % name
            return
        
        m = cmplx_re.match(val)
        if m != None:
            re = float(m.group(1)); im = float(m.group(2))
            self.initparams[ord] = re
            self.initparams[ord+1] = im

    def parse_func_a(self,val,f):
        self.set_named_param("@a",val)

    def parse_func_b(self,val,f):
        self.set_named_param("@b",val)

    def parse_func_c(self,val,f):
        self.set_named_param("@c",val)

    def parse__colors_(self,val,f):
        cf = Colorizer()
        cf.load(f)        
        self.colorlist = cf.colorlist
        self.solids[0] = cf.solid
        
    def parse__colorizer_(self,val,f):
        which_cf = int(val)
        cf = Colorizer()
        cf.load(f)        
        if which_cf == 0:
            self.colorlist = cf.colorlist
            self.solids[0] = cf.solid
        # ignore other colorlists for now

    def parse_inner(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_inner("gf4d.cfrm",name)

    def parse_outer(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_outer("gf4d.cfrm",name)
        
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
    
    def loadFctFile(self,f):
        line = f.readline()
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:             
                self.parseVal(name,val,f)
            
            line = f.readline()
        
if __name__ == '__main__':
    import sys
    import fc
    import fract4dc

    g_comp = fc.Compiler()
    g_comp.load_formula_file("./gf4d.frm")
    g_comp.load_formula_file("test.frm")
    g_comp.load_formula_file("gf4d.cfrm")

    f = T(g_comp)
    for arg in sys.argv[1:]:
        file = open(arg)
        f.loadFctFile(file)
        f.compile()
        image = fract4dc.image_create(640,480)
        f.draw(image)
        fract4dc.image_save(image,os.path.basename(arg) + ".tga")

        
