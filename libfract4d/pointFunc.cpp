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
#include "colorFunc.h"
#include "colorTransferFunc.h" 

#include <unistd.h>
#include <dlfcn.h>


class pf_wrapper : public pointFunc
{
private:
    colorizer **m_ppcizer;
    void *m_handle; 
    iterFunc *m_iterType;
    colorFunc *m_pOuterColor;
    colorFunc *m_pInnerColor;
    colorTransferFunc *m_pOuterCTF;    
    colorTransferFunc *m_pInnerCTF;

    pf_obj *m_pfo;
    void *one_space;
    
public:
    pf_wrapper(
	pf_obj *pfo,
	iterFunc *iterType,
	double bailout,
	double period_tolerance,
	std::complex<double> *params,
	colorizer **ppcizer, 
	void *dlHandle, 
	e_colorFunc outerCfType, e_colorFunc innerCfType,
	const char *outerCtfType, const char *innerCtfType
	) : 
	m_ppcizer(ppcizer), m_handle(dlHandle), m_iterType(iterType), m_pfo(pfo)
	{
	    m_pfo->vtbl->init(m_pfo,bailout,period_tolerance,params);

            m_pOuterColor = colorFunc_new(outerCfType);
            m_pInnerColor = colorFunc_new(innerCfType);
	    m_pOuterCTF = colorTransferFunc::create(outerCtfType);
	    m_pInnerCTF = colorTransferFunc::create(innerCtfType);

	    one_space = malloc(buffer_size());
	}
    virtual ~pf_wrapper()
	{
            delete m_pOuterColor;
            delete m_pInnerColor;
	    delete m_pOuterCTF;
	    delete m_pInnerCTF;

	    free(one_space);

	    m_pfo->vtbl->kill(m_pfo);
	    if(NULL != m_handle) 
	    {
		dlclose(m_handle);
	    }
	}
    virtual void calc(
        // in params
        const double *params, int nIters, int nNoPeriodIters,
	// only used for debugging
	int x, int y, int aa,
        // out params
        struct rgb *color, int *pnIters, void *out_buf) const
	{


	    if(NULL == out_buf) out_buf = one_space;


	    double *pIterData;
	    m_pfo->vtbl->calc(m_pfo, params, nIters, nNoPeriodIters, x, y, aa,
			      pnIters, &pIterData);

	    double colorDist= colorize(*pnIters,pIterData,out_buf);

	    if(color)
	    {
		*color = calcColor(*pnIters,colorDist);
	    }
	}
    inline rgb_t calcColor(int iter, double dist) const
	{
	    int id = iter == -1 ? 1 : 0;
	    return  m_ppcizer[id]->calc(dist);
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
    inline colorTransferFunc *getColorTransferFunc(int iter) const
	{
	    if(iter == -1)
	    {
		return m_pInnerCTF;
	    }
	    else
	    {
		return m_pOuterCTF;
	    }
	}

    inline double colorize(int iter, const double *p, void *out_buf) const
        {
            double colorDist;
	    colorFunc *pcf = getColorFunc(iter);
	    pcf->extract_state(p,out_buf);
	    colorDist = (*pcf)(iter, p[EJECT],out_buf);
	    colorTransferFunc *pctf = getColorTransferFunc(iter);
	    colorDist = pctf->calc(colorDist);
            return colorDist; 
        }
    virtual rgb_t recolor(int iter, double eject, const void *buf) const
	{
	    colorFunc *pcf = getColorFunc(iter);
	    double dist = (*pcf)(iter, eject, buf);
	    colorTransferFunc *pctf = getColorTransferFunc(iter);
	    dist = pctf->calc(dist);
            return calcColor(iter,dist);
	}
    virtual int buffer_size() const
	{
	    return std::max(m_pInnerColor->buffer_size(),
		       m_pOuterColor->buffer_size());
	}
};


pointFunc *pointFunc::create(
    iterFunc *iterType, 
    bailFunc *bailType, 
    double bailout,
    double periodicity_tolerance,
    colorizer **ppcf,
    e_colorFunc outerCfType,
    e_colorFunc innerCfType,
    const char *outerCtfType,
    const char *innerCtfType)
{
    std::map<std::string,std::string> code_map;
    iterType->get_code(code_map);
    bailType->get_code(code_map, iterType->flags());

    // disable periodicity if inner function will show its effect
    if(innerCfType != COLORFUNC_ZERO)
    {
	code_map["NOPERIOD"]="1";
    }
	    
    void *dlHandle = g_pCompiler->getHandle(code_map);

    // get a pointer to the pf_new function in the new .so
    pf_obj *(*pFunc)() = (pf_obj *(*)()) dlsym(dlHandle, "pf_new");

    if(NULL == pFunc)
    {
	return NULL;
    }
	    
    // create a new pf_obj
    pf_obj *p = (*pFunc)();
	    
    return new pf_wrapper(
	p,
	iterType,
	bailout,
	periodicity_tolerance,
	iterType->opts(),
	ppcf, dlHandle, 
	outerCfType, innerCfType,
	outerCtfType, innerCtfType);
}

