#include "pointFunc.h"

#include <math.h>
#include <complex>
#include <algorithm>
#if TRACE
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#endif
#include <float.h>
#include <stdlib.h>

typedef double T;

// redeclare from vectors.h to avoid reading the whole file
enum {VX, VY, VZ, VW};		    // axes

class pointCalc : public inner_pointFunc {
private:
    double m_eject;
    T m_period_tolerance;

#if N_OPTIONS > 0
    std::complex<double> a[N_OPTIONS];
#endif
#if TRACE
    std::ofstream *out;
#endif
public:
    /* ctor */
    pointCalc(double eject,
              double period_tolerance,
              std::complex<double> *options)
        : m_eject(eject), m_period_tolerance(period_tolerance)
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
        }
    virtual ~pointCalc()
        {
#if TRACE
            delete out;
#endif
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
        double *colorDist, int *pnIters, T **out_buf)
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
	    *out_buf = &p[0];
        };
    
};

typedef struct {
    pf_obj parent;
    T p[STATE_SPACE];
    double m_eject;
    T m_period_tolerance;

#if N_OPTIONS > 0
    std::complex<double> a[N_OPTIONS];
#endif
#if TRACE
    std::ofstream *out;
#endif
    
} pf_real ;

extern "C" {

static void pf_init(
    struct s_pf_data *p_stub,
    double bailout,
    double period_tolerance, 
    std::complex<double> *params)
{
    pf_real *p = (pf_real *)p_stub;

    p->m_eject = bailout;
    p->m_period_tolerance = period_tolerance;
#if N_OPTIONS > 0
    for(int i = 0; i < N_OPTIONS; ++i)
    {
	p->a[i] = options[i];
    }
#endif
#if TRACE
    p->out = NULL;
#endif
}

    static void pf_kill(
	struct s_pf_data *p_stub)
    {
	free(p_stub);
    }

    static inner_pointFunc *create_pointfunc(
        double bailout,
        double period_tolerance,
        std::complex<double> *params)
    {
        return new pointCalc(
            bailout, 
            period_tolerance, 
            params);
    }


static struct s_pf_vtable vtbl = 
{
    create_pointfunc,
    pf_init,
    NULL,
    pf_kill
};

    pf_obj *pf_new()
    {
	pf_obj *p = (pf_obj *)malloc(sizeof(pf_real));
	if(!p) return NULL;
	p->vtbl = &vtbl;
	return p;
    }


}
