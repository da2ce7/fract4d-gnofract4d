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

/* different iteration functions expressed as function objects */

#ifndef _ITERFUNC_H_
#define _ITERFUNC_H_

#include "fract_public.h"
#include "pointFunc_public.h"

#include <iosfwd>
#include <complex>

// offsets into parameter array
#define X 0
#define Y 1
#define CX 2
#define CY 3
#define X2 4
#define Y2 5
#define EJECT 6
#define EJECT_VAL 7
#define LASTX 8
#define LASTY 9
#define SCRATCH_SPACE LASTY+1

/* bailout flags */
#define HAS_X2 1
#define HAS_Y2 2

/* a function which performs a single fractal iteration 
   on the scratch space in p */

class iterFunc {
 public:
    virtual void operator()(double *p) const = 0;
    virtual void iter8(double *p) const = 0;
#ifdef HAVE_GMP
    virtual void operator()(gmp::f *p) const = 0;
#endif
    virtual int flags() const = 0;
    virtual const char *type() const = 0;

    // make a new one Just Like This
    virtual iterFunc *clone() const = 0;

    // boring things
    virtual std::ostream& put(std::ostream&) const = 0;
    virtual std::istream& get(std::istream&) = 0;
    virtual bool operator==(const iterFunc&) const = 0;

    // the number of options this fractal takes
    virtual int nOptions() const = 0;

    // FIXME: no gmp options
    virtual void setOption(int n, std::complex<double> val) = 0;
    virtual std::complex<double> getOption(int n) const = 0;
    virtual const char *optionName(int n) const = 0;

    // reset all options to standard values
    virtual void reset(double *fract_params) = 0;
    virtual e_bailFunc preferred_bailfunc(void) = 0;
};


typedef struct {
    const char *name;
    iterFunc *(*ctor)();
} ctorInfo;

const ctorInfo *iterFunc_names();

iterFunc *iterFunc_new(const char *name);
//iterFunc *iterFunc_mix(iterFunc *a, iterFunc *b);
iterFunc *iterFunc_read(std::istream& s);

std::ostream& operator<<(std::ostream& s, const iterFunc& iter);
std::istream& operator>>(std::istream& s, iterFunc& iter);

#endif /* _ITERFUNC_H_ */
