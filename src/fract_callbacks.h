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

    // these are the only gf4d_fractal functions that fract needs to call
    // they're broken out here to insulate the fractal-drawing code from
    // the front-end

    void gf4d_fractal_parameters_changed(Gf4dFractal *f);
    void gf4d_fractal_image_changed(Gf4dFractal *f, int x1, int x2, int y1, int y2);
    void gf4d_fractal_progress_changed(Gf4dFractal *f, float progress);
    void gf4d_fractal_status_changed(Gf4dFractal *f, int status_val);
    void gf4d_fractal_error_occurred(Gf4dFractal *f, char *message);

    // returns true if we've been interrupted and are supposed to stop
    bool gf4d_fractal_try_finished_cond(Gf4dFractal *f);

#ifdef __cplusplus
}
#endif

#endif /* _FRACT_CALLBACKS_H_ */
