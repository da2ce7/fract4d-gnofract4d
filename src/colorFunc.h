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

/* A colorFunc defines a mapping from the state of the computation
once the iterations have been completed, to a floating-point number
which is used to determine the distance into the colormap to use for
drawing */

#ifndef _COLORFUNC_H_
#define _COLORFUNC_H_

#include "colorizer_public.h"
#include "calc.h"
#include "pointFunc_public.h"

#include <iosfwd>
#include <string>

// abstract base class
class colorFunc {
 public:
    virtual double operator()(int iter, const double *pIter, const double *pInput, const double *pTemp) const = 0;
#ifdef HAVE_GMP
    virtual double operator()(int iter, gmp::f *scratch) const = 0;
#endif
};

// factory method to construct color function objects 
colorFunc *colorFunc_new(e_colorFunc);
colorFunc *colorFunc_read(std::istream& s);


#endif /*_COLORFUNC_H_*/
