/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
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

#ifndef _CALC_H_
#define _CALC_H_
#include "config.h"

#include "vectors.h"

#include <string>
#include <strstream.h>

#ifdef HAVE_CLN
#define WANT_OBFUSCATING_OPERATORS
#include "cl_real.h"
#include "cl_float.h"
#include "cl_float_io.h"
typedef cl_F d;
#define D2ADECL \
 	std::ostrstream os

#define A2D(_x) cl_F(_x);
#define D2A(_x) (os << _x << std::ends, os.str())
#define D(_x) (cl_float(_x,cl_float_format (digits)))
#define D_LIKE(_x,_y) cl_float(_x,_y)
#define I2D_LIKE(_x,_y) cl_float(((double)(_x)),_y)
#define DOUBLE(_x) cl_double_approx(_x)
#else
typedef double d;
#define D2ADECL 
#define A2D(_x) atof(_x)
#define D2A(_x) g_strdup_printf("%g",_x)
#define D(_x) (d)(_x)
#define D_LIKE(_x,_y) (d)(_x)
#define I2D_LIKE(_x,_y) (d)(_x)
#define DOUBLE(_x) _x
#endif

typedef vec4<d> dvec4;
typedef mat4<d> dmat4;


void debug_precision(const d& s, char *location);

#endif /* _CALC_H_ */
