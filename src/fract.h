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
 
#ifndef _FRACT_H_
#define _FRACT_H_

#include "fract_public.h"
#include "pointFunc_public.h"
#include "colorizer_public.h"

#include "calc.h"

class fractFunc;
class iterFunc;

struct fractal
{
    // member vars
    private:

    // basic params
    d params[N_PARAMS];
    int maxiter;
    e_antialias antialias;
    int digits;
    bool potential;

    // color params
    colorizer *cizer;

    public:

    e_bailFunc bailout_type;    
    iterFunc *pIterFunc;

    private:
    // parameters which aren't saved

    // direction to move in for flip2julia
    double rot_by;

    // rotated params
    dmat4 rot;

    bool auto_deepen;

    public:
    
    // member funs
    fractal();
    fractal(const fractal& f); // copy ctor
    fractal& operator=(const fractal& f); // assignment op
    bool operator==(const fractal& f); // equality 
    ~fractal();

    // change the function type
    void set_fractal_type(const char *type);

    // make this fractal like f but weirder
    void set_inexact(const fractal& f, double weirdness); 
    void reset();
    void calc(Gf4dFractal *gf4d, image *im);
    void recolor(image *im);
    void relocate(double x, double y, double zoom);
    void flip2julia(double x, double y);
    void move(param_t i, double distance);
    bool write_params(const char *filename);
    bool load_params(const char *filename);
    char *get_param(param_t i);
    bool set_param(param_t i, const char *val);
    void set_max_iterations(int val);
    void set_aa(e_antialias val);
    void set_auto(bool val);
    int get_max_iterations();
    e_antialias get_aa();
    bool get_auto();
    bool get_potential() { return potential; };
    void set_potential(bool p) { potential = p; };
    bool check_precision();
    bool set_precision(int digits); 

    // color functions
    colorizer_t *get_colorizer();
    void set_colorizer(colorizer_t *cizer);

    void update_matrix();
    dvec4 get_center();
    friend class fractFunc;

    private:
    void recenter(const dvec4& delta);
    // used by copy ctor and op=
    void copy(const fractal& f);
};

void fract_delete(fractal_t **f);

#endif /* _FRACT_H_ */
