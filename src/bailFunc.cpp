#include "bailFunc.h"
#include "iterFunc.h"

#include <cstddef>
#include <cmath>

inline double MIN(double x, double y) { return x < y ? x : y; }
inline double MAX(double x, double y) { return x > y ? x : y; }

class mag_bailout : public bailFunc {
public:
    void operator()(double *p, int flags)
        {
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                p[X2] = p[X] * p[X];
                p[Y2] = p[Y] * p[Y];
            }            
            p[EJECT_VAL] = p[X2] + p[Y2];
        };
    bool iter8_ok() { return true; };
};

class and_bailout : public bailFunc {
public:
    void operator()(double *p, int flags)
        {
            p[EJECT_VAL] = MIN(p[X2],p[Y2]);
        };
    bool iter8_ok() { return true; };

};

class or_bailout : public bailFunc {
public:
    void operator()(double *p, int flags)
        {
            p[EJECT_VAL] = MAX(p[X2],p[Y2]);
        }
    bool iter8_ok() { return true; }

};

class manhattan2_bailout : public bailFunc {
public:
    void operator()(double *p, int flags)
        {
            double t = fabs(p[X2]) + fabs(p[Y]);
            p[EJECT_VAL] = t*t;
        }
    bool iter8_ok() { return false; }
};

class manhattan_bailout : public bailFunc {
public:
    void operator()(double *p, int flags)
        {
            p[EJECT_VAL] = p[X] + p[Y];
        }
    bool iter8_ok() { return false; }

};

bailFunc *bailFunc_new(e_bailFunc e)
{
    bailFunc *pbf=NULL;
    switch(e){
    case BAILOUT_MAG:
        pbf = new mag_bailout;
        break;
    case BAILOUT_MANH:
        pbf = new manhattan_bailout;
        break;
    case BAILOUT_MANH2:
        pbf = new manhattan2_bailout;
        break;
    case BAILOUT_OR:
        pbf = new or_bailout;
        break;
    case BAILOUT_AND:
        pbf = new and_bailout;
        break;
    }
    return pbf;
}
