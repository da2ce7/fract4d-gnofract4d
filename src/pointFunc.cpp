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
#include "compiler.h"
#include "colorizer.h"

#include <unistd.h>
#include <dlfcn.h>


class pf_wrapper : public pointFunc
{
private:
    inner_pointFunc *m_pf;
    colorizer *m_pcizer;

public:
    pf_wrapper(inner_pointFunc *pf, colorizer *pcizer) : 
	m_pf(pf), m_pcizer(pcizer)
	{

	}
    virtual void calc(
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        struct rgb *color, int *pnIters, void *out_buf)
	{
	    double colorDist;
	    m_pf->calc(params,nIters, nNoPeriodIters, x , y, aa, 
		       &colorDist, pnIters, out_buf);

	    if(color)
	    {
		*color = m_pcizer->calc(colorDist);
	    }
	}
    virtual ~pf_wrapper()
	{
	    delete m_pf;
	}
    virtual rgb_t recolor(int iter, double eject, const void *buf) const
	{
	    double dist = m_pf->recolor(iter, eject, buf);
            return m_pcizer->calc(dist);
	}
    virtual void *handle()
	{
	    return m_pf->handle();
	}
    virtual int buffer_size() const
	{
	    return m_pf->buffer_size();
	}
};

pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType, 
    double bailout,
    double periodicity_tolerance,
    colorizer *pcf,
    e_colorFunc outerCfType,
    e_colorFunc innerCfType)
{
    bailFunc *b = bailFunc_new(bailType);

    std::map<std::string,std::string> code_map;
    iterType->get_code(code_map);
    b->get_code(code_map, iterType->flags());
    void *dlHandle = g_pCompiler->getHandle(code_map);

    inner_pointFunc *(*pFunc)(
        void *, 
        double, 
        double, 
        std::complex<double> *,
        e_colorFunc, 
        e_colorFunc) = 
        (inner_pointFunc *(*)(void *, double, double, std::complex<double> *, e_colorFunc, e_colorFunc)) 
        dlsym(dlHandle, "create_pointfunc");

    if(NULL == pFunc)
    {
        return NULL;
    }

    inner_pointFunc *inner_pf = pFunc(
	dlHandle, bailout, periodicity_tolerance, 
	iterType->opts(), outerCfType, innerCfType);

    return new pf_wrapper(inner_pf, pcf);
}

/* can't just call dtor because we need to free the handle to the .so
   - and we can't do that *inside* the .so or Bad Things will happen */
void
pointFunc_delete(pointFunc *pF)
{
    if(NULL != pF)
    {
        void *handle = pF->handle();
        delete pF;
        if(NULL != handle) 
        {
            dlclose(handle);
        }
    }
}

