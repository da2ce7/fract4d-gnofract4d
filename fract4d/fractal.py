#!/usr/bin/env python

import string
import StringIO
import re
import os
import sys
import struct
import math
import copy
import random

import fract4dc
import fracttypes
import gradient

rgb_re = re.compile(r'\s*(\d+)\s+(\d+)\s+(\d+)')
cmplx_re = re.compile(r'\((.*?),(.*?)\)')
hyper_re = re.compile(r'\((.*?),(.*?),(.*?),(.*?)\)')

THIS_VERSION=2.8

# generally useful funcs for reading in .fct files
class FctUtils:
    def __init__(self,parent=None):
        self.endsect = "[endsection]"
        self.tr = string.maketrans("[] ","___")
        self.parent = parent
        
    def warn(self,msg):
        if self.parent:
            self.parent.warn(msg)
            
    def parseVal(self,name,val,f,sect=""):
        # try to find a method matching name        
        methname = "parse_" + sect + name.translate(self.tr)
        meth = None
        try:
            klass = self.__class__
            while True:
                meth = klass.__dict__.get(methname)
                if meth != None:
                    break
                bases = klass.__bases__
                if len(bases) > 0:                    
                    klass = bases[0]
                else:
                    break
        except Exception, err:
            print "ignoring unknown attribute %s" % methname
            print err
            
        if meth:
            return meth(self,val,f)

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
    '''Parses the various different kinds of color data we have'''
    def __init__(self,parent=None):
        FctUtils.__init__(self,parent)
        self.name = "default"
        self.gradient = gradient.Gradient()
        self.solids = [(0,0,0,255)]
        self.direct = False
        self.rgb = [0,0,0]
        
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
            # convert to a direct coloring algorithm
            self.direct = True
        elif t == 1:
            pass
        else:
            raise ValueError("Unknown colorizer type %d" % t)

    def parse_red(self,val,f):
        self.rgb[0] = float(val)

    def parse_green(self,val,f):
        self.rgb[1] = float(val)

    def parse_blue(self,val,f):
        self.rgb[2] = float(val)

    def extract_color(self,val,pos,alpha=False):
        cols = [int(val[pos:pos+2],16),
                int(val[pos+2:pos+4],16),
                int(val[pos+4:pos+6],16),
                255]
        if alpha:
            cols[3] = int(val[pos+6:pos+8],16)
        return cols
        
    def parse_colordata(self,val,f):
        'long list of hex digits: gf4d < 2.0'
        nc =len(val)//6
        i = 0
        colorlist = []
        while i < nc:
            pos = i*6
            cols = self.extract_color(val,pos)
            if i == 0:
                # first color is inside solid color
                self.solids[0] = tuple(cols)
            else:
                c = tuple([float(i-1)/(nc-2)] + cols)
                colorlist.append(c)
            i+= 1
        self.gradient.load_list(colorlist)
        
    def parse_solids(self,val,f):
        line = f.readline()
        self.solids = []
        while not line.startswith("]"):
            cols = self.extract_color(line,0,True)            
            self.solids.append(tuple(cols))
            line = f.readline()
        
    def parse_colorlist(self,val,f):
        '0.7234 = 0xffaa3765: gf4d < 2.7'
        line = f.readline()
        colorlist = []
        while not line.startswith("]"):
            entry = line.split("=")
            
            if len(entry) != 2:
                raise ValueError, "invalid color %s in file" % line

            cols = self.extract_color(entry[1],0,True)            
            index = float(entry[0])
            
            colorlist.append(tuple([index] + cols))
            line = f.readline()
        self.gradient.load_list(colorlist)

    def parse_gradient(self,val,f):
        'Gimp gradient format: gf4d >= 2.7'
        self.gradient.load(f)
        
    def parse_file(self,val,f):
        mapfile = open(val)
        self.parse_map_file(mapfile)

    def parse_map_file(self,mapfile, maxdiff=0):
        x = mapfile.tell()
        try:
            self.gradient.load(mapfile)
        except gradient.HsvError, err1:
            if self.parent:
                self.parent.warn("Error reading colormap: %s" % str(err1))
            
        except gradient.Error, err1:
            try:
                mapfile.seek(x)
                self.parse_fractint_map_file(mapfile,maxdiff)
            except Exception, err2:
                if self.parent:
                    self.parent.warn("Error reading colormap: %s" % str(err2))
        
    def parse_fractint_map_file(self,mapfile,maxdiff=0):
        'parse a fractint .map file'
        i = 0
        colorlist = []
        for line in mapfile:
            m = rgb_re.match(line)
            if m != None:
                (r,g,b) = (min(255, int(m.group(1))),
                           min(255, int(m.group(2))),
                           min(255, int(m.group(3))))
                
                if i == 0:
                    # first color is inside solid color
                    self.solids[0] = (r,g,b,255)
                else:
                    colorlist.append(((i-1)/255.0,r,g,b,255))
            i += 1
        self.gradient.load_list(colorlist,maxdiff)
        
class T(FctUtils):
    XCENTER = 0
    YCENTER = 1
    ZCENTER = 2
    WCENTER = 3
    MAGNITUDE = 4
    XYANGLE = 5
    XZANGLE = 6
    XWANGLE = 7
    YZANGLE = 8
    YWANGLE = 9
    ZWANGLE = 10
    
    def __init__(self,compiler,site=None):
        FctUtils.__init__(self)
        
        self.format_version = 2.8
        
        # formula support
        self.formula = None
        self.funcName = "Mandelbrot"
        self.bailfunc = 0
        self.cfuncs = [None,None]
        self.cfunc_names = [None,None]
        self.cfunc_files = [None,None]
        self.cfunc_params = [[], []]
        self.cfunc_paramtypes = [[], []]
        self.yflip = False
        self.periodicity = True
        self.auto_tolerance = False
        self.antialias = 1
        self.compiler = compiler
        self.outputfile = None
        self.set_formula("gf4d.frm",self.funcName)
        self.set_inner("gf4d.cfrm","zero")
        self.set_outer("gf4d.cfrm","continuous_potential")
        self.dirtyFormula = True # formula needs recompiling
        self.dirty = True # parameters have changed
        self.auto_deepen = True
        self.clear_image = True
        
        self.reset()

        # interaction with fract4dc library
        self.site = site or fract4dc.site_create(self)

        # default is just white outside
        self.gradient = gradient.Gradient()
        self.gradient.segments[0].left_color = [1.0,1.0,1.0,1.0]
        self.gradient.segments[0].right_color = [1.0,1.0,1.0,1.0]

        self.solids = [(0,0,0,255),(0,0,0,255)]
        
        # colorfunc lookup
        self.colorfunc_names = [
            "default", 
            "continuous_potential",
            "zero",
            "ejection_distance",
            "decomposition",
            "external_angle"]

        self.saved = True # initial params not worth saving

    def serialize(self):
        out = StringIO.StringIO()
        self.save(out,False)
        return out.getvalue()

    def deserialize(self,string):
        self.loadFctFile(StringIO.StringIO(string))
        self.changed()
        
    def save_cfunc_info(self,index,section,file):
        print >>file, "[%s]" % section
        print >>file, "formulafile=%s" % self.cfunc_files[index]
        print >>file, "function=%s" % self.cfunc_names[index]
        self.save_formula_params(
            file,self.cfuncs[index],self.cfunc_params[index])
        print >>file, "[endsection]"
        
    def save(self,file,update_saved_flag=True):
        print >>file, "gnofract4d parameter file"
        print >>file, "version=2.8"

        paramnames = ["x","y","z","w","size","xy","xz","xw","yz","yw","zw"]
        for pair in zip(paramnames,self.params):
            print >>file, "%s=%.17f" % pair

        print >>file, "maxiter=%d" % self.maxiter
        print >>file, "yflip=%s" % self.yflip
        print >>file, "periodicity=%s" % self.periodicity
        print >>file, "[function]"
        print >>file, "formulafile=%s" % self.funcFile
        print >>file, "function=%s" % self.funcName
        self.save_formula_params(file,self.formula,self.initparams)
        print >>file, "[endsection]"
        
        self.save_cfunc_info(1,"inner",file)
        self.save_cfunc_info(0,"outer",file)
        
        print >>file, "[colors]"
        print >>file, "colorizer=1"
        print >>file, "solids=["
        for solid in self.solids:
            print >>file, "%02x%02x%02x%02x" % solid
        print >>file, "]"
        
        print >>file, "gradient="
        self.gradient.save(file)
        
        if update_saved_flag:
            self.saved = True

    def save_formula_params(self,file,formula,params):
        names = self.func_names(formula)
        names.sort()
        for name in names:
            print >>file, "%s=%s" % (name, self.get_func_value(name,formula))
        names = formula.symbols.param_names()
        names.sort()
        for name in names:
            print >>file, "%s=%s" % \
                  (name, self.initvalue(name, formula.symbols,params))
        
    def initvalue(self,name,symbol_table,params):
        ord = self.order_of_name(name,symbol_table)
        type = symbol_table[name].type
        
        if type == fracttypes.Complex:
            return "(%.17f,%.17f)"%(params[ord],params[ord+1])
        elif type == fracttypes.Hyper:
            return "(%.17f,%.17f,%.17f,%.17f)"% \
                   (params[ord],params[ord+1],params[ord+2],params[ord+3])
        elif type == fracttypes.Float:
            return "%.17f" % params[ord]
        elif type == fracttypes.Int:
            return "%d" % params[ord]
        elif type == fracttypes.Bool:
            return "%s" % params[ord]
        else:
            raise ValueError("Unknown type %s for param %s" % (type,name))

    def parse_periodicity(self,val,f):
        self.set_periodicity(bool(val))
        
    def parse__inner_(self,val,f):
        params = ParamBag()
        params.load(f)
        self.set_inner(params.dict["formulafile"],params.dict["function"])
        self.set_cfunc_params(params,1)
        
    def parse__outer_(self,val,f):
        params = ParamBag()
        params.load(f)
        self.set_outer(params.dict["formulafile"],params.dict["function"])
        self.set_cfunc_params(params,0)

    def set_cfunc_params(self,params,index):
        for (name,val) in params.dict.items():
            if name == "formulafile" or name=="function":
                pass
            else:
                self.set_named_item(
                    name,val,self.cfuncs[index],self.cfunc_params[index])

    def set_named_item(self,name,val,formula,params):
        sym = formula.symbols[name].first()
        if isinstance(sym, fracttypes.Func):
            self.set_named_func(name,val,formula)
        else:
            self.set_named_param(name,val,formula,params)
        
    def __del__(self):
        if self.outputfile:
            #os.remove(self.outputfile)
            pass

    def __copy__(self):
        # override shallow-copy to do a deeper copy than normal,
        # but still don't try and copy *everything*

        c = T(self.compiler,self.site)

        c.maxiter = self.maxiter
        c.params = copy.copy(self.params)

        c.bailfunc = self.bailfunc

        c.set_formula(self.funcFile,self.funcName)

        # copy the function overrides
        for name in self.func_names(self.formula):
            c.set_named_func(name,
                             self.get_func_value(name,self.formula),
                             c.formula)

        c.initparams = copy.copy(self.initparams) # must be after set_formula

        c.set_outer(self.cfunc_files[0], self.cfunc_names[0])
        c.set_inner(self.cfunc_files[1], self.cfunc_names[1])
        
        for i in range(2):
            frm = self.cfuncs[i]
            c_frm = c.cfuncs[i]
            for name in self.func_names(frm):
                c.set_named_func(name,
                                 self.get_func_value(name,frm),
                                 c_frm)

            c.cfunc_params[i] = copy.copy(self.cfunc_params[i]) 
                    
        c.gradient = copy.copy(self.gradient)
        c.solids = copy.copy(self.solids)
        c.yflip = self.yflip
        c.periodicity = self.periodicity
        c.saved = self.saved
        c.clear_image = self.clear_image
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
        self.yflip = False
        self.auto_tolerance = False
        
        self.set_formula_defaults()

    def reset_zoom(self):
        mag = self.formula.defaults.get("magn")
        if mag:
            mag = mag.value
        else:
            mag = self.formula.defaults.get("magnitude")
            if mag:
                mag = mag.value
            else:
                mag = 4.0
        self.set_param(self.MAGNITUDE, mag)

    def copy_colors(self, f):
        self.gradient = copy.copy(f.gradient)
        self.solids[0:len(f.solids)] = f.solids[:]
        self.changed(False)
        
    def set_cmap(self,mapfile):
        c = Colorizer(self)
        file = open(mapfile)
        c.parse_map_file(file)
        self.gradient = c.gradient
        self.solids[0:len(c.solids)] = c.solids[:]
        self.changed(False)

    def get_initparam(self,n,param_type):
        if param_type == 0:
            params = self.initparams
        else:
            params = self.cfunc_params[param_type-1]
        return params[n]
    
    def set_initparam(self,n,val, param_type):
        if param_type == 0:
            params = self.initparams
            t = self.paramtypes[n]
        else:
            params = self.cfunc_params[param_type-1]
            t = self.cfunc_paramtypes[param_type-1][n]

        if t == fracttypes.Float:
            val = float(val)
        elif t == fracttypes.Int:
            val = int(val)
        elif t == fracttypes.Bool:
            val = bool(val)
        else:
            raise ValueError("Unknown parameter type %s" % t)
        
        if params[n] != val:
            params[n] = val
            self.changed()

    def set_solids(self, solids):
        if self.solids[0] == solids[0] and self.solids[1] == solids[1]:
            return
        self.solids = solids
        self.changed(False)
        
    def set_gradient(self, g):
        # FIXME: compare for equality
        self.gradient = g
        self.changed(False)
        
    def refresh(self):
        if self.compiler.out_of_date(self.funcFile):
            self.set_formula(self.funcFile,self.funcName)
        for i in xrange(2):
            if self.compiler.out_of_date(self.cfunc_files[i]):
                self.set_colorfunc(i,self.cfunc_files[i],self.cfunc_names[i])
            
    def set_formula_defaults(self):
        if self.formula == None:
            return

        self.initparams = self.formula.symbols.default_params()
        self.paramtypes = self.formula.symbols.type_of_params()
        
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

        for i in xrange(2):
            self.cfunc_params[i] = self.cfuncs[i].symbols.default_params()
            self.cfunc_paramtypes[i] = self.cfuncs[i].symbols.type_of_params()
        
    def set_formula(self,formulafile,func):
        formula = self.compiler.get_formula(formulafile,func)
        if formula == None:
            raise ValueError("no such formula: %s:%s" % (formulafile, func))

        if formula.errors != []:
            raise ValueError("invalid formula '%s':\n%s" % \
                             (func, "\n".join(formula.errors)))

        self.formula = formula
        self.funcName = func
        self.funcFile = formulafile

        self.initparams = self.formula.symbols.default_params()
        self.paramtypes = self.formula.symbols.type_of_params()
        self.set_bailfunc()

        self.formula_changed()
        self.changed()

    def get_func_name(self):
        return self.funcName

    def get_saved(self):
        return self.saved
    
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
            self.set_func(func[0],funcname,self.formula)            

    def func_names(self,formula):
        return formula.symbols.func_names()

    def param_names(self,formula):
        return formula.symbols.param_names()
    
    def set_named_func(self,func_to_set,val,formula):
        fname = formula.symbols.demangle(func_to_set)
        func = formula.symbols.get(fname)
        self.set_func(func[0],val,formula)            

    def get_func_value(self,func_to_get,formula):
        fname = formula.symbols.demangle(func_to_get)
        func = formula.symbols[fname]
        #print "got %s" % func
        return func[0].cname

    def get_named_param_value(self,name):
        op = self.formula.symbols.order_of_params()
        ord = op.get(self.formula.symbols.mangled_name(name))
        return self.initparams[ord]
    
    def changed(self,clear_image=True):
        self.dirty = True
        self.saved = False
        self.clear_image = clear_image
        
    def formula_changed(self):
        self.dirtyFormula = True
        
    def set_func(self,func,fname,formula):
        if func.cname != fname:
            formula.symbols.set_std_func(func,fname)
            self.dirtyFormula = True
            self.changed()
            
    def set_periodicity(self,periodicity):
        if self.periodicity != periodicity:
            self.periodicity = periodicity
            self.changed()
        
    def set_inner(self,funcfile,funcname):
        self.set_colorfunc(1,funcfile,funcname)

    def set_colorfunc(self,index,funcfile,funcname):
        func = self.compiler.get_colorfunc(funcfile,funcname,"cf%d" % index)
        if func == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, funcname))
        if func.errors != []:
            raise ValueError("Invalid colorfunc '%s':\n%s" % \
                             (funcname,"\n".join(func.errors)))
        
        self.cfuncs[index] = func
        self.cfunc_files[index] = funcfile
        self.cfunc_names[index] = funcname
        self.cfunc_params[index] = func.symbols.default_params()
        self.cfunc_paramtypes[index] = func.symbols.type_of_params()
        
        self.dirtyFormula = True
        self.formula_changed()
        self.changed()
        
    def set_outer(self,funcfile,funcname):
        self.set_colorfunc(0,funcfile,funcname)
        
    def compile(self):
        if self.formula == None:
            raise ValueError("no formula")
        if self.dirtyFormula == False:
            return self.outputfile

        outputfile = self.compiler.compile_all(
            self.formula, 
            self.cfuncs[0],
            self.cfuncs[1])
        
        if outputfile != None:
            if self.outputfile != outputfile:
                self.outputfile = outputfile
                self.handle = fract4dc.pf_load(self.outputfile)
                self.pfunc = fract4dc.pf_create(self.handle)

        self.dirtyFormula = False
        return self.outputfile

    def make_random_colors(self, n):
        self.gradient.randomize(n)
        self.changed(False)
        
    def mul_vs(self,v,s):
        return map(lambda x : x * s, v)

    def xy_random(self,weirdness,size):
        return weirdness * 0.5 * size * (random.random() - 0.5)

    def zw_random(self,weirdness,size):
        factor = math.fabs(1.0 - math.log(size)) + 1.0
        return weirdness * (random.random() - 0.5 ) * 1.0 / factor

    def angle_random(self, weirdness):
        action = random.random()
        if action > weirdness:
            return 0.0 # no change

        action = random.random()
        if action < weirdness/6.0: 
            # +/- pi/2
            if random.random() > 0.5:
                return math.pi/2.0
            else:
                return math.pi/2.0
        
        return weirdness * (random.random() - 0.5) * math.pi/2.0

    def mutate_formula_params(self, weirdness, size, params, paramtypes):
        for i in xrange(len(params)):
            if paramtypes[i] == fracttypes.Float:
                params[i] += self.zw_random(weirdness, size)
            elif paramtypes[i] == fracttypes.Int:
                # FIXME: need to be able to look up enum to find min/max
                pass
            elif paramtypes[i] == fracttypes.Bool:
                if random.random() < weirdness * 0.2:
                    params[i] = not params[i]
        
    def mutate(self,weirdness,color_weirdness,colormaps):
        '''randomly adjust position, colors, angles and parameters.
        weirdness is between 0 and 1 - 0 is no change, 1 is lots'''

        is4d = self.formula.is4D()
        size = self.params[self.MAGNITUDE]
        self.params[self.XCENTER] += self.xy_random(weirdness, size)
        self.params[self.YCENTER] += self.xy_random(weirdness, size)
        if is4d:
            self.params[self.ZCENTER] += self.zw_random(weirdness, size)
            self.params[self.WCENTER] += self.zw_random(weirdness, size)

        self.params[self.XYANGLE] += self.angle_random(weirdness)
        
        if is4d:
            for a in xrange(self.XZANGLE,self.ZWANGLE):
                self.params[a] += self.angle_random(weirdness)

        if random.random() < weirdness * 0.75:
            self.params[self.MAGNITUDE] *= 1.0 + (0.5 - random.random())

        self.mutate_formula_params(weirdness, size, self.initparams, self.paramtypes)
        self.mutate_formula_params(
            color_weirdness, size, self.cfunc_params[0], self.cfunc_paramtypes[0])
        self.mutate_formula_params(
            color_weirdness, size, self.cfunc_params[1], self.cfunc_paramtypes[1])
        
        if random.random() < color_weirdness * 0.3:
            self.set_cmap(random.choice(colormaps))
        
    def nudge(self,x,y,axis=0):
        # move a little way in x or y
        self.relocate(0.025 * x , 0.025 * y, 1.0,axis)

    def relocate(self,dx,dy,zoom,axis=0):
        if dx == 0 and dy == 0 and zoom == 1.0:
            return
        
        m = fract4dc.rot_matrix(self.params)

        deltax = self.mul_vs(m[axis],dx)
        if self.yflip:
            deltay = self.mul_vs(m[axis+1],dy)
        else:
            deltay = self.mul_vs(m[axis+1],-dy)

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

    def all_params(self):
        return self.initparams + self.cfunc_params[0] + self.cfunc_params[1]

    def draw(self,image):
        handle = fract4dc.pf_load(self.outputfile)
        pfunc = fract4dc.pf_create(handle)
        cmap = fract4dc.cmap_create_gradient(self.gradient.segments)
        (r,g,b,a) = self.solids[0]
        fract4dc.cmap_set_solid(cmap,0,r,g,b,a)
        (r,g,b,a) = self.solids[1]
        fract4dc.cmap_set_solid(cmap,1,r,g,b,a)
        
        initparams = self.all_params()
        fract4dc.pf_init(pfunc,1.0E-9,initparams)

        fract4dc.calc(self.params,self.antialias,self.maxiter,
                      self.yflip,self.periodicity,
                      pfunc,cmap,self.auto_deepen,
                      1,image,self.site, self.clear_image)
        
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
        global THIS_VERSION
        self.format_version=float(val)
        if self.format_version < 2.0:
            # old versions displayed everything upside down
            # switch the rotation so they load OK
            self.yflip = True
        if 1.7 < self.format_version < 2.0:
            # a version that used auto-tolerance for Nova and Newton
            self.auto_tolerance = True
            
        if self.format_version > THIS_VERSION:
            warning = \
'''This file was created by a newer version of Gnofract 4D.
The image may not display correctly. Please upgrade to version %.1f.''' 

            self.warn(warning % self.format_version)
    def warn(self,msg):
        print msg
        
    def parse__function_(self,val,f):
        params = ParamBag()
        params.load(f)
        file = params.dict.get("formulafile",self.funcFile)
        func = params.dict.get("function", self.funcName)
        self.set_formula(file,func)
            
        for (name,val) in params.dict.items():
            if name == "formulafile" or name == "function":
                pass
            elif name == "a" or name =="b" or name == "c":
                self.set_named_param("@" + name, val,
                                     self.formula, self.initparams)
            else:
                self.set_named_item(name,val,self.formula,
                                    self.initparams)

    def set_named_param(self,name,val,formula,params):
        #print "named param %s : %s" % (name, val)
        op = formula.symbols.order_of_params()
        ord = op.get(formula.symbols.mangled_name(name))
        if ord == None:
            #print "Ignoring unknown param %s" % name
            return

        t = formula.symbols[name].type 
        if t == fracttypes.Complex:
            m = cmplx_re.match(val)
            if m != None:
                re = float(m.group(1)); im = float(m.group(2))
                if params[ord] != re:
                    params[ord] = re
                    self.changed()
                if params[ord+1] != im:                
                    params[ord+1] = im
                    self.changed()
        elif t == fracttypes.Hyper:
            m = hyper_re.match(val)
            if m!= None:
                for i in xrange(4):
                    val = float(m.group(i+1))
                    if params[ord+i] != val:
                        params[ord+i] = val
                        self.changed()
        elif t == fracttypes.Float:
            params[ord] = float(val)
        elif t == fracttypes.Int:
            params[ord] = int(val)
        elif t == fracttypes.Bool:
            params[ord] = bool(val)
        else:
            raise ValueError("Unknown param type %s for %s" % (t,name))
        
    def parse_bailfunc(self,val,f):
        # can't set function directly because formula hasn't been parsed yet
        self.bailfunc = int(val)

    def apply_colorizer(self, cf):
        self.gradient = cf.gradient
        self.solids[0:len(cf.solids)] = cf.solids[:]
        self.changed(False)
        if cf.direct:
            # loading a legacy rgb colorizer
            self.set_outer("gf4d.cfrm", "rgb")
            cfunc = self.cfuncs[0]
            params = self.cfunc_params[0]

            self.set_named_item("@base_red",cf.rgb[0], cfunc, params)
            self.set_named_item("@base_green",cf.rgb[1], cfunc, params)
            self.set_named_item("@base_blue",cf.rgb[2], cfunc, params)

    def parse__colors_(self,val,f):
        cf = Colorizer(self)
        cf.load(f)
        self.apply_colorizer(cf)
        
    def parse__colorizer_(self,val,f):
        which_cf = int(val)
        cf = Colorizer(self)
        cf.load(f)        
        if which_cf == 0:
            self.apply_colorizer(cf)
        # ignore other colorlists for now

    def parse_inner(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_inner("gf4d.cfrm",name)

    def parse_outer(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_outer("gf4d.cfrm",name)

    def set_yflip(self,yflip):
        if self.yflip != yflip:
            self.yflip = yflip
            self.changed()
        
    def parse_yflip(self,val,f):
        self.yflip = val == "1"
        
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

    def order_of_name(self,name,symbol_table):
        op = symbol_table.order_of_params()
        rn = symbol_table.mangled_name(name)
        ord = op.get(rn)
        if ord == None:
            #print "can't find %s (%s) in %s" % (name,rn,op)
            pass
        return ord
    
    def fix_bailout(self):
        # because bailout occurs before we know which function this is
        # in older files, we save it in self.bailout then apply to the
        # initparams later
        if self.bailout != 0.0:
            self.update_bailout_param(self.formula.symbols,self.initparams)
            self.update_bailout_param(
                self.cfuncs[0].symbols,self.cfunc_params[0])
            self.update_bailout_param(
                self.cfuncs[1].symbols,self.cfunc_params[1])
            
    def update_bailout_param(self,symbols,params):
        ord = self.order_of_name("@bailout",symbols)
        if ord == None:
            # no bailout value for this function
            return
        params[ord] = float(self.bailout)
            
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
        self.saved = True
        
if __name__ == '__main__':
    import sys
    import fc
    import fract4dc

    g_comp = fc.Compiler()
    g_comp.file_path.append("formulas")
    g_comp.file_path.append("../formulas")
    g_comp.file_path.append(
            os.path.join(sys.exec_prefix, "share/formulas/gnofract4d"))

    f = T(g_comp)
    for arg in sys.argv[1:]:
        file = open(arg)
        f.loadFctFile(file)
        f.compile()
        image = fract4dc.image_create(64,48)
        f.draw(image)
        fract4dc.image_save(image,os.path.basename(arg) + ".tga")
        
