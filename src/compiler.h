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

#include "pthread.h"

class compiler
{
public:
    std::string cc;
    std::string flags; 
    std::string in;
    std::string out;

    compiler();

    void *getHandle(std::string iter, std::string decl, std::string ret, std::string bail);

 private:
    typedef std::map<std::string,void *> t_cache;
    t_cache cache;
    int next_so;
    pthread_mutex_t cache_lock;
    std::string so_cache_dir;

    void *compile(std::string commandLine);
    std::string Dstring(std::string iter, std::string decl, std::string ret, std::string bail);
};

// pointer to global compiler instance
extern compiler *g_pCompiler;

#endif /* COMPILER_H_ */
