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

#include "fract_public.h"
#include "calc.h"

struct fractal
{
public:
	d params[N_PARAMS];
	int nbit_max;
	int fractal_type;
	int aa_profondeur;
	int auto_deepen;
	double r;
	double g;
	double b;
	int digits;
	bool running;
	bool finished;

public:
	fractal();
	fractal(fractal& f); // copy ctor
	~fractal();
	void reset();
	void calc(Gf4dFractal *gf4d, image *im);
	void relocate(double x, double y, double zoom);
	void flip2julia(double x, double y);
	bool write_params(const char *filename);
	bool load_params(const char *filename);
	char *get_param(param_t i);
	bool set_param(param_t i, const char *val);
	void set_max_iterations(int val);
	void set_aa(int val);
	void set_auto(int val);
	int get_max_iterations();
	int get_aa();
	int get_auto();
	void finish();
	double get_r();
	double get_g();
	double get_b();
	bool set_precision(int digits); // not implemented
private:
	void recenter(const dvec4& delta);
};

void fract_delete(fractal_t **f);




/* accessor functions */
int fract_get_xres(fractal_t *f);
int fract_get_yres(fractal_t *f);

char *fract_get_tmp_img(fractal_t *f);
double fract_get_ratio(fractal_t *f);

/* update functions */

int  fract_set_resolution(fractal_t *f, int xres, int yres);
void fract_set_color(fractal_t *f, double r, double g, double b);
void fract_realloc_image(fractal_t *f);
void fract_delete_image(fractal_t *f);




#endif /* _FRACT_H_ */
