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

#include <gnome.h> // g_warning, mostly
#include "calc.h"
#include "fractFunc.h"
#include "iterFunc.h"

#include <fstream>
#include <queue>

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

    // set fractal type to Mset
    pIterFunc = iterFunc_new(0);

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
    if(*pIterFunc != *f.pIterFunc) return false;
    if(antialias != f.antialias) return false;
    if(auto_deepen != f.auto_deepen) return false;
    if(digits != f.digits) return false;
    if(rot_by != f.rot_by) return false;

    if(*cizer != *f.cizer) return false;
    if(potential != f.potential) return false;
    if(bailout_type != f.bailout_type) return false;
    
    return true;
}

void 
fractal::set_fractal_type(int type)
{
    delete pIterFunc;
    pIterFunc = iterFunc_new(type);
}

/* x & y vary by up to 50% of the size */

static double
xy_random(double weirdness, double size)
{
    return weirdness * 0.5 * size * (drand48() - 0.5);
}

/* z & w vary by up to 1.0 / log(size) 
   small size = gradually diminishing changes 
*/

static double
zw_random(double weirdness, double size)
{
    double factor = fabs(1.0 - log(size)) + 1.0;
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
    
    params[XCENTER] += xy_random(weirdness, params[SIZE]);
    params[YCENTER] += xy_random(weirdness, params[SIZE]);
    params[ZCENTER] += zw_random(weirdness, params[SIZE]);
    params[WCENTER] += zw_random(weirdness, params[SIZE]);

    for(int i = XYANGLE; i <= ZWANGLE ; i++)
    {	       
        params[i] += angle_random(weirdness);
    }
	
    if(drand48() < weirdness * 0.75)
    {
        params[SIZE] *= 1.0 + (0.5 - drand48());
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
	
    params[SIZE] = four;
    params[BAILOUT] = four;
    for(int i = XYANGLE; i < ZWANGLE+1; i++) {
        params[i] = zero;
    }

    maxiter = 64;
    rot_by = M_PI/2.0;
}

e_colorizer
fractal::get_color_type()
{
    return cizer->type();
}

void
fractal::set_color_type(e_colorizer type)
{
    if(type == cizer->type()) return;

    colorizer_delete(&cizer);
    cizer = colorizer_new(type);
}

void
fractal::set_cmap_file(const char *filename)
{
    cmap_colorizer *cmap_cizer = dynamic_cast<cmap_colorizer *>(cizer);
    if(cmap_cizer)
    {
        if(strcmp(cmap_cizer->name.c_str(),filename)==0)
        {
            return; // already set to same file
        }
        cmap_cizer->set_cmap_file(filename);
    }
    else
    {
        g_warning("set_cmap_file on non-cmap colorizer");
    }
}

char *
fractal::get_cmap_file()
{
    cmap_colorizer *cmap_cizer = dynamic_cast<cmap_colorizer *>(cizer);
    if(!cmap_cizer) return NULL;
    return g_strdup(cmap_cizer->name.c_str());
}

bool 
fractal::write_params(const char *filename)
{
    std::ofstream os(filename);

    if(!os) return false;

    for(int i = 0; i < N_PARAMS; i++) {
        os << params[i] << "\n";
    }

    os << maxiter << "\n";
    os << *pIterFunc << "\n";
    os << (int) antialias << "\n";
    os << *cizer << "\n";
    os << (int) bailout_type << "\n";

    if(!os) return false;
    return true;
}

bool
fractal::load_params(const char *filename)
{
    std::ifstream is(filename);

    if(!is) return false;

    for(int i = 0; i < N_PARAMS; i++) {
        is >> params[i];
    }

    is >> maxiter;
    // cast is to quiet a curious compiler warning
    iterFunc *iter_tmp = iterFunc_read(is);
    if(iter_tmp)
    {
        delete pIterFunc;
        pIterFunc = iter_tmp;
    }
    is >> (int&)antialias;
    colorizer *cizer_tmp = colorizer_read(is);
    if(cizer_tmp)
    {
        colorizer_delete(&cizer);
        cizer = cizer_tmp;
    }
    is >> (int&)bailout_type;

    if(!is) return false;

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

void 
fractal::set_color(double _r, double _g, double _b)
{
    rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
    if(!rgb_cizer) return;
    rgb_cizer->set_colors(_r,_g,_b);
}

double 
fractal::get_r()
{
    rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
    if(!rgb_cizer) return 0.0;
    return rgb_cizer->r;
}

double 
fractal::get_g()
{
    rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
    if(!rgb_cizer) return 0.0;
    return rgb_cizer->g;
}

double 
fractal::get_b()
{
    rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
    if(!rgb_cizer) return 0.0;
    return rgb_cizer->b;
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
    g_print("new bits of precision: %d\n",float_digits(params[SIZE]));
    if(float_digits(params[SIZE]) > 53)
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
    d delta = (params[SIZE])/D_LIKE(1024.0,params[SIZE]);

    debug_precision(params[SIZE],"check precision");

#ifdef HAVE_CLN
    if (delta < float_epsilon(cl_float_format(params[SIZE]))*D_LIKE(10.0,params[SIZE])) { 
        g_print("increasing precision from %d\n",float_digits(delta)); 
        // float_digits gives bits of precision,
        // cl_float takes decimal digits. / by 3 should be safe?
        set_precision(float_digits(delta)/3 +4);
        return false;
    }
#else
    if ( delta < 1.0e-15)
    {
        gtk_widget_show(gnome_warning_dialog(_("Sorry, max precision was reached, the image will become horrible !")));
        return false;
    }	
#endif

    return true;
}

bool 
fractal::set_param(param_t pnum, const char *val)
{
    g_return_val_if_fail(pnum > -1 && pnum < N_PARAMS,false);
    params[pnum] = A2D(val);
    return true;
}

char *
fractal::get_param(param_t pnum)
{
    D2ADECL;
    g_return_val_if_fail(pnum > -1 && pnum < N_PARAMS,NULL);
    return D2A(params[pnum]);
}

void
fractal::update_matrix()
{
    debug_precision(params[XYANGLE],"xyangle");
    d one = D_LIKE(1.0,params[SIZE]);
    d zero = D_LIKE(0.0, params[SIZE]);
    dmat4 id = identity3D<d>(params[SIZE],zero);

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
    d dx = D_LIKE(x,params[SIZE]);
    d dy = D_LIKE(y,params[SIZE]);  

    update_matrix();
    deltax=rot[VX];
    deltay=rot[VY];

    debug_precision(deltax[VX],"relocate:deltax");
    recenter(dx *deltax + dy *deltay);

    debug_precision(params[SIZE],"relocate 1");

    params[SIZE] /= D_LIKE(zoom,params[SIZE]);

    debug_precision(params[SIZE],"relocate 2");

    check_precision();

}	

void
fractal::flip2julia(double x, double y)
{
    relocate(x,y,1.0);
	
    params[XZANGLE] += D_LIKE(rot_by,params[SIZE]);
    params[YWANGLE] += D_LIKE(rot_by,params[SIZE]);

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
