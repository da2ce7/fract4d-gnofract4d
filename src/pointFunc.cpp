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
#include <stdio.h>

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

    inline rgb_t colorize(int iter, double *pIter, double *pInput, double *pTemp)
        {
            double colorDist;
            if(iter == -1)
            {
                colorDist = (*m_pInnerColor)(iter, pIter, pInput, pTemp);
            }
            else
            {
                colorDist = (*m_pOuterColor)(iter, pIter, pInput, pTemp);
            }
            return (*m_pcf)(colorDist);
        }

    template<class T>inline void calc(
        const vec4<T>& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            int flags = m_pIter->flags();

            T pIter[ITER_SPACE*(8+1)], pInput[INPUT_SPACE], pTemp[TEMP_SPACE];
            pIter[X] =  params.n[VZ]; 
            pIter[Y] =  params.n[VW];
            pInput[CX] = params.n[VX];
            pInput[CY] = params.n[VY];
            pInput[EJECT] = m_eject;
            pTemp[LASTX] = pTemp[LASTY] = DBL_MAX;

            int iter = 0;

            /* periodicity vars */
            const d PERIOD_TOLERANCE = 1.0E-10;
            d lastx = pIter[X], lasty=pIter[Y];
            int k =1, m = 1;

            /* to save on bailout tests and function call overhead, we
               try to calculate 8 iterations at a time. Some bailout
               functions don't allow this, however */
            if(m_pBail->iter8_ok())
            {
                int nMax8Iters = (nMaxIters/8) * 8;
                do
                {
                    m_pIter->iter8(pIter,pInput,pTemp);
                    if((iter+= 8) >= nMax8Iters)
                    {
                        goto finished8;
                    }                    
                    for(int i = 2; i < 18; ++i)
                    {
                        if(fabs(pIter[X+i] - lastx) < PERIOD_TOLERANCE &&
                           fabs(pIter[Y+i] - lasty) < PERIOD_TOLERANCE)
                        {
                            // period detected!
                            //printf(",");
                            iter = -1; goto finishedAll;
                        }
                    }
                    if(--k == 0)
                    {
                        lastx = pIter[X]; lasty = pIter[Y];
                        m *= 2;
                        k = m;
                    }                    
                    (*m_pBail)(pIter,pInput,pTemp,flags);  
                    if(pTemp[EJECT_VAL] >= m_eject)
                    {
                        break;
                    }
                    pIter[X] = pIter[X + (2*8)];
                    pIter[Y] = pIter[Y + (2*8)];                    
                }while(true);

                // we bailed out - need to look through the list to
                // see where (could do binary search, but can't be bothered)
                int i = 0;
                for(; i < 9; ++i)
                {
                    // 0 for flags because X2, Y2 data not up to date
                    (*m_pBail)(pIter + 2*i, pInput, pTemp, 0);
                    if(pTemp[EJECT_VAL] >= m_eject)
                    {
                        iter = iter - 8 + i;
                        goto finishedAll;
                    }
                }
                assert(false && "we must bailout before reaching this point");
            }

        finished8:
            // we finished the 8some iterations without bailing out
            do
            {
                (*m_pIter)(pIter,pInput,pTemp);
                if(iter++ >= nMaxIters) 
                {
                    // ran out of iterations
                    iter = -1; break; 
                }
                (*m_pBail)(pIter,pInput,pTemp,flags);            
                if(pTemp[EJECT_VAL] >= m_eject)
                {
                    break;
                }
                pIter[X] = pIter[X + (2*1)];
                pIter[Y] = pIter[Y + (2*1)];
                if(fabs(pIter[X] - lastx) < PERIOD_TOLERANCE &&
                   fabs(pIter[Y] - lasty) < PERIOD_TOLERANCE)
                {
                    // period detected!
                    //printf(".");
                    iter = -1; break;
                }
                if(--k == 0)
                {
                    lastx = pIter[X]; lasty = pIter[Y];
                    m *= 2;
                    k = m;
                }
            }while(1);

        finishedAll:
            *pnIters = iter;
            if(color)
            {
                *color = colorize(iter,pIter,pInput,pTemp);
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
            // fake the calculation state
            d inputSpace[INPUT_SPACE]= { 0.0 };
            d iterSpace[ITER_SPACE] = { 0.0 };
            // set ejectval = 1.0 , otherwise we have 0/0 = NaN for some colorFuncs
            d tempSpace[TEMP_SPACE] = { 0.0, 0.0, 1.0, 0.0, 0.0 };
            return colorize(iter, &inputSpace[0], &iterSpace[0], &tempSpace[0]);
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

