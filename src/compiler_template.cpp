#include "pointFunc.h"
#include "iterFunc.h"
#include "bailFunc.h"
#include "compiler.h"

#include <math.h>
#include <iostream>
#include <float.h>
#include <stdio.h>
#include <algorithm>

const d PERIOD_TOLERANCE = 1.0E-10;

class pointCalc : public pointFunc {
private:
    /* members */
    colorFunc *m_pOuterColor, *m_pInnerColor;
    double m_eject;
    colorizer *m_pcf;

public:
    /* ctor */
    pointCalc(double eject,
              colorizer *pcf,
              e_colorFunc outerCfType,
              e_colorFunc innerCfType) 
        : m_eject(eject), m_pcf(pcf)
        {
            m_pOuterColor = colorFunc_new(outerCfType);
            m_pInnerColor = colorFunc_new(innerCfType);
        }
    virtual ~pointCalc()
        {
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

    /* do some iterations without periodicity */
    template<class T>
    bool calcNoPeriod(int& iter, int maxIter, T *pIter, T *pInput, T *pTemp)
        {
            do
            {
                iter1(pIter,pInput,pTemp);
                if((iter++) >= maxIter)
                {   
                    return false;
                }                    
                bail(pIter,pInput,pTemp);  
                if(pTemp[EJECT_VAL] >= m_eject)
                {
                    return true;
                }
            }while(true);
        }

    template<class T>
    bool calcWithPeriod(
        int &iter, int nMaxIters, 
        T *pIter, T *pInput, T *pTemp)
        {
            /* periodicity vars */
            d lastx = pIter[X], lasty=pIter[Y];
            int k =1, m = 1;

            do
            {
                iter1(pIter,pInput,pTemp);
                if(iter++ >= nMaxIters) 
                {
                    // ran out of iterations
                    iter = -1; return false;
                }
                bail(pIter,pInput,pTemp);            
                if(pTemp[EJECT_VAL] >= m_eject)
                {
                    return true;
                }
                if(fabs(pIter[X] - lastx) < PERIOD_TOLERANCE &&
                   fabs(pIter[Y] - lasty) < PERIOD_TOLERANCE)
                {
                    // period detected!
                    iter = -1; return false;
                }
                if(--k == 0)
                {
                    lastx = pIter[X]; lasty = pIter[Y];
                    m *= 2;
                    k = m;
                }
            }while(1);
        }

    template<class T>
    inline void calc(
        const vec4<T>& params, int nMaxIters, int nNoPeriodIters,
        struct rgb *color, int *pnIters
        )
        {
            T pIter[ITER_SPACE], pInput[INPUT_SPACE], pTemp[TEMP_SPACE];
            pIter[X] =  params.n[VZ]; 
            pIter[Y] =  params.n[VW];
            pInput[CX] = params.n[VX];
            pInput[CY] = params.n[VY];
            pInput[EJECT] = m_eject;
            pTemp[LASTX] = pTemp[LASTY] = DBL_MAX;

            int iter = 0;
            bool done = false;

            assert(nNoPeriodIters <= nMaxIters);

            if(nNoPeriodIters > 0)
            {
                done = calcNoPeriod(iter,nNoPeriodIters,pIter,pInput, pTemp);
            }
            if(!done)
            {
                done = calcWithPeriod(iter,nMaxIters,pIter,pInput,pTemp);
            }

            *pnIters = iter;
            if(color)
            {
                *color = colorize(iter,pIter,pInput,pTemp);
            }
        };

    virtual void operator()(
        const vec4<double>& params, int nMaxIters, int nNoPeriodIters,
        struct rgb *color, int *pnIters
        )
        {
            calc<double>(params, nMaxIters, nNoPeriodIters, color, pnIters);
        }
#ifdef HAVE_GMP
    virtual void operator()(
        const vec4<gmp::f>& params, int nMaxIters,
        struct rgb *color, int *pnIters
        )
        {
            calc<gmp::f>(params, nMaxIters, nNoPeriodIters, color, pnIters);
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

    //template<class T>
    inline void iter1(
        double *pIter, 
        double *pInput, 
        double *pTemp) const 
        {
            DECL;
            ITER;
            RET;
        }
    inline void bail(
        double *pIter, double *pInput, double *pTemp)
        {
            BAIL;
        }
};

extern "C" {
    void *create_pointfunc(
            double bailout,
            colorizer *pcf,
            e_colorFunc outerCfType,
            e_colorFunc innerCfType)
    {
        return new pointCalc(bailout, pcf, outerCfType, innerCfType);
    }
}
