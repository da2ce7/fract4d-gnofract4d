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

#include "pf.h"
#include "cmap.h"

class IFractalSite;

/* interface for function object which computes and/or colors a single point */
class pointFunc {
 public:
    /* factory method for making new pointFuncs */
    static pointFunc *create(
	pf_obj *pfo,
	cmap_t *cmap,
	IFractalSite *site);
	
    virtual ~pointFunc() {};
    virtual void calc(
        // in params. params points to [x,y,cx,cy]
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        rgba_t *color, int *pnIters
        ) const = 0;
    virtual rgba_t recolor(double dist) const = 0;
};

#endif
