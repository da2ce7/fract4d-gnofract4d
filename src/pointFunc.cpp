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

#define STATIC_FUNCTION

#ifdef STATIC_FUNCTION
#define ITER pTemp[X2] = pIter[X] * pIter[X];pTemp[Y2] = pIter[Y] * pIter[Y];atmp = pTemp[X2] - pTemp[Y2] + pInput[CX];pIter[Y] = 2.0 * pIter[X] * pIter[Y] + pInput[CY];pIter[X] = atmp
#define DECL double atmp 
#define RET 
#define BAIL pTemp[EJECT_VAL] = pTemp[X2] + pTemp[Y2];

#include "compiler_template.cpp"
#endif

pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType, 
    double bailout,
    colorizer *pcf,
    e_colorFunc outerCfType,
    e_colorFunc innerCfType)
{
#ifdef STATIC_FUNCTION
    return (pointFunc *)create_pointfunc(bailout,pcf,outerCfType,innerCfType);
#else
    bailFunc *b = bailFunc_new(bailType);

    std::string iter = iterType->iter_code();
    std::string decl = iterType->decl_code();
    std::string ret  = iterType->ret_code();
    std::string bail = b->bail_code(iterType->flags());
    void *dlHandle = g_pCompiler->getHandle(iter,decl,ret,bail);

    pointFunc *(*pFunc)(
        double, colorizer *, e_colorFunc, e_colorFunc) = 
        (pointFunc *(*)(double, colorizer *, e_colorFunc, e_colorFunc)) 
        dlsym(dlHandle, "create_pointfunc");

    if(NULL == pFunc)
    {
        return NULL;
    }

    return pFunc(bailout, pcf, outerCfType, innerCfType);
#endif
}

