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

#include <unistd.h>
#include <dlfcn.h>

pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType, 
    double bailout,
    colorizer *pcf,
    e_colorFunc outerCfType,
    e_colorFunc innerCfType)
{
#ifdef STATIC_FUNCTION
    return (pointFunc *)create_pointfunc(NULL,bailout,pcf,outerCfType,innerCfType);
#else
    bailFunc *b = bailFunc_new(bailType);

    std::map<std::string,std::string> code_map;
    iterType->get_code(code_map);
    b->get_code(code_map, iterType->flags());
    void *dlHandle = g_pCompiler->getHandle(code_map);

    pointFunc *(*pFunc)(
        void *, double, std::complex<double> *,colorizer *, e_colorFunc, e_colorFunc) = 
        (pointFunc *(*)(void *, double, std::complex<double> *, colorizer *, e_colorFunc, e_colorFunc)) 
        dlsym(dlHandle, "create_pointfunc");

    if(NULL == pFunc)
    {
        return NULL;
    }

    return pFunc(dlHandle, bailout, iterType->opts(), pcf, outerCfType, innerCfType);
#endif
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

