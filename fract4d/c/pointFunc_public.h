#ifndef _POINTFUNC_PUBLIC_H_
#define _POINTFUNC_PUBLIC_H_

#include "pf.h"
#include "cmap.h"

class IFractalSite;

/* interface for function object which computes and/or colors a single point */
class pointFunc {
 public:
    /* factory method for making new pointFuncs */
    static pointFunc *create(
	pf_obj *pfo,
	cmap_t *cmap,
	IFractalSite *site);
	
    virtual ~pointFunc() {};
    virtual void calc(
        // in params. params points to [x,y,cx,cy]
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        rgba_t *color, int *pnIters
        ) const = 0;
    virtual rgba_t recolor(double dist) const = 0;
};

#endif
