#include "pointFunc.h"
#include "iterFunc.h"
#include "bailFunc.h"

#include <math.h>
#include <iostream>
#if TRACE
#include <fstream>
#include <sstream>
#include <iomanip>
#endif
#include <float.h>
#include <stdio.h>
#include <algorithm>

typedef double T;

class pointCalc : public pointFunc {
private:
    /* members */
    colorFunc *m_pOuterColor, *m_pInnerColor;
    double m_eject;
    T m_period_tolerance;
    colorizer *m_pcf;
    void *m_handle; // handle of .so which keeps us in memory

#if N_OPTIONS > 0
    std::complex<double> a[N_OPTIONS];
#endif
#if TRACE
    std::ofstream *out;
#endif
public:
    /* ctor */
    pointCalc(void *handle,
              double eject,
              double period_tolerance,
              std::complex<double> *options,
              colorizer *pcf,
              e_colorFunc outerCfType,
              e_colorFunc innerCfType) 
        : m_eject(eject), m_period_tolerance(period_tolerance), m_pcf(pcf), m_handle(handle)
        {
#if N_OPTIONS > 0
            for(int i = 0; i < N_OPTIONS; ++i)
            {
                a[i] = options[i];
            }
#endif
#if TRACE
            out = NULL;
#endif
            m_pOuterColor = colorFunc_new(outerCfType);
            m_pInnerColor = colorFunc_new(innerCfType);
        }
    virtual ~pointCalc()
        {
            delete m_pOuterColor;
            delete m_pInnerColor;
#if TRACE
            delete out;
#endif
        }
    inline rgb_t colorize(int iter, const T*pIter, const T*pInput, const T*pTemp)
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
    //template<class T>
    bool calcNoPeriod(int& iter, int maxIter)
        {
            DECL;
#if TRACE
            (*out) << "in:" << XPOS << "," << YPOS << "\n";
#endif 

#if UNROLL
            while(iter + 8 < maxIter)
            {
                SAVE_ITER;
                ITER; 
                ITER; 
                ITER; 
                ITER; 
                ITER; 
                ITER; 
                ITER; 
                ITER; 
#if TRACE
                (*out) << "8:" << XPOS << "," << YPOS << "\n";
#endif 

                BAIL;
                if(pTemp[EJECT_VAL] >= m_eject)
                {
                    // we bailed out somewhere in the last 8iters -
                    // go back to beginning and look one-by-one
                    RESTORE_ITER;
                    break;
                }
                iter += 8;
            }
#endif      
            while(iter + 1 < maxIter)
            {
                ITER;
#if TRACE
                (*out) << "1:" << XPOS << "," << YPOS << "\n";
#endif 
                BAIL;
                if(pTemp[EJECT_VAL] >= m_eject)
                {
                    RET;
#if TRACE
		    (*out) << "bail\n";
#endif
                    return true; // escaped
                }
                iter++;
            }            
            RET;
#if TRACE
	    (*out) << "max\n";
#endif
            return false; // finished iterations without escaping
        }

    //template<class T>
    void calcWithPeriod(
        int &iter, int nMaxIters)
        {
            /* periodicity vars */
            d lastx = pIter[X], lasty=pIter[Y];
            int k =1, m = 1;
            
            // single iterations
            DECL; 
#if TRACE
            (*out) << "pin:" << XPOS << "," << YPOS << "\n";
#endif 
            do
            {
                ITER; 
#if TRACE
                (*out) << "p:" << XPOS << "," << YPOS << "\n";
#endif 
                BAIL;
                if(pTemp[EJECT_VAL] >= m_eject)
                {
                    RET;
#if TRACE
		    (*out) << "pbail\n";
#endif
                    return;
                }
                if(iter++ >= nMaxIters) 
                {
                    // ran out of iterations
                    RET;
#if TRACE
		    (*out) << "pmax\n";
#endif
                    iter = -1; return;
                }
                if(fabs(XPOS - lastx) < m_period_tolerance &&
                   fabs(YPOS - lasty) < m_period_tolerance)
                {
                    // period detected!
                    RET;
#if TRACE
		    (*out) << "pp\n";
#endif
                    iter = -1;  return;
                }
                if(--k == 0)
                {
                    lastx = XPOS; lasty = YPOS;
                    m *= 2;
                    k = m;
                }
            }while(1);
        }

    T pIter[ITER_SPACE], pInput[INPUT_SPACE], pTemp[TEMP_SPACE];
         
    //template<class T>
    inline void calc(
        const vec4<T>& params, int nMaxIters, int nNoPeriodIters,
	int x, int y, int aa,
        struct rgb *color, int *pnIters
        )
        {
#if TRACE
            if(out == NULL)
            {
                std::ostringstream ofname;
                ofname << "out-" << pthread_self() << ".txt";
                std::string outname = ofname.str();
                std::cout << outname << "\n";
                out = new std::ofstream(outname.c_str());
                (*out) << std::setprecision(17);
            }
#endif
            pIter[X] =  params.n[VZ]; 
            pIter[Y] =  params.n[VW];
            pInput[CX] = params.n[VX];
            pInput[CY] = params.n[VY];
            pInput[EJECT] = m_eject;
            pTemp[LASTX] = pTemp[LASTY] = DBL_MAX/4.0;

            int iter = 0;
            bool done = false;

            assert(nNoPeriodIters >= 0 && nNoPeriodIters <= nMaxIters);

#if NOPERIOD
            nNoPeriodIters = nMaxIters;
#else 
#if ALLPERIOD
            nNoPeriodIters = 0;
#endif
#endif

#if TRACE
	    (*out)  << "calc: " << nNoPeriodIters << " " << nMaxIters 
		    << " " << x << " " << y << " " << aa << "\n";
#endif
            if(nNoPeriodIters > 0)
            {
                done = calcNoPeriod(iter,nNoPeriodIters);
            }
            if(!done)
            {
		if(nMaxIters > nNoPeriodIters)
		{
		    calcWithPeriod(iter,nMaxIters);
		}
		else
		{
		    iter = -1;
		}
            }

            *pnIters = iter;
#if TRACE
            (*out) << iter << "\n";
#endif
            if(color)
            {
                *color = colorize(iter,pIter,pInput,pTemp);
            }
        };

    virtual void operator()(
        const vec4<double>& params, int nMaxIters, int nNoPeriodIters,
	int x, int y, int aa,
        struct rgb *color, int *pnIters
        )
        {
            calc(params, nMaxIters, nNoPeriodIters, x, y, aa,color, pnIters);
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
            // fake the calculation state for recoloration
            const T inputSpace[INPUT_SPACE]= { 0.0 };
            const T iterSpace[ITER_SPACE] = { 0.0 };
            // set ejectval = 1.0 , otherwise we have 0/0 = NaN for some colorFuncs
            const T tempSpace[TEMP_SPACE] = { 0.0, 0.0, 1.0, 0.0, 0.0 };

            return colorize(iter, &inputSpace[0], &iterSpace[0], &tempSpace[0]);
        }
    virtual void *handle()
        {
            return m_handle;
        }
};

extern "C" {
    void *create_pointfunc(
        void *handle,
        double bailout,
        double period_tolerance,
        std::complex<double> *params,
        colorizer *pcf,        
        e_colorFunc outerCfType,
        e_colorFunc innerCfType)
    {
        return new pointCalc(
            handle, 
            bailout, 
            period_tolerance, 
            params, 
            pcf, 
            outerCfType, 
            innerCfType);
    }
}
