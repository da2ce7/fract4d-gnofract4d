#!/usr/bin/env python

# Trivial symbol table implementation

import copy
from UserDict import UserDict
from UserList import UserList
import string
import types
import re
import math

from fracttypes import *
import stdlib

class OverloadList(UserList):
    def __init__(self,list,**kwds):
        UserList.__init__(self,list)
        self.pos = -1
        self._is_operator = kwds.get("operator")
        self.__doc__ = kwds.get("doc")
        
    def first(self):
        return self[0]

    def is_operator(self):
        return self._is_operator
    
def efl(fname, template, tlist,**kwds):
    'short-hand for expandFuncList - just reduces the amount of finger-typing'
    list = []
    for t in tlist:            
        f = "Func(%s,stdlib,\"%s\")" % (re.sub("_", str(t), template), fname)
        realf = eval(f)
        list.append(eval(f))
    return OverloadList(list,**kwds)

def cfl(template, tlist):
    list = []
    for t in tlist:            
        f = re.sub("_", str(t), template)
        realf = eval(f)
        list.append(eval(f))
    return list

def mkf(args, ret, fname, module=stdlib):
    # create a function
    return Func(args,ret,module,fname)

def mkfl(dict, name, list, **kwds):
    "make a list of functions"
    fname = kwds.get("fname",name) # fname overrides name if present
    # avoid having to provide list of one element
    if not isinstance(list[0][0],types.ListType):
        list = [list]
    funclist = map(lambda x : mkf(x[0],x[1],fname), list)
    dict[name] = OverloadList(funclist,**kwds)
        
class Alias:
    def __init__(self,realName):
        self.realName = realName
        self.pos = -1
        self.cname = None

    
def createDefaultDict():
    d = {
        # standard operators

        # comparison
        
        # fixme - issue a warning for complex compares
        ">":  efl("gt",    "[_,_] , Bool", [Int, Float, Complex]),
        ">=": efl("gte",   "[_,_] , Bool", [Int, Float, Complex]),
        "<":  efl("lt",    "[_,_] , Bool", [Int, Float, Complex]),
        "<=": efl("lte",   "[_,_] , Bool", [Int, Float, Complex]),

        # arithmetic
        "%":  efl("mod",   "[_,_] , _", [Int, Float],operator=True),

        "/":  OverloadList([
                Func([Float, Float], Float, stdlib, "div"),
                Func([Complex, Float], Complex, stdlib, "div"),
                Func([Complex, Complex], Complex, stdlib, "div"),
                #Func([Color, Float], Float, stdlib, "div")
                ],operator=True),

        "*":  efl("mul",   "[_,_] , _", [Int, Float, Complex, Hyper]), #+ \
              #[ Func([Color, Float], Float, stdlib, "mul")],

        "^": OverloadList([ Func([Float, Float], Float, stdlib, "pow"),
                Func([Complex, Float], Complex, stdlib, "pow"),
                Func([Complex, Complex], Complex, stdlib, "pow")]),
        
        "t__neg": efl("neg", "[_], _", [Int, Float, Complex]),
        
        # unary negation already factored out

        # logical ops
        "&&": OverloadList([ Func([Bool, Bool], Bool, stdlib, None) ]),
        "||": OverloadList([ Func([Bool, Bool], Bool, stdlib, None) ]),
        "!" : OverloadList([ Func([Bool],Bool, stdlib, None) ]),

        # predefined magic variables
        "t__h_pixel": Alias("pixel"),
        "t__h_xypixel": Alias("pixel"),
        "pixel" : Var(Complex,doc="The (X,Y) coordinates of the current point. When viewing the Mandelbrot set, this has a different value for each pixel. When viewing the Julia set, it remains constant for each pixel."), 
        "t__h_z" : Alias("z"),
        "z"  : Var(Complex),
        "t__h_index": Var(Float),
        "t__h_numiter": Var(Int),
        "t__h_maxiter": Alias("maxiter"),
        "maxiter" : Var(Int),
        "t__h_pi" : Var(Float,math.pi),
        "t__h_tolerance" : Var(Float),
        "t__h_zwpixel" : Var(Complex,doc="The (Z,W) coordinates of the current point. (See #pixel for the other two coordinates.) When viewing the Mandelbrot set, this remains constant for each pixel on the screen; when viewing the Julia set, it's different for each pixel. Initialize z to some function of this to take advantage of 4D drawing."),
        "t__h_solid" : Var(Bool,doc="Set this to true in a coloring function to use the solid color rather than the color map.")
        }

    # extra shorthand to make things as short as possible
    def f(name, list, **kwds):
        mkfl(d,name,list,**kwds)

    # standard functions 
    f("complex",
      [[Float, Float], Complex],
      doc='''Construct a complex number from two real parts.
      complex(a,b) is equivalent to (a,b).''')

    f("hyper",
      [[Float, Float, Float, Float], Hyper],
      doc='''Construct a hypercomplex number from a real and 3 imaginary parts.
      hypercomplex(a,b,c,d) is equivalent to (a,b,c,d).''')
    
    f("sqr",
      cfl("[_] , _",  [Int, Float, Complex]),
      doc="Square the argument. sqr(x) is equivalent to x*x or x^2.")

    #f("cube",
    #  cfl("[_] , _", [Int, Float, Complex]),
    #  doc="Cube the argument. cube(x) is equivalent to x*x*x or x^3.")
    
    f("ident",
      cfl("[_] , _",  [Int, Float, Complex, Bool]),
      doc='''Do nothing. ident(x) is equivalent to x.
      This function is useless in normal formulas but
      comes in useful as a value for a function parameter
      to a formula. For example, a general formula like z = @fn1(z*z)+c
      can be set back to a plain Mandelbrot by setting fn1 to ident.
      Note: ident() is compiled out so there\'s no speed penalty involved.''')
    
    f("conj",
      [[Complex], Complex],
      doc="The complex conjugate. conj(a,b) is equivalent to (a,-b).")

    f("flip",
      [[Complex], Complex],
      doc='''Swap the real and imaginary parts of a complex number.
      flip(a,b) = (b,a).''')

    f("real",
      [[[Complex], Float], [[Hyper], Float]],
      doc='''Extract the real part of a complex or hypercomplex number.
      real(a,b) = a.
      real() is unusual in that it can be assigned to: real(z) = 7 changes
      the real part of z.''')

    f("real2",
      [[Complex], Float],
      doc='''The square of the real part of a complex number.
      real2(a,b) = a*a.
      While not a generally useful function, this is provided to ease porting
      of files from older Gnofract 4D versions.''')

    f("imag",
      [[[Complex], Float], [[Hyper], Float]],
      doc='''Extract the imaginary part of a complex or hypercomplex number.
      imag(a,b) = b.
      imag() is unusual in that it can be assigned to: imag(z) = 7 changes
      the imag part of z.''')

    f("imag2",
      [[Complex], Float],
      doc='''The square of the imaginary part of a complex number.
      real2(a,b) = b*b.
      While not a generally useful function, this is provided to ease porting
      of files from older Gnofract 4D versions.''')

    f("hyper_ri",
      [[Hyper], Complex],
      doc='''The real and imaginary parts of a hypercomplex number.
      Can be assigned to. hyper_ri(a,b,c,d) = (a,b).''')

    f("hyper_jk",
      [[Hyper], Complex],
      doc='''The 3rd and 4th parts of a hypercomplex number.
      Can be assigned to. hyper_jk(a,b,c,d) = (c,d).''')
    
    f("hyper_j",
      [[Hyper], Float],
      doc='''The 3rd component of a hypercomplex number. Can be assigned to.
      hyper_j(a,b,c,d) = c.''')

    f("hyper_k",
      [[Hyper], Float],
      doc='''The 4th component of a hypercomplex number. Can be assigned to.
      hyper_k(a,b,c,d) = d.''')
      
    f("recip",
      cfl("[_] , _", [ Float, Complex]),
      doc='''The reciprocal of a number. recip(x) is equivalent to 1/x.''')

    f("trunc",
      [[[Float], Int], [[Complex], Complex]],
      doc='''Round towards zero.''')

    f("round",
      [[[Float], Int], [[Complex], Complex]],
      doc='''Round to the nearest number (0.5 rounds up).''')

    f("floor",
      [[[Float], Int], [[Complex], Complex]],
      doc='''Round down to the next lowest number.''')

    f("ceil",
      [[[Float], Int], [[Complex], Complex]],
      doc='''Round up to the next highest number.''')

    f("zero",
      cfl("[_], _ ", [Int, Float, Complex]),
      doc='''Returns zero.''')
    
    f("abs",
      cfl("[_], _", [Float, Complex]),
      doc='''The absolute value of a number. abs(3) = abs(-3) = 3.
      abs() of a complex number is a complex number consisting of
      the absolute values of the real and imaginary parts, i.e.
      abs(a,b) = (abs(a),abs(b)).''')

    f("cabs",
      [[Complex], Float],
      doc='''The complex modulus of a complex number z.
      cabs(a,b) is equivalent to sqrt(a*a+b*b).
      This is also the same as sqrt(|z|)''')

    f("cmag",
      [[[Complex], Float], [[Hyper], Float]],
      doc='''The squared modulus of a complex or hypercomplex number z.
      cmag(a,b) is equivalent to a*a+b*b. This is the same as |z|.''')

    f("log",
      cfl("[_], _", [Float, Complex]),
      doc='The natural log.')

    f("sqrt",
      cfl("[_], _", [Float, Complex]),
      doc='''The square root.
      The square root of a negative float number is NaN
      (ie it is NOT converted to complex). Thus sqrt((-3,0)) != sqrt(-3).''' )

    f("exp",
      cfl("[_], _", [Float, Complex]),
      doc='exp(x) is equivalent to e^x')

    f("manhattan",
      [[Complex], Float],
      doc='''The Manhattan distance between the origin and complex number z.
      manhattan(a,b) is equivalent to abs(a) + abs(b).''')
    
    f("manhattanish",
      [[Complex], Float],
      doc='''A variant on Manhattan distance provided for backwards
      compatibility. manhattanish(a,b) is equivalent to a+b.''')
      
    f("manhattanish2",
      [[Complex], Float],
      doc='''A variant on Manhattan distance provided for backwards
      compatibility. manhattanish2(a,b) is equivalent to (a*a + b*b)^2.''')

    f("max2",
      [[Complex], Float],
      doc='''max2(a,b) returns the larger of a*a or b*b. Provided for
      backwards compatibility.''')

    f("min2",
      [[Complex], Float],
      doc='''min2(a,b) returns the smaller of a*a or b*b. Provided for
      backwards compatibility.''')

    f("sin",
      cfl( "[_], _", [Float, Complex]),
      doc='trigonometric sine function.')
    
    f("cos",
      cfl( "[_], _", [Float, Complex]),
      doc='trigonometric sine function.')

    f("cosxx",
      cfl( "[_], _", [Complex]),
      doc='''Incorrect version of cosine function. Provided for backwards
      compatibility with equivalent wrong function in Fractint.''')
    
    f("tan",
      cfl( "[_], _", [Float, Complex]),
      doc='trigonometric sine function.')

    f("cotan",
      cfl("[_], _", [Float, Complex]),
      doc="Trigonometric cotangent function.")
      
    f("sinh",
      cfl( "[_], _", [Float, Complex]),
      doc='Hyperbolic sine function.')
    
    f("cosh",
      cfl( "[_], _", [Float, Complex]),
      doc='Hyperbolic cosine function.')
    
    f("tanh",
      cfl( "[_], _", [Float, Complex]),
      doc='Hyperbolic tangent function.')

    f("cotanh",
      cfl("[_], _", [Float, Complex]),
      doc='Hyperbolic cotangent function.')
        
    f("asin",
      cfl( "[_], _", [Float, Complex]),
      doc='Inverse sine function.')
    
    f("acos",
      cfl( "[_], _", [Float, Complex]),
      doc='Inverse cosine function.')
    
    f("atan",
      cfl( "[_], _", [Float, Complex]),
      doc='Inverse tangent function.')

    f("atan2",
      [[Complex], Float],
      doc='''The angle between this complex number and the real line,
      aka the complex argument.''')
    
    f("asinh",
      cfl( "[_], _", [Float, Complex]),
      doc='Inverse hyperbolic sine function.')
    
    f("acosh",
      cfl( "[_], _", [Float, Complex]),
      doc='Inverse hyperbolic cosine function.')
    
    f("atanh",
      cfl( "[_], _", [Float, Complex]),
      doc='Inverse hyperbolic tangent function.')

    # operators
    
    f("+", 
      cfl("[_,_] , _", [Int, Float, Complex, Hyper]),
      fname="add",
      operator=True,
      doc='Adds two numbers together.')

    f("-",
      cfl("[_,_] , _", [Int, Float, Complex, Hyper]),
      fname="sub",
      operator=True,
      doc='Subtracts two numbers')
    
    f("!=",
      cfl("[_,_] , Bool", [Int, Float, Complex, Bool]),
      fname="noteq",
      operator=True,
      precedence=3,
      doc='''Inequality operator. Compare two values and return true if
      they are different.'''),

    f("==",
      cfl("[_,_] , Bool", [Int, Float, Complex, Bool]),
      fname="eq",
      operator=True,
      precedence=3,
      doc='''Equality operator. Compare two values and return true if they are
      the same.''')


    # predefined parameters
    for p in xrange(1,7):
        name = "p%d" % p
        d[name] = Alias("t__a_" + name)
        d["t__a_" + name]  = Var(Complex)
        
    # predefined functions
    for p in xrange(1,5):
        name = "fn%d" % p
        d[name] = Alias("t__a_" + name)
        d["t__a_" + name ] = OverloadList([Func([Complex],Complex, stdlib, "ident") ])

    d["t__a__transfer"] = OverloadList([Func([Float],Float, stdlib, "ident") ])
    
    for (k,v) in d.items():
        if hasattr(v,"cname") and v.cname == None:
            v.cname = k
            
    return d


def mangle(k,prefix=""):
    l = string.lower(k)
    if l[0] == '#':
        l = "t__h_" + prefix + l[1:]
    elif l[0] == '@':
        l = "t__a_" + prefix + l[1:]
    return l
               
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self,prefix=""):
        UserDict.__init__(self)
        self.reset()
        self.nextlabel = 0
        self.nextTemp = 0
        self.prefix = prefix

    def merge(self,other):
        # self = union(self,other)
        # any clashes are won by self
        for k in other.data.keys():
            if self.data.get(k) == None:
                if self.is_param(k):
                    self.data[self.insert_prefix(other.prefix,k)] = other.data[k]
                else:
                    self.data[k] = other.data[k]
            elif hasattr(self.data[k],"cname") and \
                 hasattr(other.data[k],"cname") and \
                 self.data[k].cname != other.data[k].cname:
                    self.data[self.insert_prefix(other.prefix,k)] = other.data[k]

    def has_user_key(self,key):
        return self.data.has_key(mangle(key))
    
    def has_key(self,key):
        if self.data.has_key(mangle(key)):
            return True        
        return self.default_dict.has_key(mangle(key))

    def is_user(self,key):
        val = self.data.get(mangle(key),None)
        if val == None:
            val = self.default_dict.get(mangle(key))
        return val.pos != -1

    def insert_prefix(self, prefix, key):
        if key[0:5] == "t__a_":
            return "t__a_" + prefix + key[5:]
        if key[0:3] == "t__":
            return "t__" + prefix + key[3:]
        return prefix + key
    
    def is_param(self,key):
        return key[0:5] == 't__a_'

    def is_private(self,key):
        return key[0:3] == "t__"

    def mangled_name(self,key):
        k = mangle(key)
        return k
    
    def realName(self,key):
        ' returns mangled key even if var not present for test purposes'
        k = mangle(key)
        return self._realName(k)

    def _realName(self,k):
        val = self.data.get(k,None)
        if val == None:
            val = self.default_dict.get(k)
        if isinstance(val,Alias):
            val = self.default_dict.get(val.realName)
        if val != None:
            if val.cname == None:
                #print k
                raise Exception("argh" + k)
            return val.cname
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
                  ("symbol '%s': only predefined symbols can begin with '#'" %key)
        self.data[k] = value
        if hasattr(value,"cname") and value.cname == None:
            value.cname=self.insert_prefix(self.prefix,k)
        
    def parameters(self,varOnly=False):
        params = {}
        for (name,sym) in self.data.items():
            if self.is_param(name):
                if not varOnly or isinstance(sym,Var):
                    try:
                        params[name] = sym.first()
                    except AttributeError:
                        print sym, name
                        raise
                        
        return params

    def demangle(self,name):
        # remove most obvious mangling.
        # because of case-folding, demangle(mangle(s)) != s
        if name[:3] == "t__":
            name = name[3:]

        if name[:2] == "a_":
            name = "@" + name[2:]
        elif name[:2] == "h_":
            name = "#" + name[2:]
            
        return name

    def param_names(self):
        params = self.parameters()

        names = []
        for (name,param) in params.items():
            if isinstance(param,Var):
                names.append(self.demangle(name))

        return names

    def func_names(self):
        params = self.parameters()

        func_names = []
        for (name,param) in params.items():
            if isinstance(param,Func):
                func_names.append(self.demangle(name))
        return func_names

    def available_param_functions(self,ret,args):
        # a list of all function names which take a complex
        # and return one (for GUI to select a function)
        flist = []
        for (name,func) in self.default_dict.items():
            try:
                for f in func:
                    if f.ret == ret and f.args == args and \
                           not self.is_private(name):
                        flist.append(name)
            except TypeError:
                # wasn't a list
                pass
            
        return flist

    def keysort(self,a,b):
        'comparison fn for key sorting - ensures colorfuncs come at the end'
        if a.startswith('t__a_cf') and not b.startswith('t__a_cf'):
            return 1
        if b.startswith('t__a_cf') and not a.startswith('t__a_cf'):
            return -1
        return cmp(a,b)
    
    def order_of_params(self):
        # a hash which maps param name -> order in input list
        p = self.parameters(True)
        karray = p.keys()
        karray.sort(self.keysort)
        op = {}; i = 0
        for k in karray:
            op[k] = i
            if p[k].type == Complex:
                i += 2
            else:
                i += 1
        op["__SIZE__"]=i

        return op

    def default_params(self):
        op = self.order_of_params()
        defaults = [0.0] * op["__SIZE__"]
        for (k,i) in op.items():
            param = self.get(k)
            if not param: continue
            defval = getattr(param,"default",None)
            if not defval: continue
            if param.type == Complex:
                defaults[i] = defval.value[0].value
                defaults[i+1] = defval.value[1].value
            else:
                defaults[i] = defval.value
        return defaults

    def set_std_func(self,func,fname):
        # repoint parameter @func to use fname next time we compile
        func.set_func(stdlib,fname)
        
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = {} 

    def newLabel(self):
        label = "%slabel%d" % (self.prefix, self.nextlabel)
        self.nextlabel += 1
        return label

    def newTemp(self,type):
        name = "t__%stemp%d" % (self.prefix, self.nextTemp)
        self.nextTemp += 1
        # bypass normal setitem because that checks for t__
        v = Var(type)
        v.cname = name
        v.is_temp = True
        self.data[name] = v
        
        return name
