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

#include "bailFunc.h"
#include "iterFunc.h"

#include <cstddef>
#include <cmath>
#include <iostream>

inline double MIN(double x, double y) { return x < y ? x : y; }
inline double MAX(double x, double y) { return x > y ? x : y; }

class mag_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                pTemp[X2] = pIter[X] * pIter[X];
                pTemp[Y2] = pIter[Y] * pIter[Y];
            }            
            pTemp[EJECT_VAL] = pTemp[X2] + pTemp[Y2];
        };
    bool iter8_ok() { return true; };
    void init(void) {};
};
/*
class real_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            if(!(flags & (HAS_X2)))
            {
                p[X2] = p[X] * p[X];
            }            
            p[EJECT_VAL] = p[X2];
        };
    bool iter8_ok() { return true; };
};

class imag_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            if(!(flags & (HAS_Y2)))
            {
                p[Y2] = p[Y] * p[Y];
            }            
            p[EJECT_VAL] = p[Y2];
        };
    bool iter8_ok() { return true; };
};

class and_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                p[X2] = p[X] * p[X];
                p[Y2] = p[Y] * p[Y];
            }            
            p[EJECT_VAL] = MIN(p[X2],p[Y2]);
        };
    bool iter8_ok() { return true; };

};

class or_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                p[X2] = p[X] * p[X];
                p[Y2] = p[Y] * p[Y];
            }            
            p[EJECT_VAL] = MAX(p[X2],p[Y2]);
        }
    bool iter8_ok() { return true; }

};

class manhattan2_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                p[X2] = p[X] * p[X];
                p[Y2] = p[Y] * p[Y];
            }            
            double t = fabs(p[X2]) + fabs(p[Y2]);
            p[EJECT_VAL] = t*t;
        }
    bool iter8_ok() { return false; }
};

class manhattan_bailout : public bailFunc {
public:
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            p[EJECT_VAL] = p[X] + p[Y];
        }
    bool iter8_ok() { return false; }
};
*/

/* eject if difference between this point and last iteration is < epsilon */
class diff_bailout : public bailFunc {
public:
    static const double epsilon = 0.01;
    void operator()(double *pIter, double *pInput, double *pTemp, int flags)
        {
            double diffx = pIter[X] - pTemp[LASTX];
            double diffy = pIter[Y] - pTemp[LASTY];

            double diff = diffx * diffx + diffy * diffy;

            pTemp[LASTX] = pIter[X]; pTemp[LASTY] = pIter[Y];
            // FIXME: continuous potential doesn't work well with this
            pTemp[EJECT_VAL] = pInput[EJECT] + epsilon - diff;

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
/*
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
    case BAILOUT_REAL:
        pbf = new real_bailout;
        break;
    case BAILOUT_IMAG:
        pbf = new imag_bailout;
        break;
*/
    case BAILOUT_DIFF:
        pbf = new diff_bailout;
        break;
    default:
        std::cerr << "Warning: unknown bailFunc value" << (int)e << "\n";
    }
     
    return pbf;
}
