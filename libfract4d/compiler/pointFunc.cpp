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


#include "pf.h"
#include "cmap.h"
#include "pointFunc_public.h"

#include <unistd.h>
#include <dlfcn.h>


class pf_wrapper : public pointFunc
{
private:
    pf_obj *m_pfo;
    cmap_t *m_cmap;

public:
    pf_wrapper(
	pf_obj *pfo,
	cmap_t *cmap
	) : 
	m_pfo(pfo), m_cmap(cmap)
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

	    if(fate == 1)
	    {
		*pnIters = -1;
	    }
	    *color = cmap_lookup(m_cmap,dist);
	}
    inline rgba_t recolor(double dist) const
	{	    
	    return cmap_lookup(m_cmap,dist);
	}
};


pointFunc *pointFunc::create(
    pf_obj *pfo,
    cmap_t *cmap)
{
    if(NULL == pfo || NULL == cmap)
    {
	return NULL;
    }

    return new pf_wrapper(pfo,cmap);
}

