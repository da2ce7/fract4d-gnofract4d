#!/usr/bin/env python

# Generate C code from a linearized IR trace

import string
import tempfile
import copy
import os

import absyn
import ir
import re
import types

import optimize
import fracttypes

from fracttypes import Bool, Int, Float, Complex, Hyper, Color
from instructions import *
    
class Formatter:
    ' fed to print to fill the output template'
    def __init__(self, codegen, tree, lookup):
        self.codegen = codegen
        self.lookup = lookup
        self.tree = tree
    def __getitem__(self,key):
        try:
            out = self.tree.output_sections[key]
            str_output = string.join(map(lambda x : x.format(), out),"\n")
            return str_output

        except KeyError, err:
            #print "missed %s" % key
            return self.lookup.get(key,"")

class T:
    'code generator'
    def __init__(self,symbols,options={}):
        self.symbols = symbols
        self.out = []
        self.optimize_flags = options.get("optimize",optimize.Nothing)
        # a list of templates and associated actions
        # this must be ordered with largest, most efficient templates first
        # thus performing a crude 'maximal munch' instruction generation
        self.templates = self.expand_templates([
            [ "Binop" , T.binop],
            [ "Unop", T.unop],
            [ "Call", T.call],
            [ "Var" , T.var],
            [ "Const", T.const],
            [ "Label", T.label],
            [ "Move", T.move],
            [ "Jump", T.jump],
            [ "CJump", T.cjump],
            [ "Cast", T.cast],
            ])
        
        self.generate_trace = False

        self.generate_trace = options.get("trace",False)
            
        self.output_template = '''
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

%(pf)s

typedef struct {
    pf_obj parent;
    struct s_param p[PF_MAXPARAMS];
    double pos_params[N_PARAMS];
    double period_tolerance;
    %(struct_members)s
} pf_real ;

static void pf_init(
    struct s_pf_data *p_stub,
    double period_tolerance,
    double *pos_params,
    struct s_param *params,
    int nparams)
{
    pf_real *pfo = (pf_real *)p_stub;
    int i;
    
    if(nparams > PF_MAXPARAMS)
    {
        nparams = PF_MAXPARAMS;
    }
    for(i = 0; i < nparams; ++i)
    {
        pfo->p[i] = params[i];
        /* printf("param %%d = %%.17g\\n",i,params[i]); */
    }
    for(i = 0; i < N_PARAMS; ++i)
    {
        pfo->pos_params[i] = pos_params[i];
    }
    
    pfo->period_tolerance = period_tolerance;
}

static void pf_calc(
    // "object" pointer
    struct s_pf_data *t__p_stub,
    // in params
    const double *t__params, int maxiter, int t__warp_param,
    // only used for debugging
    int t__p_x, int t__p_y, int t__p_aa,
    // out params
    int *t__p_pnIters, int *t__p_pFate, double *t__p_pDist, int *t__p_pSolid,
    int *t__p_pDirectColorFlag, double *t__p_pColors
    )
{
    pf_real *t__pfo = (pf_real *)t__p_stub;

double pixel_re = t__params[0];
double pixel_im = t__params[1];
double t__h_zwpixel_re = t__params[2];
double t__h_zwpixel_im = t__params[3];

double t__h_index = 0.0;
int t__h_solid = 0;
int t__h_fate = 0;
int t__h_inside = 0;
double t__h_color_re = 0.0;
double t__h_color_i = 0.0;
double t__h_color_j = 0.0;
double t__h_color_k = 0.0;

*t__p_pDirectColorFlag = %(dca_init)s;

if(t__warp_param != -1)
{
    t__pfo->p[t__warp_param].doubleval = t__h_zwpixel_re;
    t__pfo->p[t__warp_param+1].doubleval = t__h_zwpixel_im;
    t__h_zwpixel_re = t__h_zwpixel_im = 0.0;
}

/* variable declarations */
%(var_inits)s
int t__h_numiter = 0;

%(t_transform)s

%(init)s

%(cf0_init)s

%(cf1_init)s
do
{
    %(loop)s

    %(loop_inserts)s
    %(bailout)s

    %(bailout_inserts)s
    if(!%(bailout_var)s) break;
    %(cf0_loop)s

    %(cf1_loop)s

    t__h_numiter++;
}while(t__h_numiter < maxiter);

/* fate of 0 = escaped, 1 = trapped */
t__h_inside = (t__h_numiter >= maxiter);

%(pre_final_inserts)s
%(final)s

%(done_inserts)s

*t__p_pnIters = t__h_numiter;
if(t__h_inside == 0)
{
    %(cf0_final)s
        ;
}
else
{
    %(cf1_final)s
        ;
}
*t__p_pFate = t__h_fate | (t__h_inside ? FATE_INSIDE : 0);
*t__p_pDist = t__h_index;
*t__p_pSolid = t__h_solid;
%(save_colors)s
%(return_inserts)s
return;
}


static void pf_calc_period(
    // "object" pointer
    struct s_pf_data *t__p_stub,
    // in params
    const double *t__params, int maxiter, int t__warp_param,
    // only used for debugging
    int t__p_x, int t__p_y, int t__p_aa,
    // out params
    int *t__p_pnIters, int *t__p_pFate, double *t__p_pDist, int *t__p_pSolid,
    int *t__p_pDirectColorFlag, double *t__p_pColors
    )
{
    pf_real *t__pfo = (pf_real *)t__p_stub;

double pixel_re = t__params[0];
double pixel_im = t__params[1];
double t__h_zwpixel_re = t__params[2];
double t__h_zwpixel_im = t__params[3];

double t__h_index = 0.0;
int t__h_solid = 0;
int t__h_fate = 0;
int t__h_inside = 0;
double t__h_color_re = 0.0;
double t__h_color_i = 0.0;
double t__h_color_j = 0.0;
double t__h_color_k = 0.0;

*t__p_pDirectColorFlag = %(dca_init)s;

if(t__warp_param != -1)
{
    t__pfo->p[t__warp_param].doubleval = t__h_zwpixel_re;
    t__pfo->p[t__warp_param+1].doubleval = t__h_zwpixel_im;
    t__h_zwpixel_re = t__h_zwpixel_im = 0.0;
}

/* variable declarations */
%(var_inits)s
%(decl_period)s
int t__h_numiter = 0;

%(t_transform)s

%(init)s
%(cf0_init)s
%(cf1_init)s

%(init_period)s
do
{
    %(loop)s

    %(loop_inserts)s
    %(bailout)s

    %(bailout_inserts)s
    if(!%(bailout_var)s) break;
    %(check_period)s   
    %(cf0_loop)s
    %(cf1_loop)s

    t__h_numiter++;
}while(t__h_numiter < maxiter);

/* fate of 0 = escaped, 1 = trapped */
t__h_inside = (t__h_numiter >= maxiter);

%(pre_final_inserts)s
%(final)s
%(done_inserts)s

*t__p_pFate = (t__h_numiter >= maxiter);
*t__p_pnIters = t__h_numiter;
if(t__h_inside == 0)
{
    %(cf0_final)s
        ;
}
else
{
    %(cf1_final)s
        ;
}
*t__p_pFate = t__h_fate | (t__h_inside ? FATE_INSIDE : 0);
*t__p_pDist = t__h_index;
*t__p_pSolid = t__h_solid;
%(save_colors)s
%(return_inserts)s
return;
}

static void pf_kill(
    struct s_pf_data *p_stub)
{
    free(p_stub);
}

static struct s_pf_vtable vtbl = 
{
    pf_init,
    pf_calc,
    pf_calc_period,
    pf_kill
};

pf_obj *pf_new()
{
    pf_obj *p = (pf_obj *)malloc(sizeof(pf_real));
    if(!p) return NULL;
    p->vtbl = &vtbl;
    return p;
}

%(main_inserts)s
'''

        # we insert pf.h so C compiler doesn't have to find it
        # this needs to be updated each time pf.h changes
        self.pf_header= '''
#ifndef PF_H_
#define PF_H_


/* C signature of point-funcs generated by compiler 
   
   This is essentially an opaque object with methods implemented in C. 
   Typical usage:

   //#pixel.re, #pixel.im, #z.re, #z.im 
   double pparams[] = { 1.5, 0.0, 0.0, 0.0};
   double initparams[] = {5.0, 2.0};
   int nItersDone=0;
   int nFate=0;
   double dist=0.0;
   int solid=0;
   pf_obj *pf = pf_new();
   pf->vtbl->init(pf,0.001,initparams,2);
   
   pf->vtbl->calc(
        pf,
        pparams,
        100,
        0,0,0,
        &nItersDone, &nFate, &dist, &solid);
   
   pf->vtbl->kill(pf);
*/

// maximum number of params which can be passed to init
#define PF_MAXPARAMS 200

// number of positional params used
#define N_PARAMS 11

/* the 'fate' of a point. This can be either
   Unknown (255) - not yet calculated
   N - reached an attractor numbered N (up to 30)
   N | FATE_INSIDE - did not escape
   N | FATE_SOLID - color with solid color 
   N | FATE_DIRECT - color with DCA
*/

typedef unsigned char fate_t;

#define FATE_UNKNOWN 255
#define FATE_SOLID 0x80
#define FATE_DIRECT 0x40
#define FATE_INSIDE 0x20

typedef enum
{
    INT = 0,
    FLOAT = 1,
    GRADIENT = 2
} e_paramtype;

struct s_param
{
    e_paramtype t;
    int intval;
    double doubleval;
    void *gradient;
};

struct s_pf_data;

struct s_pf_vtable {
    /* fill in fields in pf_data with appropriate stuff */
    void (*init)(
	struct s_pf_data *p,
        double period_tolerance,
	double *pos_params,
        struct s_param *params,
	int nparams
	);

    /* calculate one point.
       perform up to nIters iterations,
       return:
       number of iters performed in pnIters
       outcome in pFate: 0 = escaped, 1 = trapped. 
       More fates may be generated in future
       dist : index into color table from 0.0 to 1.0
    */
    void (*calc)(
	struct s_pf_data *p,
        // in params
        const double *params, int nIters, int warp_param,
	// only used for debugging
	int x, int y, int aa,
        // out params
        int *pnIters, int *pFate, double *pDist, int *pSolid,
	int *pDirectColorFlag, double *pColors
	);
    /* calculate one point, using periodicity checking */
    void (*calc_period)(
	struct s_pf_data *p,
        // in params
        const double *params, int nIters, int warp_param,
	// only used for debugging
	int x, int y, int aa,
        // out params
        int *pnIters, int *pFate, double *pDist, int *pSolid,
	int *pDirectColorFlag, double *pColors
	);
    /* deallocate data in p */
    void (*kill)(
	struct s_pf_data *p
	);
} ;

struct s_pf_data {
    struct s_pf_vtable *vtbl;
} ;

typedef struct s_pf_vtable pf_vtable;
typedef struct s_pf_data pf_obj;

/* create a new pf_obj.*/

#ifdef __cplusplus
extern "C" {
#endif
 
extern pf_obj *pf_new(void);

#ifdef __cplusplus
}
#endif

#endif /* PF_H_ */
'''

    def emit_binop(self,op,srcs,type):
        dst = self.newTemp(type)

        self.out.append(Binop(op, srcs ,[ dst ], self.generate_trace))
        return dst

    def emit_func(self,op,srcs,type):
        # emit a call to C stdlib function 'op'
        dst = self.newTemp(type)
        assem = "%(d0)s = " + op + "(%(s0)s);"
        self.out.append(Oper(assem, srcs, [dst]))
        return dst

    def emit_func2(self,op,srcs,type):
        # emit a call to C stdlib function 'op'
        dst = self.newTemp(type)
        assem = "%(d0)s = " + op + "(%(s0)s,%(s1)s);"
        self.out.append(Oper(assem, srcs, [dst]))
        return dst

    def emit_func3(self,op,srcs,type):
        # emit a call to a C func which takes 3 args and returns 1
        dst = self.newTemp(type)
        assem = "%(d0)s = " + op + "(%(s0)s,%(s1)s,%(s2)s);"
        self.out.append(Oper(assem,srcs, [dst]))
        return dst

    def emit_func3_3(self,op,srcs,type):
        # emit a call to a C func which takes 3 args and returns 3 out params
        # This rather specialized feature is to call hls2rgb
        dst = [
            self.newTemp(type),
            self.newTemp(type),
            self.newTemp(type)]
        assem = op + "(%(s0)s,%(s1)s,%(s2)s, &%(d0)s, &%(d1)s, &%(d2)s);"
        self.out.append(Oper(assem,srcs, dst))
        return dst

    def emit_func2_3(self,op,srcs,type):
        # take 2 objects and return 3, as in gradient func
        dst = [
            self.newTemp(type),
            self.newTemp(type),
            self.newTemp(type)]
        assem = op + "(%(s0)s,%(s1)s, &%(d0)s, &%(d1)s, &%(d2)s);"
        self.out.append(Oper(assem,srcs, dst))
        return dst

    def emit_func0_2(self,op,srcs,type):
        # take 0 objects and return 2, as in random()
        dst = [
            self.newTemp(type),
            self.newTemp(type)]
        assem = op + "(&%(d0)s, &%(d1)s);"
        self.out.append(Oper(assem,srcs, dst))
        return dst
        
    def emit_move(self, src, dst):
        self.out.append(Move([src],[dst], self.generate_trace))

    def emit_cjump(self, test,dst):
        assem = "if(%(s0)s) goto " + dst + ";"
        self.out.append(Oper(assem, [test], []))

    def emit_jump(self, dst):
        assem = "goto %s;" % dst
        self.out.append(Oper(assem,[],[],[dst]))

    def emit_label(self,name):
        self.out.append(Label(name))

    def get_var(self,name):
        temp_ir = ir.Var(name, absyn.Empty(0), fracttypes.Gradient)
        var = self.var(temp_ir)
        return var

    def make_complex_init(self,type,varname, re_val,im_val):
        return [ Decl("%s %s_re = %s;" % (type,varname,re_val)),
                 Decl("%s %s_im = %s;" % (type,varname,im_val))]

    def make_hyper_init(self,type,varname, vals):
        return [ Decl("%s %s_re = %s;" % (type,varname,vals[0])),
                 Decl("%s %s_i = %s;"  % (type,varname,vals[1])),
                 Decl("%s %s_j = %s;"  % (type,varname,vals[2])),
                 Decl("%s %s_k = %s;"  % (type,varname,vals[3]))]

    def is_direct(self):
        return self.symbols.has_user_key("#color")

    def output_symbol(self,key,sym,op,out,overrides):
        if isinstance(sym,fracttypes.Var):
            t = fracttypes.ctype(sym.type)
            val = sym.value
            override = overrides.get(key)
            if override == None:
                if sym.type == fracttypes.Complex:
                    ord = op.get(key)
                    if ord == None:
                        re_val = "%.17f" % val[0]
                        im_val = "%.17f" % val[1]
                        out += self.make_complex_init(t,sym.cname, re_val, im_val)
                    else:
                        re_val = "t__pfo->p[%d].doubleval" % ord
                        im_val = "t__pfo->p[%d].doubleval" % (ord+1)
                        out += self.make_complex_init(t,sym.cname, re_val, im_val)

                elif sym.type == fracttypes.Hyper or \
                     sym.type == fracttypes.Color:
                    ord = op.get(key)
                    if ord == None:
                        fval = [ "%.17f" % v for v in val]
                        out += self.make_hyper_init(t,sym.cname, fval)
                    else:
                        fval = [ "t__pfo->p[%d].doubleval" % x for x in range(ord,ord+4)]
                        out += self.make_hyper_init(t,sym.cname, fval)
                    
                elif sym.type == fracttypes.Float:
                    ord = op.get(key)
                    if ord == None:
                        out.append(Decl("%s %s = %.17f;" % (t,sym.cname,val)))
                    else:
                        out.append(Decl("%s %s = t__pfo->p[%d].doubleval;" % \
                                            (t, sym.cname, ord)))
                elif sym.type == fracttypes.Int or \
                         sym.type == fracttypes.Bool:
                    ord = op.get(key)
                    if ord == None:
                        out.append(Decl("%s %s = %d;" % (t,sym.cname,val)))
                    else:
                        out.append(Decl("%s %s = t__pfo->p[%d].intval;" % \
                                            (t, sym.cname, ord)))
                elif sym.type == fracttypes.Gradient:
                    ord = op.get(key)
                    if ord == None:
                        raise fracttypes.TranslationError(
                            "Internal Compiler Error: gradient not as a param")
                    else:
                        out.append(Decl("%s %s = t__pfo->p[%d].gradient;" % \
                                        (t, sym.cname, ord)))
                else:
                    raise ValueError("Unknown symbol type %d for %s" % \
                                     (sym.type, key))
            else:
                #print "override %s for %s" % (override, key)
                out.append(Decl(override))
        else:
            #print "Weird symbol %s: %s" %( key,sym)
            pass

    def make_complex_decl(self,type,varname):
        return [ Decl("%s %s_re;" % (type,varname)),
                 Decl("%s %s_im;" % (type,varname))]

    def make_hyper_decl(self,type,varname):
        return [ Decl("%s %s_re;" % (type,varname)),
                 Decl("%s %s_i;" % (type,varname)),
                 Decl("%s %s_j;" % (type,varname)),
                 Decl("%s %s_k;" % (type,varname))]

    def output_decl(self,key,sym,out,overrides):
        if not isinstance(sym,fracttypes.Var):
            return
        
        t = fracttypes.ctype(sym.type)
        val = sym.value
        override = overrides.get(key)
        if override == None:
            if sym.type == fracttypes.Complex:
                out += self.make_complex_decl(t,sym.cname)
            elif sym.type == fracttypes.Hyper or \
                 sym.type == fracttypes.Color:
                out += self.make_hyper_decl(t,sym.cname)
            else:
                out.append(Decl("%s %s;" % (t,sym.cname)))
        else:
            #print "override %s for %s" % (override, key)
            out.append(Decl(override))

    def output_struct_members(self,ir,user_overrides):            
        overrides = {
            "t__h_zwpixel" : "",
            "pixel" : "",
            "t__h_numiter" : "",
            "t__h_index" : "",
            "maxiter" : "",
            "t__h_tolerance" : "",
            "t__h_solid" : "",
            "t__h_color" : "",
            "t__h_fate" : "",
            "t__h_inside" : ""            
            }
        
        for (k,v) in user_overrides.items():
            overrides[k] = v
            
        out = []

        for (key,sym) in ir.symbols.items():
            self.output_decl(key,sym,out,overrides)

        if hasattr(ir,"output_sections"):
            ir.output_sections["var_decls"] = out
        return out

    def output_local_vars(self,ir,user_overrides):
        overrides = {
            "t__h_zwpixel" : "",
            "pixel" : "",
            "t__h_numiter" : "",
            "t__h_index" : "",
            "maxiter" : "",
            "t__h_tolerance" :
            "double t__h_tolerance = t__pfo->period_tolerance;",
            "t__h_solid" : "",
            "t__h_color" : "",
            "t__h_fate" : "",
            "t__h_inside" : "",
            "t__h_magn" : \
                "double t__h_magn = log(4.0/t__pfo->pos_params[4])/log(2.0) + 1.0;",
            "t__h_center" : \
                """double t__h_center_re = t__pfo->pos_params[0];
                double t__h_center_im = t__pfo->pos_params[1];"""
            }
        
        for (k,v) in user_overrides.items():
            #print "%s = %s" % (k,v)
            overrides[k] = v
            
        out = []
        op = ir.symbols.order_of_params()
        for (key,sym) in ir.symbols.items():
            self.output_symbol(key,sym,op,out,overrides)

        if hasattr(ir,"output_sections"):
            ir.output_sections["var_inits"] = out
                
        return out

    def output_section(self,t,section):
        self.out = []
        self.generate_all_code(t.canon_sections[section])
        self.emit_label("t__end_%s%s" % (t.symbols.prefix, section))
        t.output_sections[section] = self.out
    
    def output_all(self,t):
        for k in t.canon_sections.keys():
            self.output_section(t,k)

    def output_decls(self,t,overrides={}):
        # must be done after other sections or temps are missing
        self.output_local_vars(t,overrides)
        self.output_struct_members(t,overrides)

    def get_bailout_var(self,t):
        return t.symbols["__bailout"].cname
    
    def output_c(self,t,inserts={},output_template=None):
        inserts["bailout_var"] = self.get_bailout_var(t)
        inserts["pf"] = self.pf_header

        inserts["dca_init"] = "%d" % self.is_direct()

        if self.is_direct():
            inserts["save_colors"] = '''
            t__p_pColors[0] = t__h_color_re;
            t__p_pColors[1] = t__h_color_i;
            t__p_pColors[2] = t__h_color_j;
            t__p_pColors[3] = t__h_color_k;
            '''

        # can only do periodicity if formula uses z
        if self.symbols.data.has_key("z"):
            inserts["decl_period"] = '''
                double old_z_re;
                double old_z_im;
                int period_iters = 0;
                int k=1,m=1;'''
            inserts["init_period"] = '''
                old_z_re = z_re;
                old_z_im = z_im;'''

            inserts["check_period"] = '''
                if ( fabs(z_re - old_z_re) + fabs(z_im - old_z_im) <
                     t__pfo->period_tolerance)
                {
                    period_iters = t__h_numiter;
                    t__h_numiter = maxiter; break;
                }
                if(--k == 0)
                {
                    old_z_re = z_re;
                    old_z_im = z_im;
                    m *= 2;
                    k = m;
                }'''
        else:
            inserts["decl_period"]=""
            inserts["init_period"]=""
            inserts["check_period"]=""
            
        f = Formatter(self,t,inserts)
        if output_template == None:
            output_template = self.output_template
        return output_template % f

    def writeToTempFile(self,data=None,suffix=""):
        'try mkstemp or mktemp if missing'
        try:
            (fileno,cFileName) = tempfile.mkstemp(suffix,"gf4d")
            cFile = os.fdopen(fileno,"w")
        except AttributeError, err:
            # this python is too antique for mkstemp
            cFileName = tempfile.mktemp(suffix)
            cFile = open(cFileName,"w+b")

        if data != None:
            cFile.write(data)
        cFile.close()
        return cFileName

    def findOp(self,t):
        ' find the most appropriate overload for this op'
        overloadList = self.symbols[t.op]
        typelist = map(lambda n : n.datatype , t.children)
        for ol in overloadList:
            if ol.matchesArgs(typelist):
                return ol
        raise fracttypes.TranslationError(
            "Internal Compiler Error: Invalid argument types %s for %s" % \
            (typelist, opnode.leaf))

    def newTemp(self,type):
        return TempArg(self.symbols.newTemp(type),type)

    def temp(self,name,type):
        return TempArg(name,type)
    
    # action routines
    def cast(self,t):
        'Generate code to cast child of type child.datatype to t.datatype' 
        child = t.children[0]
        src = self.generate_code(child)

        dst = None
        if t.datatype == Complex:
            dst = ComplexArg(self.newTemp(Float),
                             self.newTemp(Float))
            if child.datatype == Int or child.datatype == Bool:
                assem = "%(d0)s = ((double)%(s0)s);"
                self.out.append(Oper(assem,[src], [dst.re]))
                assem = "%(d0)s = 0.0;"
                self.out.append(Oper(assem,[src], [dst.im]))
            elif child.datatype == Float:
                assem = "%(d0)s = %(s0)s;"
                self.out.append(Oper(assem,[src], [dst.re]))
                assem = "%(d0)s = 0.0;"
                self.out.append(Oper(assem,[src], [dst.im]))
        elif t.datatype == Float:
            if child.datatype == Int or child.datatype == Bool:
                dst = self.newTemp(Float)
                assem = "%(d0)s = ((double)%(s0)s);" 
                self.out.append(Oper(assem,[src], [dst]))
        elif t.datatype == Int:
            if child.datatype == Bool:
                # needn't do anything
                dst = src
        elif t.datatype == Bool:
            dst = self.newTemp(Bool)
            if child.datatype == Int or child.datatype == Bool:
                assem = "%(d0)s = (%(s0)s != 0);"
                self.out.append(Oper(assem,[src], [dst]))
            elif child.datatype == Float:
                assem = "%(d0)s = (%(s0)s != 0.0);"
                self.out.append(Oper(assem,[src], [dst]))
            elif child.datatype == Complex:
                assem = "%(d0)s = ((%(s0)s != 0.0) || (%(s1)s != 0.0));"
                self.out.append(Oper(assem,[src.re, src.im], [dst]))
            else:
                dst = None
        elif t.datatype == Hyper or t.datatype == Color:
            dst = HyperArg(self.newTemp(Float),
                           self.newTemp(Float),
                           self.newTemp(Float),
                           self.newTemp(Float))
            if child.datatype == Int or \
                   child.datatype == Bool or child.datatype == Float:
                assem = "%(d0)s = ((double)%(s0)s);"
                self.out.append(Oper(assem,[src], [dst.parts[0]]))
                assem = "%(d0)s = 0.0;"
                for i in xrange(1,4):
                    self.out.append(Oper(assem,[src], [dst.parts[i]]))
            elif child.datatype == Complex:
                assem = "%(d0)s = ((double)%(s0)s);"
                self.out.append(Oper(assem,[src.re], [dst.parts[0]]))
                self.out.append(Oper(assem,[src.im], [dst.parts[1]]))
                assem = "%(d0)s = 0.0;"
                self.out.append(Oper(assem,[src], [dst.parts[2]]))
                self.out.append(Oper(assem,[src], [dst.parts[3]]))
            else:
                dst = None
                
        if dst == None:
            msg = "%d: Invalid Cast from %s to %s" % \
                  (t.node.pos,fracttypes.strOfType(child.datatype),
                   fracttypes.strOfType(t.datatype))
            raise fracttypes.TranslationError(msg)
        
        return dst
                
    def move(self,t):
        dst = self.generate_code(t.children[0])
        src = self.generate_code(t.children[1])
        if t.datatype == Complex:
            self.emit_move(src.re,dst.re)
            self.emit_move(src.im,dst.im)
        elif t.datatype == Hyper or t.datatype == Color:
            for i in xrange(4):
                self.emit_move(src.parts[i],dst.parts[i])
        else:
            self.emit_move(src,dst)
        return dst
    
    def label(self,t):
        assert(t.children == [])
        self.emit_label(t.name)

    def cjump(self,t):
        # canonicalize has ensured we fall through to false branch,
        # so we can just deal with true case
        binop = ir.Binop(t.op,t.children,t.node,Bool)
        result = self.binop(binop)
        self.emit_cjump(result,t.trueDest)
        
    def jump(self,t):
        self.emit_jump(t.dest)

    def unop(self,t):
        s0 = t.children[0]
        src = self.generate_code(s0)
        op = self.findOp(t)
        dst = op.genFunc(self, t, [src])
        return dst

    def call(self,t):
        srcs = [self.generate_code(x) for x in t.children]
        op = self.findOp(t)
        try:
            dst = op.genFunc(self, t, srcs)
        except TypeError, err:
            msg = "Internal Compiler Error: missing stdlib function %s" % \
                  op.genFunc
            raise fracttypes.TranslationError(msg)
        
        return dst
        
    def binop(self,t):
        s0 = t.children[0]
        s1 = t.children[1]
        srcs = [self.generate_code(s0), self.generate_code(s1)]
        op = self.findOp(t)
        try:
            dst = op.genFunc(self,t,srcs)
        except TypeError, err:
            msg = "Internal Compiler Error: missing stdlib function %s" % \
                  op.genFunc
            print msg
            raise fracttypes.TranslationError(msg)
        return dst
    
    def const(self,t):
        return create_arg(t)
    
    def var(self,t):
        name = self.symbols.realName(t.name)
        if t.datatype == fracttypes.Complex:
            return ComplexArg(
                self.temp(name + "_re", fracttypes.Float),
                self.temp(name + "_im", fracttypes.Float))
        elif t.datatype == fracttypes.Hyper or t.datatype == fracttypes.Color:
            return HyperArg(
                self.temp(name + "_re", fracttypes.Float),
                self.temp(name + "_i", fracttypes.Float),
                self.temp(name + "_j", fracttypes.Float),
                self.temp(name + "_k", fracttypes.Float))
        else:
            return self.temp(name,t.datatype)
    
    # matching machinery
    def generate_all_code(self,treelist):
        for tree in treelist:
            self.generate_code(tree)
        self.optimize(self.optimize_flags)
        
    def generate_code(self,tree):
        action = self.match(tree)
        return apply(action,(self,tree))

    def expand_templates(self,list):
        return map(lambda x : [self.expand(x[0]), x[1]], list)

    def expand(self, template):
        return eval(re.sub(r'(\w+)',r'ir.\1',template))

    # implement naive tree matching. We match an ir tree against a
    # nested list of classes
    def match_template(self, tree, template):
        if isinstance(template,types.ListType):
            object = template[0]
            children = template[1:]

            if not isinstance(tree, object):
                return 0
        
            for (child, matchChild) in zip(tree.children,children):
                if not self.match_template(child,matchChild):
                    return 0
                
            return 1
        else:
            return isinstance(tree, template)
        
    def optimize(self, flags):
        optimizer = optimize.T()
        self.out = optimizer.optimize(flags, self.out)
    
    def match(self,tree):
        for (template,action) in self.templates:
            if self.match_template(tree,template):
                return action
        
        # every possible tree ought to be matched by *something* 
        msg = "Internal Compiler Error:%d:unmatched tree %s" % (tree.node.pos,tree)
        raise fracttypes.TranslationError(msg)

        
