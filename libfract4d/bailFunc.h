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

#ifndef _BAILFUNC_H_
#define _BAILFUNC_H_

#include "pointFunc_public.h"

#include <iosfwd>
#include <string>
#include <map>

/* a bailfunc is a function object which determines whether to stop
   iterating */

class bailFunc {
 public:
    static bailFunc *create(e_bailFunc);
    static bailFunc *read(std::istream& is);
    static const char **names();

    virtual ~bailFunc() {};
    /* returns a code snippet which does bailout */
    virtual std::string bail_code(int flags) const = 0;

    /* add the code snippet to this map */
    virtual void get_code(std::map<std::string,std::string>& map, int flags) const
        {
            map["BAIL"] = bail_code(flags);
	    // either iterfunc or bailfunc can veto unrolling or periodicity 
	    // operations. Might allow user to do so too later
            map["UNROLL"]= iter8_ok() && !(flags & NO_UNROLL) ? "1" : "0";
            map["NOPERIOD"] = period_ok() && !(flags & NO_PERIOD) ? "0" : "1";
        }

    // what kind of bailFunc is this anyway? (for persistence)
    virtual e_bailFunc type() const = 0;
    //virtual const char *name() const = 0;

    /* is it OK to unroll the loop with this bailout type? */
    virtual bool iter8_ok() const = 0;

    /* does periodicity checking work with this bailout type? */
    virtual bool period_ok() const = 0;
};

#endif /* _BAILFUNC_H_ */
