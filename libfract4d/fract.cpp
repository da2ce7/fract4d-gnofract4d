/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <stdlib.h>
#include <stdio.h>

#include "calc.h"
#include "fractFunc.h"
#include "iterFunc.h"
#include "bailFunc.h"
#include "io.h"

#include <queue>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <iostream>

#ifdef _WIN32
#include "win_drand.h"
#endif

#define FIELD_VERSION "version"
#define FIELD_X "x"
#define FIELD_Y "y"
#define FIELD_Z "z"
#define FIELD_W "w"
#define FIELD_XYANGLE "xy"
#define FIELD_XZANGLE "xz"
#define FIELD_XWANGLE "xw"
#define FIELD_YZANGLE "yz"
#define FIELD_YWANGLE "yw"
#define FIELD_ZWANGLE "zw"
#define FIELD_MAGNITUDE "size"
#define FIELD_BAILOUT "bailout"

#define FIELD_MAXITER "maxiter"
#define FIELD_AA "antialias"
#define FIELD_BAILFUNC "bailfunc"

#define FIELD_INNER "inner"
#define FIELD_OUTER "outer"

#define FIELD_CTF "transfer"

#define SECTION_ITERFUNC "[function]"
#define SECTION_LEGACY_COLORIZER "[colors]"
#define SECTION_COLORIZER "[colorizer]"
#define SECTION_BAILFUNC "[bailout]"

void 
debug_precision(const d& s, char *location)
{
#if !defined(NDEBUG) && defined(HAVE_CLN)
    ostrstream os;
    os << float_epsilon(cl_float_format(s)) << std::ends;
    g_print("%s : %s\n",location,os.str());
#endif
}

/* ctor */
fractal::fractal()
{
    // set fractal type to first type in list
    const char **names = iterFunc::names();
    pIterFunc = iterFunc::create(names[0]);

    reset();

    // display params
    antialias = AA_FAST;
    auto_deepen = true;

    digits = 0;
	
    cizers = new colorizer *[N_COLORFUNCS];
    for(int i = 0; i < N_COLORFUNCS; ++i)
    {
	cizers[i] = colorizer_new(COLORIZER_RGB);
    }

    bailout_type=bailFunc::create(BAILOUT_MAG);

    colorFuncs[OUTER]=COLORFUNC_CONT;
    colorFuncs[INNER]=COLORFUNC_ZERO;

    colorTransferFuncs[OUTER]="Linear"; //PseudoLog";
    colorTransferFuncs[INNER]="Linear";

    assert(bailout_type > (void *)0x4);
}

/* dtor */
fractal::~fractal()
{
    delete[] cizers;
    delete pIterFunc;
    delete bailout_type;
}


IFractal *IFractal::create()
{
    return new fractal();
}

void
fractal::copy(const fractal& f)
{
    for(int i = 0 ; i < N_PARAMS ; i++)
    {
        params[i] = f.params[i];
    }
    maxiter = f.maxiter;

    set_iterFunc(f.pIterFunc);

    antialias = f.antialias;
    auto_deepen = f.auto_deepen;
    digits = f.digits;
    rot_by = f.rot_by;

    rot = f.rot;

    for(int i = 0; i < N_COLORFUNCS; ++i)
    {
	set_colorizer(f.cizers[i],i);
        colorFuncs[i] = f.colorFuncs[i];
	colorTransferFuncs[i] = f.colorTransferFuncs[i];
    }
    set_bailType(f.get_bailType());
}

/* copy ctor */
IFractal *fractal::clone()
{
    return new fractal(*this);
}

fractal::fractal(const fractal& f)
{	
    // ensure these are initialized to something that is
    // safe to be deleted
    pIterFunc = NULL;
    cizers = new colorizer *[N_COLORFUNCS];
    for(int i = 0; i < N_COLORFUNCS; ++i)
    {
	cizers[i] = NULL;
    }
    bailout_type = NULL;

    copy(f);
}

fractal&
fractal::operator=(const fractal& f)
{
    if(&f != this)
    {
        copy(f);
    }
    return *this;
}

IFractal&
fractal::operator=(const IFractal& f)
{
    operator=((fractal&)f);

    return *this;
}

bool
fractal::operator==(const IFractal& f) const
{
    return *this == (fractal&)f;
}

// equality 
bool 
fractal::operator==(const fractal& f) const
{
    for(int i = 0 ; i < N_PARAMS ; i++)
    {
        if(params[i] != f.params[i]) return false;
    }
    if(maxiter != f.maxiter) return false;
    if(!(*pIterFunc == *f.pIterFunc)) return false;
    if(antialias != f.antialias) return false;
    if(auto_deepen != f.auto_deepen) return false;
    if(digits != f.digits) return false;
    if(rot_by != f.rot_by) return false;

    for(int i = 0; i < N_COLORFUNCS; ++i)
    {
	if(!(*cizers[i] == *f.cizers[i])) return false;
	if(colorFuncs[i] != f.colorFuncs[i]) return false;
	if(colorTransferFuncs[i] != f.colorTransferFuncs[i]) return false;
    }

    if(bailout_type->type() != f.bailout_type->type()) return false;
    
    return true;
}

void 
fractal::set_fractal_type(const char *name)
{
    delete pIterFunc;
    pIterFunc = iterFunc::create(name);

    assert(pIterFunc > (void *)0x1000);
    pIterFunc->reset(params);
    set_bailType(pIterFunc->preferred_bailfunc());
}

/* x & y vary by up to 50% of the MAGNITUDE */

static double
xy_random(double weirdness, double MAGNITUDE)
{
    return weirdness * 0.5 * MAGNITUDE * (drand48() - 0.5);
}

/* z & w vary by up to 1.0 / log(MAGNITUDE) 
   small MAGNITUDE = gradually diminishing changes 
*/

static double
zw_random(double weirdness, double MAGNITUDE)
{
    double factor = fabs(1.0 - log(MAGNITUDE)) + 1.0;
    return weirdness * (drand48() - 0.5 ) * 1.0 / factor;
}

/* scale independent, but skewed distribution */

static double
angle_random(double weirdness)
{
    double action = drand48();
    if(action > weirdness) return 0.0; // no change

    action = drand48();
    if(action < weirdness/6.0) 
    {
        // +/- pi/2
        return drand48() > 0.5 ? M_PI/2.0 : -M_PI/2.0;
    }
    return weirdness * (drand48() - 0.5) * M_PI/2.0;
}

void
fractal::set_inexact(const IFractal& f, double weirdness)
{
    *this = f; // invoke op=
    
    params[XCENTER] += xy_random(weirdness, params[MAGNITUDE]);
    params[YCENTER] += xy_random(weirdness, params[MAGNITUDE]);
    params[ZCENTER] += zw_random(weirdness, params[MAGNITUDE]);
    params[WCENTER] += zw_random(weirdness, params[MAGNITUDE]);

    for(int i = XYANGLE; i <= ZWANGLE ; i++)
    {	       
        params[i] += angle_random(weirdness);
    }
	
    if(drand48() < weirdness * 0.75)
    {
        params[MAGNITUDE] *= 1.0 + (0.5 - drand48());
    }
}

void 
fractal::set_mixed(const IFractal& if1, const IFractal& if2, double lambda)
{
    *this = if1; 

    // FIXME - doesn't deal with mixed types etc
    const fractal *f1 = (const fractal *)&if1;
    const fractal *f2 = (const fractal *)&if2;

    // FIXME: fix this to go round the short way for angles
    double nl = 1.0 - lambda;
    for(int i = 0 ; i < N_PARAMS; ++i)
    {
        params[i] = lambda * f1->params[i] + nl * f2->params[i];
    }
    maxiter = (int)(lambda * f1->maxiter + nl * f2->maxiter);
    
}

/* return to default parameters for this fractal type */
void 
fractal::reset()
{
    maxiter = 256;
    rot_by = M_PI/2.0;
    
    assert(pIterFunc != NULL);
    if(pIterFunc)
    {
        pIterFunc->reset(params);
    }
    else
    {
        // FIXME: probably not needed?
        params[XCENTER] = 0.0;
        params[YCENTER] = 0.0;
        params[ZCENTER] = 0.0;
        params[WCENTER] = 0.0;
	
        params[MAGNITUDE] = 4.0;
        params[BAILOUT] = 4.0;
        for(int i = XYANGLE; i < ZWANGLE+1; i++) {
            params[i] = 0.0;
        }
    }
}

int 
fractal::get_active_colorizers() const
{
    return 1 << pIterFunc->nCriticalValues();
}

colorizer_t *
fractal::get_colorizer(int i) const
{
    assert(i >= 0 && i < N_COLORFUNCS);
    return cizers[i];
}

void
fractal::set_colorizer(colorizer_t *c, int i)
{
    assert(i >= 0 && i < N_COLORFUNCS);
    if(cizers[i] == c) return;

    delete cizers[i];
    cizers[i] = c->clone();
}

static const char *param_names[] = {
    FIELD_BAILOUT,
    FIELD_X, FIELD_Y, FIELD_Z, FIELD_W, 
    FIELD_MAGNITUDE, 
    FIELD_XYANGLE, FIELD_XZANGLE, FIELD_XWANGLE, 
    FIELD_YZANGLE, FIELD_YWANGLE, FIELD_ZWANGLE,
};

bool 
fractal::write_params(const char *filename) const
{
    std::ofstream os(filename);

    os << std::setprecision(20);

    if(!os) return false;

    os << PACKAGE << " parameter file\n";
    os << FIELD_VERSION << "=" << VERSION << "\n";

    for(int i = 0; i < N_PARAMS; i++) {
        os << param_names[i] << "=" << params[i] << "\n";
    }

    os << FIELD_MAXITER << "=" << maxiter << "\n";
    os << FIELD_AA << "=" << (int) antialias << "\n";
    os << FIELD_BAILFUNC << "=" << (int) bailout_type->type() << "\n";
    os << FIELD_INNER << "=" << (int) colorFuncs[INNER] << "\n";
    os << FIELD_OUTER << "=" << (int) colorFuncs[OUTER] << "\n";
    os << SECTION_ITERFUNC << "\n" << *pIterFunc;
    for(int i = 0; i < N_COLORFUNCS; ++i)
    {
	os << SECTION_COLORIZER << "=" << i << "\n";
	os << *cizers[i];
    }
    if(!os) return false;
    return true;
}

bool
fractal::load_params(const char *filename)
{
    std::ifstream is(filename);

    if(!is) return false;

    // default cfuncs because old files don't override
    colorFuncs[INNER] = COLORFUNC_ZERO;
    colorFuncs[OUTER] = COLORFUNC_CONT;

    while(is)
    {
        std::string name, val;

        if(!read_field(is,name,val))
        {
            break;
        }
        std::istringstream vs(val.c_str());


        if(FIELD_VERSION==name)
            ; // do nothing with it for now
        else if(FIELD_BAILOUT==name)
            vs >> params[BAILOUT];
        else if(FIELD_X==name)
            vs >> params[XCENTER];
        else if(FIELD_Y==name)
            vs >> params[YCENTER];
        else if(FIELD_Z==name)
            vs >> params[ZCENTER];
        else if(FIELD_W==name)
            vs >> params[WCENTER];
        else if(FIELD_XYANGLE==name)
            vs >> params[XYANGLE];
        else if(FIELD_XZANGLE==name)
            vs >> params[XZANGLE];
        else if(FIELD_XWANGLE==name)
            vs >> params[XWANGLE];
        else if(FIELD_YZANGLE==name)
            vs >> params[YZANGLE];
        else if(FIELD_YWANGLE==name)
            vs >> params[YWANGLE];
        else if(FIELD_ZWANGLE==name)
            vs >> params[ZWANGLE];
        else if(FIELD_MAGNITUDE==name)
            vs >> params[MAGNITUDE];
        else if(FIELD_MAXITER==name)
            vs >> maxiter;
        else if(FIELD_AA==name)
            vs >> (int&)antialias;
        else if(FIELD_BAILFUNC==name)
	{
	    // legacy support for old files. New ones have a bailFunc section
	    e_bailFunc bf;
            vs >> (int&)bf;
	    set_bailType(bf);
	}
        else if(FIELD_INNER==name)
            vs >> (int&)colorFuncs[INNER];
        else if(FIELD_OUTER==name)
            vs >> (int&)colorFuncs[OUTER];
        else if(SECTION_ITERFUNC==name)
        {
            iterFunc *iter_tmp = iterFunc::read(is);
            if(iter_tmp)
            {
                delete pIterFunc;
                pIterFunc = iter_tmp;
            }
        }
	else if(SECTION_COLORIZER==name)
	{
	    // section header is followed by an id, eg
	    // [colorizer]=2
	    // Unorthodox but easy...

	    int id=0;
	    vs >> id;

	    colorizer *cizer_tmp = colorizer_read(is);
            if(cizer_tmp)
            {
		set_colorizer(cizer_tmp, id);
		delete cizer_tmp;
            }
	}
        else if(SECTION_LEGACY_COLORIZER==name)
        {
	    // apply to all colorizers since old files only specify 1
            colorizer *cizer_tmp = colorizer_read(is);
            if(cizer_tmp)
            {
		for(int i = 0; i < N_COLORFUNCS; ++i)
		{
		    set_colorizer(cizer_tmp, i);
		}
		delete cizer_tmp;
            }
        }
        else if(SECTION_BAILFUNC==name)
	{
	    bailFunc *bf_tmp = bailFunc::read(is);
	    if(bf_tmp)
	    {
		delete bailout_type;
		bailout_type = bf_tmp;
	    }
	}
    }

    return true;
}

void
fractal::set_max_iterations(int val)
{
    maxiter = val;
}

int 
fractal::get_max_iterations() const
{
    return maxiter;
}

void 
fractal::set_aa(e_antialias val)
{
    antialias = val;
}

e_antialias
fractal::get_aa() const
{
    return antialias;
}

void 
fractal::set_effective_aa(e_antialias val)
{
    eaa = val;
}

e_antialias
fractal::get_effective_aa() const
{
    return eaa;
}

void 
fractal::set_auto(bool val)
{
    auto_deepen = val;
}

bool 
fractal::get_auto() const
{
    return auto_deepen;
}

bool 
fractal::set_precision(int digits)
{
#ifdef HAVE_CLN
    cl_float_format_t fmt = cl_float_format(digits);
    for(int i = 0; i < N_PARAMS; i++) {
        params[i] = cl_float(params[i],fmt);
    }

    debug_precision(params[XCENTER],"set precision:x");
    g_print("new bits of precision: %d\n",float_digits(params[MAGNITUDE]));
    if(float_digits(params[MAGNITUDE]) > 53)
    {
        fractal_type = 1;
    } else {
        fractal_type = 0;
    }
    return 1;
#else
    return 0;
#endif
}

/* see if we have run out of precision. either extend float format or 
 * (if CLN isn't available) warn user 
 */
bool
fractal::check_precision()
{
#ifdef HAVE_GMP

    gmp::f delta(params[MAGNITUDE]);

    int bits = delta.prec();

    g_print("precision: %d\n",bits);
#endif
    return true;
}

bool 
fractal::set_param(param_t pnum, const char *val)
{
    if(pnum < 0 || pnum >= N_PARAMS) return false;
    params[pnum] = A2D(val);
    return true;
}

char *
fractal::get_param(param_t pnum) const
{
    D2ADECL;
    if(pnum < 0 || pnum >= N_PARAMS) return NULL;
    return D2A(params[pnum]);
}

void
fractal::update_matrix()
{
    debug_precision(params[XYANGLE],"xyangle");
    d one = D(1.0);
    d zero = D(0.0);
    dmat4 id = identity3D<d>(params[MAGNITUDE],zero);

    debug_precision(id[VX][VY],"id 1");

    rot =  id * 
        rotXY<d>(params[XYANGLE],one,zero) *
        rotXZ<d>(params[XZANGLE],one,zero) * 
        rotXW<d>(params[XWANGLE],one,zero) *
        rotYZ<d>(params[YZANGLE],one,zero) *
        rotYW<d>(params[YWANGLE],one,zero) *
        rotZW<d>(params[ZWANGLE],one,zero);

    debug_precision(rot[VX][VY],"id 3");
}

dvec4 
fractal::get_center()
{
    return dvec4(params[XCENTER],params[YCENTER],
                 params[ZCENTER],params[WCENTER]);
}

void
fractal::recenter(const dvec4& delta)
{
    debug_precision(params[XCENTER],"recenter 1:x");
    params[XCENTER] += delta.n[VX];
    params[YCENTER] += delta.n[VY];
    params[ZCENTER] += delta.n[VZ];
    params[WCENTER] += delta.n[VW];
    debug_precision(params[XCENTER],"recenter 2:x");
}

void
fractal::relocate(double x, double y, double zoom)
{
    dvec4 deltax,deltay;

    // offset to clicked point from center
    d dx(x);
    d dy(y);

    update_matrix();
    deltax=rot[VX];
    deltay=rot[VY];

    debug_precision(deltax[VX],"relocate:deltax");
    recenter(dx *deltax + dy *deltay);

    debug_precision(params[MAGNITUDE],"relocate 1");

    params[MAGNITUDE] /= D(zoom);

    debug_precision(params[MAGNITUDE],"relocate 2");

    check_precision();

}	

void
fractal::flip2julia(double x, double y)
{
    relocate(x,y,1.0);
	
    params[XZANGLE] += rot_by;
    params[YWANGLE] += rot_by;

    rot_by = -rot_by;
}

void
fractal::move(param_t i, double dist)
{
    int axis;

    switch(i){
    case XCENTER: axis = VX; break;
    case YCENTER: axis = VY; break;
	/* z & w axes have a more dramatic visual effect */
    case ZCENTER: axis = VZ; dist *= 0.5; break;
    case WCENTER: axis = VW; dist *= 0.5; break;
    default: return;
    }
    update_matrix();
    dvec4 delta = D(dist) * rot[axis];
    recenter(delta);
}

void
fractal::calc(IFractalSite *site, IImage *im)
{    
    if(eaa == AA_DEFAULT) 
    {
        eaa = antialias;
    }

    IFractWorker *worker = IFractWorker::create(nThreads,this,im);

    if(worker->ok())
    {
	site->status_changed( GF4D_FRACTAL_CALCULATING);
	fractFunc pr(this, worker, im, site);
    
	if(pr.ok)
	{
	    pr.draw_all();
	}
    }
    site->status_changed(GF4D_FRACTAL_DONE);    

    delete worker;
}

void 
fractal::recolor(IImage *im)
{
    pointFunc *p = pointFunc::create(
        pIterFunc,
        bailout_type,
        params[BAILOUT],
        tolerance(im),
        cizers,
        colorFuncs[OUTER],
        colorFuncs[INNER],
	colorTransferFuncs[OUTER],
	colorTransferFuncs[INNER]);

    int width = im->Xres();
    int height = im->Yres();
    for( int i = 0 ; i < height; ++i)
    {
        for( int j = 0; j < width; ++j)
        {
	    void *buf=im->getData(i,j);
            rgb_t result = p->recolor(im->getIter(i,j),params[BAILOUT],buf);
            im->put(i,j,result);
        }
    }

    delete p;
}

d 
fractal::tolerance(IImage *im)
{
    // 10% of the size of a pixel
    d t = params[MAGNITUDE]/(2 * std::max(im->Xres(),im->Yres()) * 10.0);
    return t;
}

e_bailFunc
fractal::get_bailType() const
{
    assert(bailout_type > (void *)0x4);
    return bailout_type->type();
}

void
fractal::set_bailType(e_bailFunc bf)
{
    delete bailout_type;
    bailout_type = bailFunc::create(bf);
    assert(bailout_type > (void *)0x4);
}

bailFunc *
fractal::get_bailFunc() const
{
    return bailout_type;
}

void 
fractal::set_colorFunc(e_colorFunc cf, int which_cf)
{
    assert(which_cf >= 0 && which_cf < N_COLORFUNCS);
    colorFuncs[which_cf] = cf;
}

e_colorFunc 
fractal::get_colorFunc(int which_cf) const
{
    assert(which_cf >= 0 && which_cf < N_COLORFUNCS);
    return colorFuncs[which_cf];
}

void 
fractal::set_colorTransferFunc(const char *name, int which_cf)
{
    assert(which_cf >= 0 && which_cf < N_COLORFUNCS);
    colorTransferFuncs[which_cf] = name;
}

const char *
fractal::get_colorTransferFunc(int which_cf) const
{
    assert(which_cf >= 0 && which_cf < N_COLORFUNCS);
    return colorTransferFuncs[which_cf];
}

void
fractal::set_threads(int n)
{
    assert(n >= 0);
    nThreads = n;
}

int 
fractal::get_threads() const
{
    return nThreads;
}

iterFunc *
fractal::get_iterFunc() const
{
    assert(pIterFunc != NULL);
    return pIterFunc;
}

void 
fractal::set_iterFunc(const iterFunc *f)
{
    assert(f != NULL);
    if(f == pIterFunc) return;
    delete pIterFunc;
    pIterFunc = f->clone();
    assert(pIterFunc != NULL);
}
