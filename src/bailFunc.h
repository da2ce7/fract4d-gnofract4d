/* function objects which determine whether to stop iterating */
#ifndef _BAILFUNC_H_
#define _BAILFUNC_H_

#include "pointFunc_public.h"

#include <iosfwd>

class bailFunc {
 public:
    /* sets the value of p[EJECT_VAL] */
    virtual void operator()(double *p, int flags)= 0;
};

// factory method to construct bailout function objects 
bailFunc *bailFunc_new(e_bailFunc);
bailFunc *bailFunc_read(std::istream& s);

#endif _BAILFUNC_H_
