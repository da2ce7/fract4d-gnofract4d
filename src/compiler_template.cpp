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
#include <assert.h>

typedef double T;

// redeclare from vectors.h to avoid reading the whole file
enum {VX, VY, VZ, VW};		    // axes

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
// this is just to stop emacs from indenting everything
#if 0
}
#endif

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
	p->a[i] = params[i];
    }
#endif
#if TRACE
    p->out = NULL;
#endif
}

static void pf_calcWithPeriod(
    pf_real *pfo,
    int *pIter, int nMaxIters)
{
    T *p = pfo->p;
#if N_OPTIONS > 0
    std::complex<double> *a = pfo->a;
#endif
    int iter = *pIter;

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
	if(p[EJECT_VAL] >= pfo->m_eject)
	{
	    RET;
#if TRACE
	    (*out) << "pbail\n";
#endif
	    break;
	}
	if(iter++ >= nMaxIters) 
	{
	    // ran out of iterations
	    RET;
#if TRACE
	    (*out) << "pmax\n";
#endif
	    iter = -1; break;
	}
	if(fabs(XPOS - lastx) < pfo->m_period_tolerance &&
	   fabs(YPOS - lasty) < pfo->m_period_tolerance)
	{
	    // period detected!
	    RET;
#if TRACE
	    (*out) << "pp\n";
#endif
	    iter = -1;  break;
	}
	if(--k == 0)
	{
	    lastx = XPOS; lasty = YPOS;
	    m *= 2;
	    k = m;
	}
    }while(1);

    *pIter = iter;
}

static bool pf_calcNoPeriod(
    pf_real *pfo,
    int *pIter, int maxIter)
{
    T *p = pfo->p;
#if N_OPTIONS > 0
    std::complex<double> *a = pfo->a;
#endif

    int iter = *pIter;
    bool escaped = false;

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
	if(p[EJECT_VAL] >= pfo->m_eject)
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
	if(p[EJECT_VAL] >= pfo->m_eject)
	{
	    RET;
#if TRACE
	    (*out) << "bail\n";
#endif
	    escaped = true; 
	    break;
	}
	iter++;
    }            
    RET;
#if TRACE
    (*out) << "max\n";
#endif

    *pIter = iter;
    return escaped; 
}

static void pf_calc(
    // "object" pointer
    struct s_pf_data *p_stub,
    // in params
    const double *params, int nMaxIters, int nNoPeriodIters,
    // only used for debugging
    int x, int y, int aa,
    // out params
    int *pnIters, double **out_buf)
{
    pf_real *pfo = (pf_real *)p_stub;

    T *p = pfo->p;

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
    p[EJECT] = pfo->m_eject;
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
	done = pf_calcNoPeriod(pfo,&iter,nNoPeriodIters);
    }
    if(!done)
    {
	if(nMaxIters > nNoPeriodIters)
	{
	    pf_calcWithPeriod(pfo,&iter,nMaxIters);
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
}

static void pf_kill(
    struct s_pf_data *p_stub)
{
    free(p_stub);
}

static struct s_pf_vtable vtbl = 
{
    pf_init,
    pf_calc,
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
