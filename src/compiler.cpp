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

// global compiler instance
compiler *g_pCompiler;

compiler::compiler()
{
    pthread_mutex_init(&cache_lock,NULL);
    flags = "-shared -O3 -ffast-math";
    in = "compiler_template.cpp";
    next_so = 0;    
    set_cc("g++");
}

void
compiler::set_cc(const char *s)
{
  //check_version(s);
    cc = s; invalidate_cache(); 
}

void
compiler::set_cache_dir(const char *s)
{ 
    so_cache_dir = s; invalidate_cache();
    struct stat buf;
    if(stat(so_cache_dir.c_str(),&buf)== -1 && errno == ENOENT)
    {
        // cache dir doesn't exist - create it
        if(mkdir(so_cache_dir.c_str(),0777) == -1)
        {
            // couldn't create the directory
            on_error("Couldn't create cache directory '" + so_cache_dir +"':\n\n" +
                     strerror(errno));
            exit(EXIT_FAILURE);
        }
    }
}
std::string
compiler::Dstring(std::map<std::string,std::string> defn_map)
{
    std::ostringstream os;
    std::map<std::string,std::string>::iterator i;
    for(i = defn_map.begin(); i != defn_map.end(); ++i)
    {
        os << "-D" << i->first << "=\"" << i->second << "\" ";
    }
    return os.str();
}

// TODO: replace all this with a fork/exec thingy so I can get exit status etc
void *
compiler::compile(std::string commandLine)
{
    char buf[PATH_MAX];
    std::string complaints;

    //std::cout << commandLine << std::endl;
    FILE *compiler_output = popen(commandLine.c_str(),"r");
    if(NULL == compiler_output)
    {
        on_error(std::string("Couldn't execute compiler: ") + strerror(errno));
        return NULL;
    }
    else
    {
        while(fgets(buf,sizeof(buf),compiler_output))
        {
            complaints += buf;
        }
        pclose(compiler_output);
    }
    
    void *dlHandle = dlopen(out.c_str(), RTLD_NOW);
    if(!dlHandle)
    {
        on_error(
	    std::string("Error compiling fractal code. "
                        "Check your compiler settings.'"),
	    std::string("Error was: '") + strerror(errno) + 
			"'\n\n" + "Command used was:\n\n" +
			commandLine + "\n\nCompiler output was:\n\n" +
			complaints);
    }
    return dlHandle;
}

void
compiler::invalidate_cache()
{
    pthread_mutex_lock(&cache_lock);
    cache.clear();
    pthread_mutex_unlock(&cache_lock);
}

void * 
compiler::getHandle(std::map<std::string,std::string> defn_map)
{
    std::string dflags = Dstring(defn_map);
    std::string find = flags + dflags;

    void *handle = NULL;
    pthread_mutex_lock(&cache_lock);

    t_cache::iterator i = cache.find(find);
    if(i == cache.end())
    {
        std::ostringstream os;
        os << so_cache_dir << "/fract" << (next_so++) << ".so";
        out = os.str();

        unlink(out.c_str()); // make sure old output file isn't left there
        std::string commandLine = 
            cc + " " + flags + " " + dflags + " " + in + " -o " + out + " 2>&1";
        
        handle = compile(commandLine);
        if(NULL == handle)
        {
            /* cache the fact that an error occurred, so we don't report
               it over & over. This will be cleared when the cache is 
               next invalidated
            */
            cache[find] = "##error";
        }
        else
        {
            cache[find] = out;
        }
    }
    else
    {
        if(i->second == "##error")
        {
            /* an error occurred last time we compiled this */
            handle = NULL; 
        }
        else
        {
            handle = dlopen(i->second.c_str(), RTLD_NOW);
        }
    }

    pthread_mutex_unlock(&cache_lock);

    return handle;
}

// chop the string up so new-lines aren't too far apart
// chop only at whitespace
std::string
compiler::flow(std::string in)
{
    std::string::size_type max_width = 40;
    std::string::size_type last_break_pos = 0;
    std::string::size_type last_space_pos = in.find(' ');
    if(last_space_pos == std::string::npos)
    {
        return in;
    }
    std::ostringstream os;

    os << in.substr(0,last_space_pos);

    std::string::size_type this_space_pos;
    while((this_space_pos = in.find(' ', last_space_pos+1)) != std::string::npos)
    {
        if(this_space_pos - last_break_pos > max_width)
        {
            os << "\n";
            last_break_pos = last_space_pos;
        }
        os << in.substr(last_space_pos,this_space_pos-last_space_pos);
        
        last_space_pos = this_space_pos;
    }
    os << in.substr(last_space_pos);

    return os.str();
}
