/* different iteration functions expressed as function objects */
#ifndef _ITERFUNC_H_
#define _ITERFUNC_H_

#include "pointFunc_public.h"

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
    virtual void operator()(double *p) = 0;
    virtual void iter8(double *p) = 0;
    virtual int flags() = 0;
};

iterFunc *iterFunc_new(e_iterFunc);

#endif _ITERFUNC_H_
