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
/*
    virtual void iter8(double *p)
        {
            for(int i = 8; i > 0; --i)
            {
                p[X2] = p[X] * p[X];
                p[Y2] = p[Y] * p[Y];
                double atmp = p[X2] - p[Y2] + p[CX];
                p[Y] = 2.0 * p[X] * p[Y] + p[CY];
                p[X] = atmp;
            }            
        }
*/
    virtual int flags()
        {
            return HAS_X2 | HAS_Y2;
        }
    virtual char *name()
        {
            return "Mandelbrot";
        }
};

class cubeFunc : public iterFunc 
{
public:
    virtual void operator()(double *p) 
        {
            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] * p[X] - 3.0 * p[X] * p[Y2] + p[CX];
            p[Y] = 3.0 * p[X2] * p[Y] - p[Y2] * p[Y] + p[CY];
            p[X] = atmp;
        }
    
    virtual int flags()
        {
            return 0;
        }
    virtual char *name()
        {
            return "Cubic Mandelbrot";
        }
};

class shipFunc: public iterFunc
{
public:
    virtual void operator()(double *p)
        {
            p[X] = fabs(p[X]);
            p[Y] = fabs(p[Y]);
            // same as mbrot from here
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
    virtual char *name()
        {
            return "Burning Ship";
        }
};

class buffaloFunc: public iterFunc
{
public:
    virtual void operator()(double *p)
        {
            p[X] = fabs(p[X]);
            p[Y] = fabs(p[Y]);

            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] - p[Y2] - p[X] + p[CX];
            p[Y] = 2.0 * p[X] * p[Y] - p[Y] + p[CY];
            p[X] = atmp;
        }
    virtual int flags()
        {
            return HAS_X2 | HAS_Y2;
        }
    virtual char *name()
        {
            return "Buffalo";
        }
};

// factory method to make new iterFuncs
iterFunc *iterFunc_new(int nFunc)
{
    switch(nFunc){
    case 0:
        return new mandFunc;
    case 1:
        return new shipFunc;
    case 2:
        return new buffaloFunc;
    case 3:
        return new cubeFunc;
    default:
        return NULL;
    }
}


