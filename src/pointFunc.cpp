/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2000 Edwin Young
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
    colorizer *m_pcf;
    double p[PARAM_SIZE];
    bool m_potential;

public:
    /* ctor */
    pointCalc(iterFunc *iterType, 
              e_bailFunc bailType, 
              const d& eject,
              colorizer *pcf,
              bool potential) 
        : m_pIter(iterType), m_eject(eject), m_pcf(pcf), m_potential(potential)
        {
            m_pBail = bailFunc_new(bailType);
        }
    virtual ~pointCalc()
        {
            delete m_pBail;
        }

    virtual void operator()(
        const dvec4& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            int flags = HAS_X2 | HAS_Y2; // FIXME get from iterFunc

            scratch_space p;
            p[X] =  DOUBLE(params.n[VZ]); 
            p[Y] =  DOUBLE(params.n[VW]);
            p[CX] = DOUBLE(params.n[VX]);
            p[CY] = DOUBLE(params.n[VY]);
            p[EJECT] = DOUBLE(m_eject);

// I've found simple periodicity checking makes even 
// fairly complex fractals draw more slowly - YMMV.

#ifdef periodicity
            d Xold = p[X], Yold = p[Y];
            int k = 1, m = 1;
#endif

            int iter = 0;
            do
            {
                (*m_pIter)(p);                
                if(iter++ == nMaxIters) 
                {
                    // ran out of iterations
                    iter = -1; break; 
                }
#ifdef periodicity
                // periodicity check
                if(p[X] == Xold && p[Y] == Yold)
                {
                    iter = -1; break;
                }
                // periodicity housekeeping
                if(!--k)
                {
                    Xold = p[X] ; Yold = p[Y];
                    m *= 2; k = m;
                }
#endif
                (*m_pBail)(p,flags);            
            }while(p[EJECT_VAL] < m_eject);

            *pnIters = iter;
            if(color)
            {
                *color = (*m_pcf)(iter, p, m_potential);
            }
        }
};


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

pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailFunc, 
    const d& bailout,
    colorizer *pcf,
    bool potential)
{
    return new pointCalc(iterType, bailFunc, bailout, pcf, potential);
}
