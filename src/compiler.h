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

class compiler
{
    std::string cc;
    void *err_callback_data;
    void (*err_callback)(void *,const char *, const char *);
public:
    void set_err_callback(void (*cb)(void *, const char *, const char *), 
			  void *cbdata) 
	{
	    err_callback = cb; err_callback_data = cbdata;
	}
    void set_cc(const char *s);
    void set_cache_dir(const char *s); 
    const char *get_cc() { return cc.c_str(); }
    std::string flags; 
    std::string in;
    std::string out;

    compiler();

    void *getHandle(std::map<std::string,std::string> defn_map);

 private:
    void on_error(std::string message, std::string extra_info) { 
        assert(err_callback != NULL); 
        (*err_callback)(err_callback_data, message.c_str(), extra_info.c_str()); 
    }
    void on_error(std::string message) {
	assert(err_callback != NULL);
	(*err_callback)(err_callback_data,message.c_str(), NULL);
    }
    typedef std::map<std::string,std::string> t_cache;
    t_cache cache;
    int next_so;
    pthread_mutex_t cache_lock;
    std::string so_cache_dir;

    void *compile(std::string commandLine);
    std::string Dstring(std::map<std::string,std::string> defn_map);

    void invalidate_cache();
    std::string flow(std::string in);
};

// pointer to global compiler instance
extern compiler *g_pCompiler;

#endif /* COMPILER_H_ */
