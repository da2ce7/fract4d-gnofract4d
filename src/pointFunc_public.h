/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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


#ifndef _POINTFUNC_PUBLIC_H_
#define _POINTFUNC_PUBLIC_H_

/* an enumeration of the available bailout functions */
// update table in properties.cpp:create_bailout_menu if this changes
typedef enum 
{
    BAILOUT_MAG = 0,
    BAILOUT_MANH,
    BAILOUT_MANH2,
    BAILOUT_OR,
    BAILOUT_AND,
    BAILOUT_REAL,
    BAILOUT_IMAG,
    BAILOUT_DIFF
} e_bailFunc;

/* an enumeration of the available color functions */
typedef enum
{
    COLORFUNC_FLAT,
    COLORFUNC_CONT,
    COLORFUNC_ZERO,
    COLORFUNC_ED
} e_colorFunc;

/* bailout flags */
#define HAS_X2 1
#define HAS_Y2 2
#define USE_COMPLEX 4
#define NO_UNROLL 8
#define NO_PERIOD 16

// iter state
#define X 0
#define Y 1

// input state
#define CX 2
#define CY 3
#define EJECT 4


// temp state
#define X2 5
#define Y2 6
#define EJECT_VAL 7
#define LASTX 8
#define LASTY 9
#define STATE_SPACE (LASTY+1)

#endif
