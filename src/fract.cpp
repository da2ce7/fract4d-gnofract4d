/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
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

#include <stdlib.h>
#include <stdio.h>

#ifndef _WIN32
#include <gnome.h> // g_warning, mostly
#endif

#include "calc.h"
#include "fractFunc.h"
#include "iterFunc.h"
#include "io.h"

#include <queue>
#include <cmath>

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

#define SECTION_ITERFUNC "[function]"
#define SECTION_COLORIZER "[colors]"

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
    reset();

    // set fractal type to first type in list
    const char * const * names = iterFunc_names();
    pIterFunc = iterFunc_new(names[0]);

    // display params
    antialias = AA_FAST;
    auto_deepen = true;

    digits = 0;
	
    cizer = colorizer_new(COLORIZER_RGB);
    potential=1;
    bailout_type=BAILOUT_MAG;
}

/* dtor */
fractal::~fractal()
{
    colorizer_delete(&cizer);
    delete pIterFunc;
}

/* call destructor & set ptr to NULL */
void
fract_delete(fractal_t **fp)
{
    fractal_t *f = *fp;
    delete f;
    *fp = NULL;
}

void
fractal::copy(const fractal& f)
{
    for(int i = 0 ; i < N_PARAMS ; i++)
    {
        params[i] = f.params[i];
    }
    maxiter = f.maxiter;
    pIterFunc = f.pIterFunc->clone();
    antialias = f.antialias;
    auto_deepen = f.auto_deepen;
    digits = f.digits;
    rot_by = f.rot_by;

    rot = f.rot;

    cizer = f.cizer->clone();
    potential = f.potential;
    bailout_type = f.bailout_type;
}

/* copy ctor */
fractal::fractal(const fractal& f)
{	
    copy(f);
}

fractal&
fractal::operator=(const fractal& f)
{
    if(&f != this)
    {
        colorizer_delete(&cizer);
        delete pIterFunc;
        copy(f);
    }
    return *this;
}

// equality 
bool 
fractal::operator==(const fractal& f) 
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

    if(!(*cizer == *f.cizer)) return false;
    if(potential != f.potential) return false;
    if(bailout_type != f.bailout_type) return false;
    
    return true;
}

void 
fractal::set_fractal_type(const char *name)
{
    delete pIterFunc;
    pIterFunc = iterFunc_new(name);
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
fractal::set_inexact(const fractal& f, double weirdness)
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

/* return to mandelbrot set */
void 
fractal::reset()
{
    digits=10;
    d zero = D(0.0);
    d four = D(4.0);
    params[XCENTER] = zero;
    params[YCENTER] = zero;
    params[ZCENTER] = zero;
    params[WCENTER] = zero;
	
    params[MAGNITUDE] = four;
    params[BAILOUT] = four;
    for(int i = XYANGLE; i < ZWANGLE+1; i++) {
        params[i] = zero;
    }

    maxiter = 256;
    rot_by = M_PI/2.0;
}

colorizer_t *
fractal::get_colorizer()
{
    return cizer;
}

void
fractal::set_colorizer(colorizer_t *c)
{
    if(cizer == c) return;

    colorizer_delete(&cizer);
    cizer = c->clone();
}

static const char *param_names[] = {
    FIELD_BAILOUT,
    FIELD_X, FIELD_Y, FIELD_Z, FIELD_W, 
    FIELD_MAGNITUDE, 
    FIELD_XYANGLE, FIELD_XZANGLE, FIELD_XWANGLE, 
    FIELD_YZANGLE, FIELD_YWANGLE, FIELD_ZWANGLE,
};

bool 
fractal::write_params(const char *filename)
{
    std::ofstream os(filename);

    if(!os) return false;

    os << PACKAGE << " parameter file\n";
    os << FIELD_VERSION << "=" << VERSION << "\n";

    for(int i = 0; i < N_PARAMS; i++) {
        os << param_names[i] << "=" << params[i] << "\n";
    }

    os << FIELD_MAXITER << "=" << maxiter << "\n";
    os << FIELD_AA << "=" << (int) antialias << "\n";
    os << FIELD_BAILFUNC << "=" << (int) bailout_type << "\n";
    os << SECTION_ITERFUNC << "\n" << *pIterFunc;
    os << SECTION_COLORIZER << "\n" << *cizer;

    if(!os) return false;
    return true;
}

bool
fractal::load_params(const char *filename)
{
    std::ifstream is(filename);

    if(!is) return false;

    while(is)
    {
        std::string name, val;

        if(!read_field(is,name,val))
        {
            break;
        }
        std::istrstream vs(val.c_str());

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
            vs >> (int&)bailout_type;
        else if(SECTION_ITERFUNC==name)
        {
            iterFunc *iter_tmp = iterFunc_read(is);
            if(iter_tmp)
            {
                delete pIterFunc;
                pIterFunc = iter_tmp;
            }
        }
        else if(SECTION_COLORIZER==name)
        {
            colorizer *cizer_tmp = colorizer_read(is);
            if(cizer_tmp)
            {
                colorizer_delete(&cizer);
                cizer = cizer_tmp;
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
fractal::get_max_iterations()
{
    return maxiter;
}

void 
fractal::set_aa(e_antialias val)
{

    antialias = val;
}

e_antialias
fractal::get_aa()
{
    return antialias;
}

void 
fractal::set_auto(bool val)
{
    auto_deepen = val;
}

bool 
fractal::get_auto()
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
    // assume image < 1024 pixels wide
    d delta = (params[MAGNITUDE])/D_LIKE(1024.0,params[MAGNITUDE]);

    debug_precision(params[MAGNITUDE],"check precision");

#ifdef HAVE_CLN
    if (delta < float_epsilon(cl_float_format(params[MAGNITUDE]))*D_LIKE(10.0,params[MAGNITUDE])) { 
        g_print("increasing precision from %d\n",float_digits(delta)); 
        // float_digits gives bits of precision,
        // cl_float takes decimal digits. / by 3 should be safe?
        set_precision(float_digits(delta)/3 +4);
        return false;
    }
#else

    if ( delta < 1.0e-15)
    {
        // precision lost, but don't do anything - user will notice anyway
        return false;
    }	
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
fractal::get_param(param_t pnum)
{
    D2ADECL;
    if(pnum < 0 || pnum >= N_PARAMS) return NULL;
    return D2A(params[pnum]);
}

void
fractal::update_matrix()
{
    debug_precision(params[XYANGLE],"xyangle");
    d one = D_LIKE(1.0,params[MAGNITUDE]);
    d zero = D_LIKE(0.0, params[MAGNITUDE]);
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
    d dx = D_LIKE(x,params[MAGNITUDE]);
    d dy = D_LIKE(y,params[MAGNITUDE]);  

    update_matrix();
    deltax=rot[VX];
    deltay=rot[VY];

    debug_precision(deltax[VX],"relocate:deltax");
    recenter(dx *deltax + dy *deltay);

    debug_precision(params[MAGNITUDE],"relocate 1");

    params[MAGNITUDE] /= D_LIKE(zoom,params[MAGNITUDE]);

    debug_precision(params[MAGNITUDE],"relocate 2");

    check_precision();

}	

void
fractal::flip2julia(double x, double y)
{
    relocate(x,y,1.0);
	
    params[XZANGLE] += D_LIKE(rot_by,params[MAGNITUDE]);
    params[YWANGLE] += D_LIKE(rot_by,params[MAGNITUDE]);

    rot_by = -rot_by;
}

void
fractal::move(param_t i, int direction)
{
    int axis;

    double d = (double)direction;

    switch(i){
    case XCENTER: axis = VX; break;
    case YCENTER: axis = VY; break;
	/* z & w axes have a more dramatic visual effect */
    case ZCENTER: axis = VZ; d *= 0.5; break;
    case WCENTER: axis = VW; d *= 0.5; break;
    default: return;
    }
    update_matrix();
    dvec4 delta = d * rot[axis] * (1.0 / 20.0);
    recenter(delta);
}

void
fractal::calc(Gf4dFractal *gf, image *im)
{
    fractFunc pr(this, im, gf);

    gf4d_fractal_status_changed(gf,GF4D_FRACTAL_CALCULATING);

    pr.draw(8,8);

    while(pr.updateiters())
    {
        gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DEEPENING);
        pr.draw(8,1);
    }
	
    if(antialias > AA_NONE) {
        gf4d_fractal_status_changed(gf,GF4D_FRACTAL_ANTIALIASING);
        pr.draw_aa();
    }
	
    gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DONE);
    gf4d_fractal_progress_changed(gf,0.0);
}

void 
fractal::recolor(image *im)
{
    int width = im->Xres;
    int height = im->Yres;
    for( int i = 0 ; i < height; ++i)
    {
        for( int j = 0; j < width; ++j)
        {
            // fake scratch space
            scratch_space s= { 0.0 };
            rgb_t result = (*cizer)(im->iter_buf[i * width + j ], s, false);
            im->put(j,i,result);
        }
    }
}
