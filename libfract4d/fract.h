/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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
 
#ifndef _FRACT_H_
#define _FRACT_H_

#include "fract_public.h"
#include "pointFunc_public.h"
#include "colorizer_public.h"

#include "calc.h"
#include "compiler.h"

class fractFunc;
class iterFunc;


struct fractal : public IFractal
{
    // member vars
private:

    // basic params
    d params[N_PARAMS];
    int maxiter;
    e_antialias antialias;
    int digits;

    // color params
    colorizer **cizers;

    e_colorFunc colorFuncs[N_COLORFUNCS];
    const char *colorTransferFuncs[N_COLORFUNCS];

    iterFunc *pIterFunc;

    // parameters beyond this point aren't saved
    int nThreads;
    e_antialias eaa;
    bailFunc *bailout_type;    

private:

    // direction to move in for flip2julia
    double rot_by;

    // rotated params
    dmat4 rot;

    bool auto_deepen;

public:
    
    // member funs
    fractal();
    fractal(const fractal& f); // copy ctor
    IFractal *clone();

    fractal& operator=(const fractal& f); // assignment op
    IFractal& operator=(const IFractal& f);
    bool operator==(const fractal& f) const; // equality 
    bool operator==(const IFractal& f) const; 
    ~fractal();

    // change the function type
    void set_fractal_type(const char *type);
    iterFunc *get_iterFunc() const;
    void set_iterFunc(const iterFunc *);

    // make this fractal like f but weirder
    void set_inexact(const IFractal& f, double weirdness); 
    // make this fractal into a mixture of f1 and f2, 
    // in the proportion lambda of f1 : 1-lambda of f2
    void set_mixed(const IFractal& f1, const IFractal& f2, double lambda);

    void reset();
    void calc(IFractalSite *site, IImage *im);

    void recolor(IImage *im);
    void relocate(double x, double y, double zoom);
    void flip2julia(double x, double y);
    void move(param_t i, double distance);
    bool write_params(const char *filename) const;
    bool load_params(const char *filename);
    char *get_param(param_t i) const;
    bool set_param(param_t i, const char *val);
    void set_max_iterations(int val);
    void set_aa(e_antialias val);
    e_antialias get_aa() const;
    void set_effective_aa(e_antialias val);
    e_antialias get_effective_aa() const ;

    void set_threads(int n);
    int get_threads() const;

    void set_auto(bool val);
    int get_max_iterations() const;

    bool get_auto() const;
    bool check_precision();
    bool set_precision(int digits); 

    // color functions
    int get_active_colorizers() const;
    colorizer_t *get_colorizer(int which_cizer) const ;
    void set_colorizer(colorizer_t *cizer, int which_cizer);

    e_bailFunc get_bailFunc() const;
    void set_bailFunc(e_bailFunc bf);

    void set_colorFunc(e_colorFunc cf, int which_cf);
    e_colorFunc get_colorFunc(int which_cf) const;

    void set_colorTransferFunc(const char *name, int which_cf);
    const char *get_colorTransferFunc(int which_cf) const;

    void update_matrix();
    dvec4 get_center();
    friend class fractFunc;
    friend class fractThreadFunc;

    // calculate the periodicity error tolerance
    d tolerance(IImage *im); 

private:
    void recenter(const dvec4& delta);
    // used by copy ctor and op=
    void copy(const fractal& f);
};

#endif /* _FRACT_H_ */
