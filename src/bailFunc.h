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

#ifndef _BAILFUNC_H_
#define _BAILFUNC_H_

#include "pointFunc_public.h"

#include <iosfwd>

/* a bailfunc is a function object which determines whether to stop
   iterating */

class bailFunc {
 public:
    /* sets the value of p[EJECT_VAL] */
    virtual void operator()(double *p, int flags)= 0;
#ifdef HAVE_GMP
    virtual void operator()(gmp::f *p, int flags)= 0;
#endif

    /* some functions (eg manhattan) can't cope with iter8 
       since it can bail out then back in again */
    virtual bool iter8_ok(void) = 0;
};

// factory method to construct bailout function objects 
bailFunc *bailFunc_new(e_bailFunc);
bailFunc *bailFunc_read(std::istream& s);

#endif /* _BAILFUNC_H_ */
