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

struct fractal
{
    private:

    // basic params
    d params[N_PARAMS];
    int maxiter;
    int fractal_type;
    bool antialias;
    bool auto_deepen;
    int digits;
    bool potential;

    // parameters which aren't saved

    // direction to move in for flip2julia
    double rot_by;

    // color params
    colorizer *cizer;

    // rotated params
    dmat4 rot;

    public:
    
    // member vars
    e_bailFunc bailout_type;

    // member funs
    fractal();
    fractal(const fractal& f); // copy ctor
    fractal& operator=(const fractal& f); // assignment op
    bool operator==(const fractal& f); // equality 
    ~fractal();

    // make this fractal like f but weirder
    void set_inexact(const fractal& f, double weirdness); 
    void reset();
    void calc(Gf4dFractal *gf4d, image *im);
    void relocate(double x, double y, double zoom);
    void flip2julia(double x, double y);
    void move(param_t i, int direction);
    bool write_params(const char *filename);
    bool load_params(const char *filename);
    char *get_param(param_t i);
    bool set_param(param_t i, const char *val);
    void set_max_iterations(int val);
    void set_aa(bool val);
    void set_auto(bool val);
    int get_max_iterations();
    bool get_aa();
    bool get_auto();
    bool get_potential() { return potential; };
    void set_potential(bool p) { potential = p; };
    bool check_precision();
    bool set_precision(int digits); 

    // color functions
    e_colorizer get_color_type();
    void set_color_type(e_colorizer);
    void set_color(double r, double g, double b);
    void set_cmap_file(const char *filename);
    char *get_cmap_file();
    double get_r();
    double get_g();
    double get_b();

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
