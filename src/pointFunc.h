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

typedef double scratch_space[8];


/* interface for function object which computes a single point */
class pointFunc {
 public:
    virtual int operator()(const dvec4& params, double *scratch, int nIters) = 0;
};

/* factory method for making new fractFuncs */
pointFunc *pointFunc_new(
    e_iterFunc iterType, 
    e_bailFunc bailType,
    const d& eject);

#endif

