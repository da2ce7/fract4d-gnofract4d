/* functions which perform individual iterations of a fractal function */

#include "iterFunc.h"

#include <cstddef>

class mandFunc : public iterFunc 
{
public:
    virtual void operator()(double *p) 
        {
            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] - p[Y2] + p[CX];
            p[Y] = 2.0 * p[X] * p[Y] + p[CY];
            p[X] = atmp;
        }
    virtual int flags()
        {
            return HAS_X2 | HAS_Y2;
        }
};

// factory method to make new iterFuncs
iterFunc *iterFunc_new(e_iterFunc e)
{
    switch(e){
    case ITERFUNC_MAND:
        return new mandFunc;
    default:
        return NULL;
    }
}
