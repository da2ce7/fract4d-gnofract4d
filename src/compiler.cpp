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

/* We use the C compiler at runtime to produce a new shared library containing
 * code which calculates this fractal - this file contains our interface to the
 * compiler */

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "compiler.h"


#include <cstdio>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <dlfcn.h>
#include <errno.h>

#include <iostream>
#include <sstream>

#include "glib.h"

// global compiler instance
compiler *g_pCompiler;

compiler::compiler()
{
    pthread_mutex_init(&cache_lock,NULL);
    cc = "g++";
    flags = "-shared -O3 -ffast-math";
    in = "compiler_template.cpp";
    next_so = 0;
    so_cache_dir = g_get_home_dir() + std::string("/.gnome/" PACKAGE "-cache");
    
    struct stat buf;
    if(stat(so_cache_dir.c_str(),&buf)== -1 && errno == ENOENT)
    {
        // cache dir doesn't exist - create it
        if(mkdir(so_cache_dir.c_str(),0777) == -1)
        {
            // couldn't create the directory
            cerr << "Couldn't create cache directory " << so_cache_dir << std::endl;
            exit(EXIT_FAILURE);
        }
    }
}

std::string
compiler::Dstring(std::string iter, std::string decl, std::string ret, std::string bail)
{
    return "-DITER=\"" + iter + 
        "\" -DDECL=\"" + decl + 
        "\" -DRET=\""  + ret  + 
        "\" -DBAIL=\"" + bail + "\"";
}

// TODO: replace all this with a fork/exec thingy so I can get exit status etc
void *
compiler::compile(std::string commandLine)
{
    char buf[PATH_MAX];

    cout << commandLine << std::endl;
    FILE *compiler_output = popen(commandLine.c_str(),"r");
    if(NULL == compiler_output)
    {
        return NULL;
    }
    else
    {
        while(fgets(buf,sizeof(buf),compiler_output))
        {
            printf(buf);
        }
        pclose(compiler_output);
    }
    
    void *dlHandle = dlopen(out.c_str(), RTLD_NOW);
    return dlHandle;
}

void * 
compiler::getHandle(std::string iter, std::string decl, std::string ret, std::string bail)
{
    std::string dflags = Dstring(iter, decl, ret, bail);
    std::string find = flags + dflags;

    void *handle = NULL;
    pthread_mutex_lock(&cache_lock);

    t_cache::iterator i = cache.find(find);
    if(i == cache.end())
    {
        ostringstream os;
        os << so_cache_dir << "/fract" << (next_so++) << ".so";
        out = os.str();

        std::string commandLine = 
            cc + " " + flags + " " + dflags + " " + in + " -o " + out + " 2>&1";

        handle = compile(commandLine);
        if(NULL != handle)
        {
            cache[find] = handle;
        }
    }
    else
    {
        handle = i->second;
    }
    pthread_mutex_unlock(&cache_lock);

    return handle;
}


