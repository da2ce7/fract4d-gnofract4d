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
#define PARAM_SIZE 8

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
    virtual void setOption(int n, complex<double> val) = 0;
    virtual complex<double> getOption(int n) const = 0;
    virtual const char *optionName(int n) const = 0;
    // reset all options to standard values
    virtual void reset() = 0;
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

#endif _ITERFUNC_H_
