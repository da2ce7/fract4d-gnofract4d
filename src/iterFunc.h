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

/* different iteration functions expressed as function objects */

#ifndef _ITERFUNC_H_
#define _ITERFUNC_H_

#include "fract_public.h"
#include "pointFunc_public.h"

#include <iosfwd>
#include <complex>
#include <string>
#include <map>

// iter state
#define X 0
#define Y 1
#define ITER_SPACE (Y+1)

// input state
#define CX 0
#define CY 1
#define EJECT 2
#define INPUT_SPACE (EJECT+1)

// temp state
#define X2 0
#define Y2 1
#define EJECT_VAL 2
#define LASTX 3
#define LASTY 4
#define TEMP_SPACE (LASTY+1)

/* bailout flags */
#define HAS_X2 1
#define HAS_Y2 2
#define USE_COMPLEX 4

/* a function which performs a single fractal iteration */

class iterFunc {
 public:
    // return the fragments of C++ code which we'll interpolate
    // into the template. They're added into the map 
    // map contains DEFINE-NAME -> CODE
    virtual void get_code(std::map<std::string,std::string>& ) const = 0;

    virtual int flags() const = 0;
    virtual const char *type() const = 0;

    // make a new one Just Like This
    virtual iterFunc *clone() const = 0;

    // boring things like I/O and equality
    virtual std::ostream& put(std::ostream&) const = 0;
    virtual std::istream& get(std::istream&) = 0;
    virtual bool operator==(const iterFunc&) const = 0;

    // the number of options this fractal takes
    virtual int nOptions() const = 0;

    // FIXME: no gmp options
    virtual void setOption(int n, std::complex<double> val) = 0;
    virtual std::complex<double> getOption(int n) const = 0;
    virtual std::complex<double> *opts() = 0;
    virtual const char *optionName(int n) const = 0;

    // reset all options to standard values
    virtual void reset(double *fract_params) = 0;
    virtual e_bailFunc preferred_bailfunc(void) = 0;

 protected:
    virtual std::string decl_code() const = 0;
    virtual std::string iter_code() const = 0;
    virtual std::string ret_code() const = 0;
    virtual std::string save_iter_code() const = 0;
    virtual std::string restore_iter_code() const = 0;
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
