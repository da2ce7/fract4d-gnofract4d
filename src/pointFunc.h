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
        double *colorDist, int *pnIters, void *out_buf
        ) = 0;
    virtual double recolor(int iter, double eject, const void *buf) const = 0;
};


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

