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
    /* returns a code snippet which does bailout */
    virtual std::string bail_code(int flags) const = 0;

    /* add the code snippet to this map */
    virtual void get_code(std::map<std::string,std::string>& map, int flags) const
        {
            map["BAIL"] = bail_code(flags);
            map["UNROLL"]= iter8_ok() ? "1" : "0";
            map["NOPERIOD"] = period_ok() ? "0" : "1";
        }

    /* is it OK to unroll the loop with this bailout type? */
    virtual bool iter8_ok() const = 0;

    /* does periodicity checking work with this bailout type? */
    virtual bool period_ok() const = 0;
};

// factory method to construct bailout function objects 
bailFunc *bailFunc_new(e_bailFunc);
bailFunc *bailFunc_read(std::istream& s);

#endif /* _BAILFUNC_H_ */
