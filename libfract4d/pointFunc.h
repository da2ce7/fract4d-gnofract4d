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


/* This is the interface that compiled code that implements a fractal function
   needs to implement. Typically such code is generated at runtime by the 
   compiler 
*/

#include <complex>
 
struct s_pf_vtable {
    /* fill in fields in pf_data with appropriate stuff */
    void (*init)(
	struct s_pf_data *p,
        double bailout,
        double period_tolerance,
        std::complex<double> *params
	);
    /* calculate one point.
       perform up to nIters iterations,
       using periodicity (if supported) after the 1st nNoPeriodIters
       return:
       number of iters performed in pnIters
       out_buf: points to an array of doubles containing info on the calculation,
       see state.h for offsets
    */
    void (*calc)(
	struct s_pf_data *p,
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        int *pnIters, double **out_buf
	);
    /* deallocate data in p */
    void (*kill)(
	struct s_pf_data *p
	);
} ;

struct s_pf_data {
    struct s_pf_vtable *vtbl;
} ;

typedef struct s_pf_vtable pf_vtable;
typedef struct s_pf_data pf_obj;


/* compiled code also needs to define a function pf_new which returns
 * a newly-allocated pf_obj
 */

extern "C" pf_obj *pf_new();

#endif

