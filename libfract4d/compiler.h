/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 *
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

#ifndef COMPILER_H_
#define COMPILER_H_

#include <string>
#include <vector>
#include <map>
#include <assert.h>

#include "pthread.h"

class IFractal;

// implemented by client 
class ICompilerSite
{
 public:
    // called by compiler to indicate a compile error occurred
    virtual void err_callback(const char *msg, const char *details) = 0;
    virtual ~ICompilerSite() {};
};

// a chunk of code which converts a fractal definition 
// into a C file, then invokes the C compiler to covert 
// it into a library, then loads that
class ICompiler
{
 public:
    static ICompiler *create(ICompilerSite *pcs);

    virtual void set_cache_dir(const char *dir) = 0;
    virtual void *compile(IFractal *f) = 0;
    virtual void *getHandle(std::map<std::string,std::string> defn_map) = 0;

    virtual void set_cc(const char *s) = 0;
    virtual const char *get_cc() = 0;

    virtual void set_in(const char *s) = 0;
    virtual const char *get_in() = 0;

    virtual void set_flags(const char *flags) = 0;
    virtual const char *get_flags() = 0;

    virtual ~ICompiler() {};
};

// pointer to global compiler instance
extern ICompiler *g_pCompiler;

#endif /* COMPILER_H_ */
