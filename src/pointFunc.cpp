/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
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

#include "pointFunc.h"
#include "iterFunc.h"
#include "bailFunc.h"

#include <math.h>
#include <iostream>

class pointCalc : public pointFunc {
private:
    /* members */
    iterFunc *m_pIter;
    bailFunc *m_pBail;
    const d& m_eject;
    double p[PARAM_SIZE];

public:
    /* ctor */
    pointCalc(e_iterFunc iterType, 
              e_bailFunc bailType, 
              const d& eject) : m_eject(eject)
        {
            m_pIter = iterFunc_new(iterType);
            m_pBail = bailFunc_new(bailType);
        }
    virtual int operator()(const dvec4& params, double *p, int nIters)
        {
            int flags = HAS_X2 | HAS_Y2; // FIXME get from iterFunc

            p[X] =  DOUBLE(params.n[VZ]); 
            p[Y] =  DOUBLE(params.n[VW]);
            p[CX] = DOUBLE(params.n[VX]);
            p[CY] = DOUBLE(params.n[VY]);
            p[EJECT] = DOUBLE(m_eject);

            int iter = 0;
            do
            {
                (*m_pIter)(p);                
                if(iter++ == nIters) return -1; // ran out of iterations
                (*m_pBail)(p,flags);            
            }while(p[EJECT_VAL] < m_eject);

            return iter;
        }
};


int test_cube(const dvec4& params, const d& eject, int nIters);


void
weird_iter(double *p)
{
    p[X2] = p[X] * p[X];
    p[Y2] = p[Y] * p[Y];
    double atmp = p[X2] - p[Y2] + p[X] + p[CX];
    p[Y] = 2.0 * p[X] * p[Y] + p[Y] + p[CY];
    p[X] = atmp;
}

int test_mandelbrot_cln(const dvec4& params, const d& eject, int nIters)
{
    d a = params.n[VZ], b = params.n[VW], 
        px = params.n[VX], py = params.n[VY], 
        atmp = D_LIKE(0.0,a), 
        a2 = a*a, b2=b*b;

    //debug_precision(a,"a");
    int n = 0;
    while ((a2 + b2) <= eject) {
        atmp = a2 - b2 + px;
        b = (a + a) * b + py;
        a = atmp;
        if(n++ == nIters) return -1; // ran out of iterations
        a2 = a*a; b2 = b*b;
    }
    return n;
}

// z = z^3 + c
int
test_cube(const dvec4& params, const d& eject, int nIters)
{
    d a = params.n[VZ], b = params.n[VW],
        px = params.n[VX], py = params.n[VY], atmp;

    int n = 0;

    while((a * a + b * b) <= eject) {
        atmp = a * a * a - 3 * a * b * b +px;
        b = 3 * a * a * b - b * b * b + py;
        a = atmp;
        if(n++ == nIters) return -1;
    }
    return n;
}

pointFunc *pointFunc_new(
    e_iterFunc iterFunc, 
    e_bailFunc bailFunc, 
    const d& bailout)
{
    return new pointCalc(iterFunc, bailFunc, bailout);
}
