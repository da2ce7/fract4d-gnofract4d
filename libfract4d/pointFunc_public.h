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


#ifndef _POINTFUNC_PUBLIC_H_
#define _POINTFUNC_PUBLIC_H_

#include "colorizer_public.h"
#include "state.h"

#include <complex>

/* an enumeration of the available bailout functions */
// update table in properties.cpp:create_bailout_menu if this changes
typedef enum 
{
    BAILOUT_MAG = 0,
    BAILOUT_MANH,
    BAILOUT_MANH2,
    BAILOUT_OR,
    BAILOUT_AND,
    BAILOUT_REAL,
    BAILOUT_IMAG,
    BAILOUT_DIFF
} e_bailFunc;


/* an enumeration of the available color functions */
typedef enum
{
    COLORFUNC_FLAT,
    COLORFUNC_CONT,
    COLORFUNC_ZERO,
    COLORFUNC_ED,
    COLORFUNC_DECOMP,
    COLORFUNC_ANGLE
} e_colorFunc;

class iterFunc;
class bailFunc;

/* interface for function object which computes and/or colors a single point */
class pointFunc {
 public:
    /* factory method for making new pointFuncs */
    static pointFunc *create(
	void *dlHandle, // library containing compiled code
	std::complex<double> *opts,
	double eject,
	double periodicity_tolerance,
	colorizer **ppcf,
	e_colorFunc outerCfType,    
	e_colorFunc innerCfType,
	const char *outerCtfType,
	const char *innerCtfType);
	
    virtual ~pointFunc() {};
    //virtual pointFunc *clone() const = 0;
    virtual void calc(
        // in params. params points to [x,y,cx,cy]
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        struct rgb *color, int *pnIters, void *out_buf
        ) const = 0;
    virtual rgb_t recolor(int iter, double eject, const void *buf) const = 0;
    virtual int buffer_size() const = 0;
};

#endif
