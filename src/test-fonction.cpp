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

#include <gnome.h>
#include "model.h"
//#include "fract.h"
#include "calc.h"
#include "test-fonction.h"
#include <math.h>

#include <iostream>

int test_cube(const dvec4& params, const d& eject, int nIters);

fractFunc fractFuncTable[NFUNCS] = {
	test_mandelbrot_double,
	test_mandelbrot_cln,
};

/* FIXME: at low iteration counts, this can use 30% of calculation time:
 * this could be reduced by precalcing 1.0 + contrast * {r,g,b} and 
 * just doing dn * iter at runtime. 
 * or even construct a palette by using different n until a cycle occurs 
 * cycle time = 256 * lcd ( 1/r, 1/g, 1/b), ie can be very large if r 
 * is approximately g etc.
 */

struct rgb colorize(int n, double r, double g, double b)
{
	struct rgb pixel={0,0,0};
	double contrast = 3.0;
	double dn;

	if (n == -1){
		pixel.r = pixel.g = pixel.b = 0;
	} else {
		dn = (double)n;
		pixel.r = (char)(dn * (1.0 + contrast * r));
		pixel.g = (char)(dn * (1.0 + contrast * g));
		pixel.b = (char)(dn * (1.0 + contrast * b));
	}
	return pixel;
}

// z = z^2 + c

int test_mandelbrot_double(const dvec4& params, const d& eject, int nIters)
{
	double  a =  DOUBLE(params.n[VZ]), 
		b =  DOUBLE(params.n[VW]), 
		px = DOUBLE(params.n[VX]), 
		py = DOUBLE(params.n[VY]), 
		e =  DOUBLE(eject),
		atmp;

	int n = 0;
	while ((a * a + b * b) <= e) {
		atmp = a * a - b * b + px;
		b = 2 * a * b + py;
		a = atmp;
		if(n++ == nIters) return -1; // ran out of iterations
	}
	return n;
}

int test_mandelbrot_cln(const dvec4& params, const d& eject, int nIters)
{
	d a = params.n[VZ], b = params.n[VW], 
		px = params.n[VX], py = params.n[VY], 
		atmp = D_LIKE(0.0,a), 
		a2 = a*a, b2=b*b;

	//debug_precision(a,"a");
	int n = 0;
	while ((a2 + b2) <= eject) {
		atmp = a2 - b2 + px;
		b = (a + a) * b + py;
		a = atmp;
		if(n++ == nIters) return -1; // ran out of iterations
		a2 = a*a; b2 = b*b;
	}
	return n;
}

// z = z^3 + c
int
test_cube(const dvec4& params, const d& eject, int nIters)
{
	d a = params.n[VZ], b = params.n[VW],
		px = params.n[VX], py = params.n[VY], atmp;

	int n = 0;

	while((a * a + b * b) <= eject) {
		atmp = a * a * a - 3 * a * b * b +px;
		b = 3 * a * a * b - b * b * b + py;
		a = atmp;
		if(n++ == nIters) return -1;
	}
	return n;
}


/*
int test_julia(double *params, int nIters)
{
	
	register double a = params[X], atmp = 0, b = params[Y];
	int n = 0;
	while ((a * a + b * b) <= params[EJECT]) {
		atmp = a * a - b * b + params[PX];
		b = 2 * a * b + params[PY];
		a = atmp;
		if(n++ == nIters) return -1;
	}
	return n;
}

int test_perso(double *params, int nIters)
{
	
	register double a = 0, atmp = 0, b = 0;
	int n = 0;
	while ((a * a + b * b) <= params[EJECT]) {
		atmp = a * a - b * b + params[X];
		b = 2 * a * b + params[Y];
		a = atmp;
		if(n++ == nIters) return -1;
	}
	return n;
}
*/
