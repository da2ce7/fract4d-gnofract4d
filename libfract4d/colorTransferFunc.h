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

/* A colorTransferFunc applies a mapping (eg, log) to the raw color
   distance produced by a colorFunc before passing it on to the
   colorizer for lookup in the colormap. 
*/

#ifndef COLORTRANSFERFUNC_H_
#define COLORTRANSFERFUNC_H_

#include "colorizer_public.h"
#include "pointFunc_public.h"

#include <iosfwd>
#include <string>

// abstract base class
class colorTransferFunc {
 public:
    static colorTransferFunc *create(const char *name);
    static colorTransferFunc *read(std::istream& s);
    static const char **names();
    virtual double calc(double colorDist) const = 0;
    virtual ~colorTransferFunc() {};
};


#endif /*COLORTRANSFERFUNC_H_*/
