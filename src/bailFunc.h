/* function objects which determine whether to stop iterating */
#ifndef _BAILFUNC_H_
#define _BAILFUNC_H_

#include "pointFunc_public.h"

#include <iosfwd>

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

#endif _BAILFUNC_H_
