/* function objects which determine whether to stop iterating */
#ifndef _BAILFUNC_H_
#define _BAILFUNC_H_

#include "test-fonction.h"

class bailFunc {
 public:
    /* sets the value of p[EJECT_VAL] */
    virtual void operator()(double *p, int flags)= 0;
};

bailFunc *bailFunc_new(e_bailFunc);

#endif _BAILFUNC_H_
