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
 
#ifndef _FRACT_H_
#define _FRACT_H_
/*
*	divers
*/

#ifdef __cplusplus
extern "C" {
#endif



void fract_relocate(fractal_t *f, int x, int y, double zoom);
void fract_flip2julia(fractal_t *f, int x, int y);
void fract_calc(fractal_t *f, Gf4dFractal *gf4d);

fractal_t * fract_new();
void fract_delete(fractal_t **pf);
fractal_t * fract_copy(fractal_t *f); // copy ctor

void fract_reset(fractal_t *f);
void fract_finish(fractal_t *f);

void fract_write_params(fractal_t *f, FILE *fp);
void fract_load_params(fractal_t *f, FILE *fp);

/* accessor functions */
int fract_get_xres(fractal_t *f);
int fract_get_yres(fractal_t *f);
int fract_get_max_iterations(fractal_t *f);
char *fract_get_tmp_img(fractal_t *f);
double fract_get_ratio(fractal_t *f);
double fract_get_r(fractal_t *f);
double fract_get_g(fractal_t *f);
double fract_get_b(fractal_t *f);
int fract_get_aa(fractal_t *f);
int fract_get_auto(fractal_t *f);
char *fract_get_param(fractal_t *f, param_t i);

/* update functions */
void fract_set_max_iterations(fractal_t *f, int val);
void fract_set_param(fractal_t *f, param_t i, char *val);
void fract_set_aa(fractal_t *f, int val);
void fract_set_auto(fractal_t *f, int val);

int  fract_set_resolution(fractal_t *f, int xres, int yres);
void fract_set_color(fractal_t *f, double r, double g, double b);
void fract_realloc_image(fractal_t *f);
int fract_set_precision(fractal_t *f, int digits);
void fract_delete_image(fractal_t *f);

void fract_move(fractal_t *f, int data);

void fract_interrupt(fractal_t *f);


#ifdef __cplusplus
}
#endif

#endif /* _FRACT_H_ */
