/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

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
    double m_eject;
    colorizer *m_pcf;
    bool m_potential;

public:
    /* ctor */
    pointCalc(iterFunc *iterType, 
              e_bailFunc bailType, 
              double eject,
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

    template<class T>inline void calc(
        const vec4<T>& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            int flags = m_pIter->flags();

            T p[SCRATCH_SPACE], save[SCRATCH_SPACE];
            p[X] =  params.n[VZ]; 
            p[Y] =  params.n[VW];
            p[CX] = params.n[VX];
            p[CY] = params.n[VY];
            p[EJECT] = m_eject;

            int iter = 0;

            if(m_pBail->iter8_ok())
            {
                int nMax8Iters = (nMaxIters/8) * 8;
                do
                {
                    save[X] = p[X];
                    save[Y] = p[Y];
                    m_pIter->iter8(p);
                    if((iter+= 8) > nMax8Iters)
                    {
                        goto finished8;
                    }
                    (*m_pBail)(p,flags);            
                }while(p[EJECT_VAL] < m_eject);

                // we bailed out - need to go back to saved position & 
                // recalculate
                p[X] = save[X]; p[Y] = save[Y];
                iter -= 8;
            }

        finished8:
            // we finished the 8some iterations without bailing out
            do
            {
                (*m_pIter)(p);                
                if(iter++ >= nMaxIters) 
                {
                    // ran out of iterations
                    iter = -1; break; 
                }
                (*m_pBail)(p,flags);            
            }while(p[EJECT_VAL] < m_eject);

            *pnIters = iter;
            if(color)
            {
                *color = (*m_pcf)(iter, p, m_potential);
            }
        };

    virtual void operator()(
        const vec4<double>& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            calc<double>(params, nMaxIters, color, pnIters);
        }
#ifdef HAVE_GMP
    virtual void operator()(
        const vec4<gmp::f>& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            calc<gmp::f>(params, nMaxIters, color, pnIters);
        }
#endif
};


pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailFunc, 
    double bailout,
    colorizer *pcf,
    bool potential)
{
    return new pointCalc(iterType, bailFunc, bailout, pcf, potential);
}
