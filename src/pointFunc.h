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

#ifndef _POINTFUNC_H_
#define _POINTFUNC_H_

#include "calc.h"
#include "pointFunc_public.h"
#include "colorizer.h"

class iterFunc;

/* interface for function object which computes a single point */
class pointFunc {
 public:
    virtual void operator()(
        // in params
        const dvec4& params, int nIters,
        // out params
        struct rgb *color, int *nIters
        ) = 0;
};

/* factory method for making new fractFuncs */
pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType,
    const d& eject,
    colorizer *pcf,
    bool potential);

#endif

