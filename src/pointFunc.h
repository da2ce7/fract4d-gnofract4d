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

#ifndef _POINTFUNC_H_
#define _POINTFUNC_H_

#include "pointFunc_public.h"
#include "colorizer_public.h"

#include <complex>
class iterFunc;

/* interface for function object which computes a single point */
class pointFunc {
 public:
    virtual void calc(
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        struct rgb *color, int *pnIters, void *out_buf
        ) = 0;
    virtual rgb_t recolor(int iter, double eject, const void *buf) const = 0;
    virtual int buffer_size() const = 0;
};
 
class inner_pointFunc {
 public:
    virtual void calc(
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        double *colorDist, int *pnIters, double **out_buf
        ) = 0;
};

struct s_pf_vtable {
    inner_pointFunc *(*create_pointFunc)(
        double bailout,
        double period_tolerance,
        std::complex<double> *params
	);
    void (*init)(
	struct s_pf_data *p,
        double bailout,
        double period_tolerance,
        std::complex<double> *params
	);
    void (*calc)(
	struct s_pf_data *p,
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        int *pnIters, double **out_buf
	);
    void (*kill)(
	struct s_pf_data *p
	);
} ;

struct s_pf_data {
    struct s_pf_vtable *vtbl;
} ;

typedef struct s_pf_vtable pf_vtable;
typedef struct s_pf_data pf_obj;

/* factory method for making new fractFuncs */
pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType,
    double eject,
    double periodicity_tolerance,
    colorizer *pcf,
    e_colorFunc outerCfType,    
    e_colorFunc innerCfType);

#endif

