/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
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
#include <float.h>

class pointCalc : public pointFunc {
private:
    /* members */
    iterFunc *m_pIter;
    bailFunc *m_pBail;
    colorFunc *m_pOuterColor, *m_pInnerColor;
    double m_eject;
    colorizer *m_pcf;

public:
    /* ctor */
    pointCalc(iterFunc *iterType, 
              e_bailFunc bailType, 
              double eject,
              colorizer *pcf,
              e_colorFunc outerCfType,
              e_colorFunc innerCfType) 
        : m_pIter(iterType), m_eject(eject), m_pcf(pcf)
        {
            m_pBail = bailFunc_new(bailType);
            m_pOuterColor = colorFunc_new(outerCfType);
            m_pInnerColor = colorFunc_new(innerCfType);
        }
    virtual ~pointCalc()
        {
            delete m_pBail;
            delete m_pOuterColor;
            delete m_pInnerColor;
        }

    inline rgb_t colorize(int iter, double *p)
        {
            double colorDist;
            if(iter == -1)
            {
                colorDist = (*m_pInnerColor)(iter, p);
            }
            else
            {
                colorDist = (*m_pOuterColor)(iter, p);
            }
            return (*m_pcf)(colorDist);
        }

    template<class T>inline void calc(
        const vec4<T>& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            int flags = m_pIter->flags();

            T p[SCRATCH_SPACE];
            T save[SCRATCH_SPACE];
            p[X] =  params.n[VZ]; 
            p[Y] =  params.n[VW];
            p[CX] = params.n[VX];
            p[CY] = params.n[VY];
            p[EJECT] = m_eject;
            p[LASTX] = p[LASTY] = DBL_MAX;

            int iter = 0;

            /* to save on bailout tests and function call overhead, we
               try to calculate 8 iterations at a time. Some bailout
               functions don't allow this, however */
            if(m_pBail->iter8_ok())
            {
                int nMax8Iters = (nMaxIters/8) * 8;
                do
                {
                    save[X] = p[X];
                    save[Y] = p[Y];
                    m_pIter->iter8(p);
                    if((iter+= 8) >= nMax8Iters)
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
                *color = colorize(iter,p);
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
    virtual rgb_t recolor(int iter)
        {
            // fake scratch space
            d s[SCRATCH_SPACE]= { 0.0 };
            s[EJECT_VAL] = 1.0; // otherwise we have 0/0 = NaN for some colorFuncs
            return colorize(iter, s);
        }

};


pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType, 
    double bailout,
    colorizer *pcf,
    e_colorFunc outerCfType,
    e_colorFunc innerCfType)
{
    return new pointCalc(iterType, bailType, bailout, pcf, outerCfType, innerCfType);
}

