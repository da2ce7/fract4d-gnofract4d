#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif


#include "pf.h"
#include "cmap.h"
#include "pointFunc_public.h"
#include "fract_public.h"

#include <unistd.h>
#include <dlfcn.h>
#include <stdio.h>


class pf_wrapper : public pointFunc
{
private:
    pf_obj *m_pfo;
    cmap_t *m_cmap;
    IFractalSite *m_site;
public:
    pf_wrapper(
	pf_obj *pfo,
	cmap_t *cmap,
	IFractalSite *site
	) : 
	m_pfo(pfo), m_cmap(cmap), m_site(site)
	{

	}
    virtual ~pf_wrapper()
	{
	    /* we don't own the member pointers, so we don't delete them */
	}
    virtual void calc(
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        rgba_t *color, int *pnIters) const
	{
	    double dist; 
	    int fate;
	    m_pfo->vtbl->calc(m_pfo, params, nIters, nNoPeriodIters, x, y, aa,
			      pnIters, &fate, &dist);

	    //printf("%d,%d,%g\n",*pnIters,fate,dist);
	    if(fate == 1)
	    {
		*pnIters = -1;
	    }
	    *color = cmap_lookup_with_transfer(m_cmap,fate,dist);

	    m_site->pixel_changed(
		params,nIters,nNoPeriodIters,
		x,y,aa,
		dist,fate,*pnIters,
		color->r, color->g, color->b, color->a);
	}
    inline rgba_t recolor(double dist) const
	{	    
	    return cmap_lookup(m_cmap,dist);
	}
};


pointFunc *pointFunc::create(
    pf_obj *pfo,
    cmap_t *cmap,
    IFractalSite *site)
{
    if(NULL == pfo || NULL == cmap)
    {
	return NULL;
    }

    return new pf_wrapper(pfo,cmap,site);
}

