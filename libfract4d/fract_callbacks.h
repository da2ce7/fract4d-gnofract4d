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

#ifndef _FRACT_CALLBACKS_H_
#define _FRACT_CALLBACKS_H_

#ifdef __cplusplus
extern "C" {
#endif

#if 0
//}
#endif

#ifdef _WIN32
class Gf4dFractal;
#else
typedef struct _Gf4dFractal Gf4dFractal;
#endif

struct s_fract_callbacks
{
    // callback functions we use to inform the host program of
    // the status of the ongoing calculation. 
    // WARNING: these are called back on a different thread, possibly
    // several different threads at the same time. It is the callee's 
    // responsibility to handle mutexing.

    void (*parameters_changed)(Gf4dFractal *f);
    void (*image_changed)(Gf4dFractal *f, int x1, int x2, int y1, int y2);
    void (*progress_changed)(Gf4dFractal *f, float progress);
    void (*status_changed)(Gf4dFractal *f, int status_val);

    // returns true if we've been interrupted and are supposed to stop
    bool (*try_finished_cond)(Gf4dFractal *f);
};

typedef struct s_fract_callbacks fract_callbacks;

#ifdef __cplusplus
}
#endif

#endif /* _FRACT_CALLBACKS_H_ */
