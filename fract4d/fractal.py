#!/usr/bin/env python

import string
import re
import os
import sys
import struct
import math
import copy

import fract4dc
import fracttypes

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

class ParamBag(FctUtils):
    def __init__(self):
        FctUtils.__init__(self)
        self.dict = {}

    def parseVal(self,name,val,f,sect=""):
        self.dict[sect + name] = val

    def load(self,f):
        line = f.readline()
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:
                if name == self.endsect: break
                self.parseVal(name,val,f)
            line = f.readline()

class Colorizer(FctUtils):
    def __init__(self):
        FctUtils.__init__(self)
        self.name = "default"
        self.colorlist = []
        self.solids = [(0,0,0,255)]
        
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

    def parse_red(self,val,f):
        pass

    def parse_green(self,val,f):
        pass

    def parse_blue(self,val,f):
        pass

    def extract_color(self,val,pos,alpha=False):
        cols = [int(val[pos:pos+2],16),
                int(val[pos+2:pos+4],16),
                int(val[pos+4:pos+6],16),
                255]
        if alpha:
            cols[3] = int(val[pos+6:pos+8],16)
        return cols
        
    def parse_colordata(self,val,f):
        nc =len(val)//6
        i = 0
        self.colorlist = []
        while i < nc:
            pos = i*6
            cols = self.extract_color(val,pos)
            if i == 0:
                # first color is inside solid color
                self.solids[0] = tuple(cols)
            else:
                c = tuple([float(i-1)/(nc-2)] + cols)
                self.colorlist.append(c)
            i+= 1

    def parse_solids(self,val,f):
        line = f.readline()
        self.solids = []
        while not line.startswith("]"):
            cols = self.extract_color(line,0,True)            
            self.solids.append(tuple(cols))
            line = f.readline()
        
    def parse_colorlist(self,val,f):
        line = f.readline()
        self.colorlist = []
        while not line.startswith("]"):
            entry = line.split("=")
            
            if len(entry) != 2:
                raise ValueError, "invalid color %s in file" % line

            cols = self.extract_color(entry[1],0,True)            
            index = float(entry[0])
            
            self.colorlist.append(tuple([index] + cols))
            line = f.readline()
            
    def parse_file(self,val,f):
        mapfile = open(val)
        self.parse_map_file(mapfile)

    def parse_map_file(self,mapfile):
        i = 0
        for line in mapfile:
            m = rgb_re.match(line)
            if m != None:
                (r,g,b) = (int(m.group(1)),
                           int(m.group(2)),
                           int(m.group(3)))
 
                if i == 0:
                    # first color is inside solid color
                    self.solids[0] = (r,g,b,255)
                else:
                    self.colorlist.append(((i-1)/255.0,r,g,b,255))
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

        self.format_version = 2.0
        
        # formula support
        self.formula = None
        self.funcName = "Mandelbrot"
        self.bailfunc = 0
        self.cfuncs = [None,None]
        self.cfunc_names = [None,None]
        self.cfunc_files = [None,None]

        self.antialias = 1
        self.compiler = compiler
        self.outputfile = None
        self.funcFile = "gf4d.frm"
        self.set_formula("gf4d.frm",self.funcName)
        self.set_inner("gf4d.cfrm","zero")
        self.set_outer("gf4d.cfrm","default")
        self.dirtyFormula = True # formula needs recompiling
        self.dirty = True # parameters have changed
        self.auto_deepen = True
        
        self.reset()

        # interaction with fract4dc library
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

    def save_cfunc_info(self,index,section,file):
        print >>file, "[%s]" % section
        print >>file, "formulafile=%s" % self.cfunc_files[index]
        print >>file, "function=%s" % self.cfunc_names[index]
        print >>file, "[endsection]"
        
    def save(self,file):
        print >>file, "gnofract4d parameter file"
        print >>file, "version=2.0"

        paramnames = ["x","y","z","w","size","xy","xz","xw","yz","yw","zw"]
        for pair in zip(paramnames,self.params):
            print >>file, "%s=%.17f" % pair

        print >>file, "maxiter=%d" % self.maxiter
        print >>file, "[function]"
        print >>file, "formulafile=%s" % self.funcFile
        print >>file, "function=%s" % self.funcName
        print >>file, "[endsection]"
        
        print >>file, "[initparams]"
        for name in self.func_names():
            print >>file, "%s=%s" % (name, self.get_func_value(name))
        for name in self.formula.symbols.param_names():
            print >>file, "%s=%s" % (name, self.initvalue(name))
        print >>file, "[endsection]"

        self.save_cfunc_info(1,"inner",file)
        self.save_cfunc_info(0,"outer",file)
        
        print >>file, "[colors]"
        print >>file, "colorizer=1"
        print >>file, "solids=["
        for solid in self.solids:
            print >>file, "%02x%02x%02x%02x" % solid
        print >>file, "]"
        
        print >>file, "colorlist=["
        for col in self.colorlist:
            print >>file, "%f=%02x%02x%02x%02x" % col
        print >>file, "]"
        
    def initvalue(self,name):
        ord = self.order_of_name(name)
        type = self.formula.symbols[name].type
        
        if type == fracttypes.Complex:
            return "(%.17f,%.17f)"%(self.initparams[ord],self.initparams[ord+1])
        else:
            return "%.17f" % self.initparams[ord]

    def parse__inner_(self,val,f):
        params = ParamBag()
        params.load(f)
        self.set_inner(params.dict["formulafile"],params.dict["function"])

    def parse__outer_(self,val,f):
        params = ParamBag()
        params.load(f)
        self.set_outer(params.dict["formulafile"],params.dict["function"])

    def parse__initparams_(self,val,f):
        params = ParamBag()
        params.load(f)
        for (name,val) in params.dict.items():
            self.set_named_item(name,val)

    def set_named_item(self,name,val):
        sym = self.formula.symbols[name].first()
        if isinstance(sym, fracttypes.Func):
            self.set_named_func(name,val)
        else:
            self.set_named_param(name,val)
        
    def __del__(self):
        if self.outputfile:
            os.remove(self.outputfile)

    def __copy__(self):
        # override shallow-copy to do a deeper copy than normal,
        # but still don't try and copy *everything*

        c = T(self.compiler,self.site)
        c.params = copy.copy(self.params)
        
        c.set_formula(self.funcFile,self.funcName)
        # copy the function overrides
        for name in self.func_names():
            c.set_named_func(name,self.get_func_value(name))

        c.initparams = copy.copy(self.initparams) # must be after set_formula
        c.bailfunc = self.bailfunc
        c.cfuncs = copy.copy(self.cfuncs)
        c.cfunc_names = copy.copy(self.cfunc_names)
        c.cfunc_files = copy.copy(self.cfunc_files)
        c.colorlist = copy.copy(self.colorlist)
        c.solids = copy.copy(self.solids)
        return c
    
    def reset(self):
        # set global default values, then override from formula
        # set up defaults
        self.params = [
            0.0, 0.0, 0.0, 0.0, # center
            4.0, # size
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # angles
            ]
        self.initparams = []

        self.bailout = 0.0
        self.maxiter = 256
        self.rot_by = math.pi/2
        self.title = self.funcName
        
        self.set_formula_defaults()

    def set_cmap(self,mapfile):
        c = Colorizer()
        file = open(mapfile)
        c.parse_map_file(file)
        self.colorlist = c.colorlist
        self.solids[0:len(c.solids)] = c.solids[:]
        self.changed()
        
    def set_initparam(self,n,val):
        val = float(val)
        if self.initparams[n] != val:
            self.initparams[n] = val
            self.changed()

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

        self.funcName = func
        self.funcFile = formulafile
        self.initparams = self.formula.symbols.default_params()
        
        self.set_bailfunc()
        self.dirtyFormula = True
        self.changed()
        
    def set_bailfunc(self):        
        bailfuncs = [
            "cmag", "manhattanish","manhattanish2",
            "max2","min2",
            "real2","imag2",
            None # bailout
            ]
        funcname = bailfuncs[self.bailfunc]
        if funcname == None:
            # FIXME deal with diff
            return

        func = self.formula.symbols.get("@bailfunc")
        if func != None:
            self.set_func(func[0],funcname)            

    def func_names(self):
        return self.formula.symbols.func_names()

    def param_names(self):
        return self.formula.symbols.param_names()
    
    def set_named_func(self,func_to_set,val):
        fname = self.formula.symbols.demangle(func_to_set)
        func = self.formula.symbols.get(fname)
        self.set_func(func[0],val)            

    def get_func_value(self,func_to_get):
        fname = self.formula.symbols.demangle(func_to_get)        
        func = self.formula.symbols.get(fname)
        return func[0].cname
    
    def changed(self):
        self.dirty = True
        
    def set_func(self,func,fname):
        if func.cname != fname:
            self.formula.symbols.set_std_func(func,fname)
            self.dirtyFormula = True            
            self.changed()
        
    def set_inner(self,funcfile,funcname):
        self.set_colorfunc(1,funcfile,funcname)

    def set_colorfunc(self,index,funcfile,funcname):
        func = self.compiler.get_colorfunc(funcfile,funcname,"cf%d" % index)
        if func == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, funcname))
        self.cfuncs[index] = func
        self.cfunc_files[index] = funcfile
        self.cfunc_names[index] = funcname

        self.dirtyFormula = True
        self.changed()
        
    def set_outer(self,funcfile,funcname):
        self.set_colorfunc(0,funcfile,funcname)
        
    def compile(self):
        if self.formula == None:
            raise ValueError("no formula")
        if self.dirtyFormula == False:
            return self.outputfile

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

        self.dirtyFormula = False
        return self.outputfile

    def mul_vs(self,v,s):
        return map(lambda x : x * s, v)
    
    def relocate(self,dx,dy,zoom):
        if dx == 0 and dy == 0 and zoom == 1.0:
            return
        
        m = fract4dc.rot_matrix(self.params)

        deltax = self.mul_vs(m[0],dx)        
        deltay = self.mul_vs(m[1],dy)

        #print "dx: %s dy: %s" % (deltax,deltay)
        
        self.params[self.XCENTER] += deltax[0] + deltay[0]
        self.params[self.YCENTER] += deltax[1] + deltay[1]
        self.params[self.ZCENTER] += deltax[2] + deltay[2]
        self.params[self.WCENTER] += deltax[3] + deltay[3]
        self.params[self.MAGNITUDE] *= zoom
        self.changed()
        
    def flip_to_julia(self):
        self.params[self.XZANGLE] += self.rot_by
        self.params[self.YWANGLE] += self.rot_by
        self.rot_by = - self.rot_by
        self.changed()
        
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

    def tolerance(self,w,h):
        #5% of the size of a pixel
        return self.params[self.MAGNITUDE]/(20.0 * max(w,h))

    def draw(self,image):
        handle = fract4dc.pf_load(self.outputfile)
        pfunc = fract4dc.pf_create(handle)
        cmap = fract4dc.cmap_create(self.colorlist)
        (r,g,b,a) = self.solids[0]
        fract4dc.cmap_set_solid(cmap,0,r,g,b,a)

        fract4dc.pf_init(pfunc,1.0E-9,self.initparams)

        #print "draw aa: %d %d %d" % (self.antialias,self.maxiter,threads)
        fract4dc.calc(self.params,self.antialias,self.maxiter,1,
                     pfunc,cmap,self.auto_deepen,image,self.site)

    def clean(self):
        self.dirty = False
        
    def set_param(self,n,val):
        val = float(val)
        if self.params[n] != val:
            self.params[n] = val
            self.changed()

    def get_param(self,n):
        return self.params[n]
    
    def parse_gnofract4d_parameter_file(self,val,f):
        pass

    def parse_version(self,val,f):
        self.format_version=float(val)
    
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

        t = self.formula.symbols[name].type 
        if t == fracttypes.Complex:
            m = cmplx_re.match(val)
            if m != None:
                re = float(m.group(1)); im = float(m.group(2))
                if self.initparams[ord] != re:
                    self.initparams[ord] = re
                    self.changed()
                if self.initparams[ord+1] != im:                
                    self.initparams[ord+1] = im
                    self.changed()
        elif t == fracttypes.Float:
            self.initparams[ord] = float(val)
        
    def parse_func_a(self,val,f):
        self.set_named_param("@a",val)

    def parse_func_b(self,val,f):
        self.set_named_param("@b",val)

    def parse_func_c(self,val,f):
        self.set_named_param("@c",val)

    def parse_bailfunc(self,val,f):
        # can't set function directly because formula hasn't been parsed yet
        self.bailfunc = int(val)

    def parse__colors_(self,val,f):
        cf = Colorizer()
        cf.load(f)        
        self.colorlist = cf.colorlist
        self.solids[0:len(cf.solids)] = cf.solids[:]
        self.changed()
        
    def parse__colorizer_(self,val,f):
        which_cf = int(val)
        cf = Colorizer()
        cf.load(f)        
        if which_cf == 0:
            self.colorlist = cf.colorlist
            self.solids[0:len(cf.solids)] = cf.solids[:]
            self.changed()
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
        # antialias now a user pref, not saved in file
        #self.antialias = int(val)
        pass

    def order_of_name(self,name):
        op = self.formula.symbols.order_of_params()
        ord = op.get(self.formula.symbols.realName(name))
        return ord
    
    def fix_bailout(self):
        # because bailout occurs before we know which function this is
        # in older files, we save it in self.bailout then apply to the
        # initparams later
        if self.bailout != 0.0:
            ord = self.order_of_name("@bailout")
            if ord == None:
                # no bailout value for this function
                return
            self.initparams[ord] = self.bailout
            
    def loadFctFile(self,f):
        line = f.readline()
        if line == None or not line.startswith("gnofract4d parameter file"):
            raise Exception("Not a valid parameter file")
        while line != "":
            (name,val) = self.nameval(line)
            if name != None:             
                self.parseVal(name,val,f)
            
            line = f.readline()
        self.fix_bailout()
        
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
        image = fract4dc.image_create(64,48)
        f.draw(image)
        fract4dc.image_save(image,os.path.basename(arg) + ".tga")
        
