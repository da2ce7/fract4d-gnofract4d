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

#include "colorFunc.h"
#include "iterFunc.h"

#include <cstddef>
#include <cmath>
#include <iostream>

// just returns the number of iterations, cast to a double
class flat_colorFunc : public colorFunc {
public:
    int buffer_size() const
	{ 
	    return 0;
	}
    void extract_state(const double *in_buf, void *out_buf) const
	{
	    // nop
	}
    double operator()(int iter, double eject, const void *p) const
        {
            return (double) iter;
        }

};

// return the iteration count plus a fractional part which ranges
// from 1 if the point "only just" escaped to 0 if it reached infinity
// this smooths the color bands which would otherwise appear
class cont_colorFunc : public colorFunc {
public:
    int buffer_size() const
	{ 
	    return sizeof(float);
	}
    void extract_state(const double *in_buf, void *out_buf) const
	{
	    *(float *) out_buf = (float) in_buf[EJECT_VAL];
	}
    double operator()(int iter, double eject, const void *p) const
        {
	    float eject_val = *(float *)p;
            return ((double) iter) + eject/eject_val;
        }
};

// just return zero, whatever - used by default for the inside of the Mset
class zero_colorFunc : public colorFunc {
public:
    int buffer_size() const
	{ 
	    return 0;
	}
    void extract_state(const double *in_buf, void *out_buf) const
	{
	    // nop
	}
    double operator()(int iter, double eject, const void *p) const
        {
            return (double) 0.0;
        }
};

// use just the ejection distance, without using the number of
// iterations.
class ejectDist_colorFunc : public colorFunc {
public:
    int buffer_size() const
	{ 
	    return sizeof(float);
	}
    void extract_state(const double *in_buf, void *out_buf) const
	{
	    *(float *) out_buf = (float) in_buf[EJECT_VAL];
	}
    double operator()(int iter, double eject, const void *in_buf) const
        {
	    float eject_val = *(float *)in_buf;
            return 256.0 * eject/eject_val;
        }
};

colorFunc *colorFunc_new(e_colorFunc e)
{
    colorFunc *pcf=NULL;
    switch(e){
    case COLORFUNC_FLAT:
        pcf = new flat_colorFunc;
        break;
    case COLORFUNC_CONT:
        pcf = new cont_colorFunc;
        break;
    case COLORFUNC_ZERO:
        pcf = new zero_colorFunc;
        break;
    case COLORFUNC_ED:
        pcf = new ejectDist_colorFunc;
        break;
    default:
        std::cerr << "Warning: unknown colorFunc value" << (int)e << "\n";
    }
     
    return pcf;
}

