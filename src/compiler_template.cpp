#include "pointFunc.h"
//#include "iterFunc.h"
#include "bailFunc.h"

#include <math.h>
#include <iostream>
#include <complex>
#if TRACE
#include <fstream>
#include <sstream>
#include <iomanip>
#endif
#include <float.h>
#include <stdio.h>
#include <algorithm>

typedef double T;

// redeclare from vectors.h to avoid reading the whole file
enum {VX, VY, VZ, VW};		    // axes


class pointCalc : public pointFunc {
private:
    /* members */
    colorFunc *m_pOuterColor, *m_pInnerColor;
    double m_eject;
    T m_period_tolerance;
    colorizer *m_pcizer;
    void *m_handle; // handle of .so which keeps us in memory
    // enough space for one color data buffer, in case we aren't passed one
    void *one_space;

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
              colorizer *pcizer,
              e_colorFunc outerCfType,
              e_colorFunc innerCfType) 
        : m_eject(eject), m_period_tolerance(period_tolerance), m_pcizer(pcizer), m_handle(handle)
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

	    one_space = malloc(buffer_size());
        }
    virtual ~pointCalc()
        {
            delete m_pOuterColor;
            delete m_pInnerColor;
	    free(one_space);
#if TRACE
            delete out;
#endif
        }
    inline colorFunc *getColorFunc(int iter) const
	{
	    if(iter == -1)
	    {
		return m_pInnerColor;
	    }
	    else
	    {
		return m_pOuterColor;
	    }
	}
    inline rgb_t colorize(int iter, const T*p, void *out_buf)
        {
            double colorDist;
	    colorFunc *pcf = getColorFunc(iter);
	    pcf->extract_state(p,out_buf);
	    colorDist = (*pcf)(iter, p[EJECT],out_buf);

            return (*m_pcizer)(colorDist);
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
                if(p[EJECT_VAL] >= m_eject)
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
                if(p[EJECT_VAL] >= m_eject)
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
            T lastx = p[X], lasty=p[Y];
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
                if(p[EJECT_VAL] >= m_eject)
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

  T p[STATE_SPACE];
         
    void calc(
        const T *params, int nMaxIters, int nNoPeriodIters,
	int x, int y, int aa,
        struct rgb *color, int *pnIters, void *out_buf
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
	    if(out_buf == NULL) out_buf = one_space;

            p[X] =  params[VZ]; 
            p[Y] =  params[VW];
            p[CX] = params[VX];
            p[CY] = params[VY];
            p[EJECT] = m_eject;
            p[LASTX] = p[LASTY] = DBL_MAX/4.0;

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
                *color = colorize(iter,p,out_buf);
            }
        };
    
    virtual rgb_t recolor(int iter, double eject, const void *buf) const
        {
	    colorFunc *pcf = getColorFunc(iter);
	    double dist = (*pcf)(iter, eject, buf);
            return (*m_pcizer)(dist);
        }
    virtual void *handle()
        {
            return m_handle;
        }
    virtual int buffer_size() const
	{
	    return std:: max(m_pInnerColor->buffer_size(),
		       m_pOuterColor->buffer_size());
	}
};

extern "C" {
    void *create_pointfunc(
        void *handle,
        double bailout,
        double period_tolerance,
        std::complex<double> *params,
        colorizer *pcizer,        
        e_colorFunc outerCfType,
        e_colorFunc innerCfType)
    {
        return new pointCalc(
            handle, 
            bailout, 
            period_tolerance, 
            params, 
            pcizer, 
            outerCfType, 
            innerCfType);
    }
}
