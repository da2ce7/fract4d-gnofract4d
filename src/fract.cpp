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

#include <stdlib.h>

#include <gnome.h>
#include "calc.h"

#include "gf4d_fractal.h"
#include "fract.h"
#include "image.h"
#include "test-fonction.h"
#include <fstream>


void 
debug_precision(const d& s, char *location)
{
#if !defined(NDEBUG) && defined(HAVE_CLN)
	ostrstream os;
	os << float_epsilon(cl_float_format(s)) << std::ends;
	g_print("%s : %s\n",location,os.str());
#endif
}

/* ctor */
fractal::fractal()
{
	reset();

	// display params
	aa_profondeur = 2;
	auto_deepen = 1;
	r = 1.0;
	g = 0.0;
	b = 0.0;

	move_by = M_PI/20.0;
	digits = 0;
	
	running = false;
	finished = false;
}

/* dtor */
fractal::~fractal()
{

}

/* call destructor & set ptr to NULL */
void
fract_delete(fractal_t **fp)
{
	fractal_t *f = *fp;
	delete f;
	*fp = NULL;
}

/* the program wants to exit: stop calculating */
void 
fractal::finish()
{
	running = 0;
	finished = 1;
}

/* copy ctor */
fractal::fractal(fractal& f)
{	
	for(int i = 0 ; i < N_PARAMS ; i++)
	{
		params[i] = f.params[i];
	}
	nbit_max = f.nbit_max;
	fractal_type = f.fractal_type;
	aa_profondeur = f.aa_profondeur;
	auto_deepen = f.auto_deepen;
	r = f.r;
	g = f.g;
	b = f.b;
	move_by = f.move_by;
	digits = f.digits;
	running = f.running;
	finished = f.finished;
}

/* return to mandelbrot set */
void 
fractal::reset()
{
	params[XCENTER] = params[YCENTER] = 0.0;
	params[ZCENTER] = params[WCENTER] = 0.0;
	
	params[SIZE] = 4.0;
	params[BAILOUT] = 4.0;
	for(int i = XYANGLE; i < ZWANGLE+1; i++) {
		params[i] = 0.0;
	}

	nbit_max = 64;
	fractal_type = 1;
}

bool fractal::write_params(const char *filename)
{
	std::ofstream os(filename);

	if(!os) return false;

	for(int i = 0; i < N_PARAMS; i++) {
		os << params[i] << "\n";
	}

	os << nbit_max << "\n";
	os << fractal_type << "\n";
	os << aa_profondeur << "\n";
	os << r << "\n" << g << "\n" << b << "\n";

	if(!os) return false;
	return true;
}

bool
fractal::load_params(const char *filename)
{
	std::ifstream is(filename);

	if(!is) return false;

	for(int i = 0; i < N_PARAMS; i++) {
		is >> params[i];
	}

	is >> nbit_max;
	is >> fractal_type;
	is >> aa_profondeur;
	is >> r >> g >> b;
	if(!is) return false;
	return true;
}

void
fractal::set_max_iterations(int val)
{
	nbit_max = val;
}

int 
fractal::get_max_iterations()
{
	return nbit_max;
}

void 
fractal::set_aa(int val)
{
	aa_profondeur = val;
}

int 
fractal::get_aa()
{
	return aa_profondeur;
}

void 
fractal::set_auto(int val)
{
	auto_deepen = val;
}

int 
fractal::get_auto()
{
	return auto_deepen;
}

void fract_set_color(fractal_t *p, double r, double g, double b)
{
	p->r = r; p->g = g; p->b = b;
}

double 
fractal::get_r()
{
	return r;
}

double 
fractal::get_g()
{
	return g;
}

double 
fractal::get_b()
{
	return b;
}


bool fractal::set_precision(int digits)
{
#ifdef HAVE_CLN
	cl_float_format_t fmt = cl_float_format(digits);
	for(int i = 0; i < N_PARAMS; i++) {
		f->params[i] = cl_float(f->params[i],fmt);
	}

	debug_precision(f->params[XCENTER],"set precision:x");
	g_print("new bits of precision: %d\n",float_digits(f->params[SIZE]));
	if(float_digits(f->params[SIZE]) > 53)
	{
		f->fractal_type = 1;
	} else {
		f->fractal_type = 0;
	}
	return 1;
#else
	return 0;
#endif
}

/* see if we have run out of precision. either extend float format or 
 * (if CLN isn't available) warn user 
 */
int fract_check_precision(fractal *p)
{
	// assume image < 1024 pixels wide
	d delta = (p->params[SIZE])/D_LIKE(1024.0,p->params[SIZE]);

	debug_precision(p->params[SIZE],"check precision");

#ifdef HAVE_CLN
	if (delta < float_epsilon(cl_float_format(p->params[SIZE]))*D_LIKE(10.0,p->params[SIZE])) { 
		g_print("increasing precision from %d\n",float_digits(delta)); 
		// float_digits gives bits of precision,
		// cl_float takes decimal digits. / by 3 should be safe?
		fract_set_precision(p,float_digits(delta)/3 +4);
		return 0;
	}
#else
	if ( delta < 1.0e-15)
	{
		gtk_widget_show(gnome_warning_dialog(_("Sorry, max precision was reached, the image will become horrible !")));
		return 0;
	}	
#endif

	return 1;
}

bool fractal::set_param(param_t pnum, const char *val)
{
	g_return_val_if_fail(pnum > -1 && pnum < N_PARAMS,false);
	params[pnum] = A2D(val);
	return true;
}

char *
fractal::get_param(param_t pnum)
{
	D2ADECL;
	g_return_val_if_fail(pnum > -1 && pnum < N_PARAMS,NULL);
	return D2A(params[pnum]);
}

dmat4 get_rotated_matrix(fractal *f)
{
	debug_precision(f->params[XYANGLE],"xyangle");
	d one = D_LIKE(1.0,f->params[SIZE]);
	d zero = D_LIKE(0.0, f->params[SIZE]);
	dmat4 id = identity3D<d>(f->params[SIZE],zero);

	debug_precision(id[VX][VY],"id 1");

	id =  id * 
		rotXY<d>(f->params[XYANGLE],one,zero) *
		rotXZ<d>(f->params[XZANGLE],one,zero) * 
		rotXW<d>(f->params[XWANGLE],one,zero) *
		rotYZ<d>(f->params[YZANGLE],one,zero) *
		rotYW<d>(f->params[YWANGLE],one,zero) *
		rotZW<d>(f->params[ZWANGLE],one,zero);

	// id *= param->size/param->Xres;
	debug_precision(id[VX][VY],"id 3");

	return id;
}

dvec4 get_deltax(fractal *f)
{
	return get_rotated_matrix(f)[VX];
}


dvec4 get_deltay(fractal *f)
{
	return get_rotated_matrix(f)[VY];

}

dvec4 get_center(fractal_t *f)
{
	return dvec4(f->params[XCENTER],f->params[YCENTER],
		     f->params[ZCENTER],f->params[WCENTER]);
}

inline int scan_double(fractal_t *f, bool visual);

void
fractal::recenter(const dvec4& delta)
{
	debug_precision(params[XCENTER],"recenter 1:x");
	params[XCENTER] += delta.n[VX];
	params[YCENTER] += delta.n[VY];
	params[ZCENTER] += delta.n[VZ];
	params[WCENTER] += delta.n[VW];
	debug_precision(params[XCENTER],"recenter 2:x");

}

void
fractal::relocate(double x, double y, double zoom)
{
	dvec4 deltax,deltay;

	// offset to clicked point from center
	d dx = D_LIKE(x,params[SIZE]);
	d dy = D_LIKE(y,params[SIZE]);  

	deltax=get_deltax(this);	
	deltay=get_deltay(this);

	debug_precision(deltax[VX],"relocate:deltax");
	recenter(dx *deltax + dy *deltay);

	debug_precision(params[SIZE],"relocate 1");

	params[SIZE] /= D(zoom);

	debug_precision(params[SIZE],"relocate 2");

	fract_check_precision(this);
}	

template<class T>
void swap(T& a, T& b)
{
	T tmp(a);
	a = b;
	b = tmp;
}

void
fractal::flip2julia(double dx, double dy)
{
	static double rot=M_PI/2;

	dvec4 deltax,deltay;
	
	deltax=get_deltax(this);
	deltay=get_deltay(this);
	
	recenter(dx*deltax + dy *deltay);
	
	params[XZANGLE] += D(rot);
	params[YWANGLE] += D(rot);

	rot = -rot;
}

class fract_rot {
public:
	Gf4dFractal *gf;
	dmat4 rot;
	dvec4 deltax, deltay;
	dvec4 delta_aa_x, delta_aa_y;
	dvec4 topleft;
	int depth;
	d ddepth;
	// n pixels correctly classified that would be wrong if we halved iterations
	int nhalfiters;
        // n pixels misclassified that would be correct if we doubled the iterations
	int ndoubleiters; 
	int k;	
	int last_update_y;
	fractal_t *f;
	colorFunc cf;
	fractFunc pf;
	int *p;
	image *im;
	fract_rot(fractal_t *_f, image *_im, colorFunc _cf, fractFunc _pf, Gf4dFractal *_gf) {
		gf = _gf;
		im = _im;
		f = _f; cf = _cf ; pf = _pf;
		depth = f->aa_profondeur ? f->aa_profondeur : 1; 

		rot = get_rotated_matrix(f)/D(im->Xres);
		deltax = rot[VX];
		deltay = rot[VY];
		ddepth = D_LIKE((double)depth,f->params[SIZE]);
		delta_aa_x = deltax / ddepth;
		delta_aa_y = deltay / ddepth;

		debug_precision(deltax[VX],"deltax");
		debug_precision(f->params[XCENTER],"center");
		topleft = get_center(f) -
		deltax * D_LIKE(im->Xres / 2.0, f->params[SIZE])  -
		deltay * D_LIKE(im->Yres / 2.0, f->params[SIZE]);

		debug_precision(topleft[VX],"topleft");
		nhalfiters = ndoubleiters = k = 0;
		p = new int[im->Xres * im->Yres];
		for(int i = 0; i < im->Xres * im->Yres; i++) {
			p[i]=-1;
		}
		last_update_y = 0;
	};
	~fract_rot() {
		delete[] p;
	}
	void pixel(int x, int y, int h, int w);
	void check_update(int i);
	void rectangle(struct rgb pixel, int x, int y, int h, int w);
	void fourpixel(int x, int y);
	struct rgb antialias(const dvec4& pos);
	bool updateiters();
	void draw(int rsize);
	void draw_aa();
	void pixel_aa(int x, int y);
};

inline void
fract_rot::rectangle(struct rgb pixel, int x, int y, int w, int h)
{
	for(int i = y ; i < y+h; i++)
	{
		char *tmp = im->buffer  + (i * im->Xres + x )*3;
		for(int j = x; j < x+w; j++) {
			*tmp++=pixel.r;
			*tmp++=pixel.g;
			*tmp++=pixel.b;
		}
	}
}

inline struct rgb
fract_rot::antialias(const dvec4& cpos)
{
	struct rgb ptmp;
	unsigned int pixel_r_val=0, pixel_g_val=0, pixel_b_val=0;
	int i,j;
	for(i=0;i<depth;i++) {
		dvec4 pos = cpos + delta_aa_y * (i - ddepth/D_LIKE(2.0,ddepth))  - 
			(ddepth/D_LIKE(2.0,ddepth)) * delta_aa_x;
		for(j=0;j<depth;j++) {
			ptmp = cf(pf(pos, f->params[BAILOUT], f->nbit_max), 
				  f->r, f->g, f->b);
			pixel_r_val += ptmp.r;
			pixel_g_val += ptmp.g;
			pixel_b_val += ptmp.b;
			pos+=delta_aa_x;
		}
	}
	ptmp.r = pixel_r_val / (depth * depth);
	ptmp.g = pixel_g_val / (depth * depth);
	ptmp.b = pixel_b_val / (depth * depth);
	return ptmp;
}

inline void 
fract_rot::pixel(int x, int y,int w, int h)
{
	int *ppos = p + y*im->Xres + x;
	if(!f->running) throw(1);

	dvec4 pos = topleft + I2D_LIKE(x, f->params[SIZE]) * deltax + 
		              I2D_LIKE(y, f->params[SIZE]) * deltay;

	struct rgb pixel;

	//debug_precision(pos[VX],"pixel");
	if(*ppos != -1) return;
		
	*ppos = pf(pos, f->params[BAILOUT], f->nbit_max); 
	pixel=cf(*ppos,f->r, f->g, f->b);

	rectangle(pixel,x,y,w,h);
	
	// test for iteration depth
	if(f->auto_deepen && k++ % 30 == 0)
	{
		if(pf(pos,f->params[BAILOUT], f->nbit_max/2)==-1)
		{
			if(pf(pos,f->params[BAILOUT], f->nbit_max)==-1)
			{
				if(pf(pos,f->params[BAILOUT], f->nbit_max*2) != -1)
				{
					ndoubleiters++; 
				}
			}
			else
			{
				nhalfiters++;
			}
		}
	}
};

inline void
fract_rot::pixel_aa(int x, int y)
{
	if(!f->running) throw(1);

	dvec4 pos = topleft + I2D_LIKE(x, f->params[SIZE]) * deltax + 
		              I2D_LIKE(y, f->params[SIZE]) * deltay;

	struct rgb pixel;

	pixel = antialias(pos);

	rectangle(pixel,x,y,1,1);
}

inline void
fract_rot::fourpixel(int x, int y)
{
	pixel(x,y,1,1);
	pixel(x+1,y,1,1);
	pixel(x+2,y,1,1);
	pixel(x+3,y,1,1);
}

void
fract_rot::check_update(int i)
{
	gf4d_fractal_image_changed(gf,0,last_update_y,im->Xres,i);
	gf4d_fractal_progress_changed(gf,(gfloat)i/(gfloat)im->Yres);
	last_update_y = i;
}

// see if the image needs more (or less) iterations to display properly
bool
fract_rot::updateiters()
{
	double doublepercent = ((double)ndoubleiters*30*100)/k;
	double halfpercent = ((double)nhalfiters*30*100)/k;
		
	if(doublepercent > 1.0) 
	{
		// more than 1% of pixels are the wrong colour! 
		// quelle horreur!
		f->nbit_max *= 2;
		return true;
	}

	if(doublepercent == 0.0 && halfpercent < 0.5 && 
		f->nbit_max > 32)
	{
		// less than .5% would be wrong if we used half as many iters
		// therefore we are working too hard!
		f->nbit_max /= 2;
	}
	return false;
}

void fract_rot::draw_aa()
{
	int w = im->Xres;
	int h = im->Yres;

	last_update_y=0;
	ndoubleiters=0;
	nhalfiters=0;

	gf4d_fractal_image_changed(gf,0,0,w,h);
	gf4d_fractal_progress_changed(gf,0.0);

	for(int y = 0; y < h ; y++) {
		check_update(y);
		for(int x = 0; x < w ; x++) {
			pixel_aa ( x, y);
		}
	}
	gf4d_fractal_image_changed(gf,0,0,w,h);		     
	gf4d_fractal_progress_changed(gf,1.0);	
}

void fract_rot::draw(int rsize)
{
	int x,y;
	int w = im->Xres;
	int h = im->Yres;

	last_update_y=0;
	ndoubleiters=0;
	nhalfiters=0;

	gf4d_fractal_image_changed(gf,0,0,w,h);
	gf4d_fractal_progress_changed(gf,0.0);

	// size-4 blocks & extra pixels at end of lines
	for (y = 0 ; y < h - 4 ; y += 4) {
		check_update(y);
		for ( x = 0 ; x< w - 4 ; x += 4) {
			pixel ( x, y, rsize, rsize);
		}
		for(; x< w ; x++) {
			pixel (x, y,  1, 1);
			pixel (x, y+1,1, 1);
			pixel (x, y+2,1, 1);
			pixel (x, y+3,1, 1);
		}
	}
	// remaining lines
	for ( ; y < h ; y++)
	{
		check_update(y);
		for (x = 0 ; x < w ; x++) {
			pixel (x, y, 1, 1);
		}

	}

	last_update_y=0;
	ndoubleiters=0;
	nhalfiters=0;
	
	// fill in gaps in the 4-blocks
	for ( y = 0; y < h - 4; y += 4) {
		check_update(y);
		for(x = 0; x < w - 4 ; x += 4) {
			int pthis = p[y * w + x];
			if(pthis == p[y * w + x +4] &&
			   pthis == p[(y+4) * w +x] &&
			   pthis == p[(y+4) * w + x+ 4]) {
				// all 4 corners equal, so assume
				// square is flat
				continue;
			}
			
			pixel(x+1,y,1,1);
			pixel(x+2,y,1,1);
			pixel(x+3,y,1,1);
			fourpixel(x,y+1);
			fourpixel(x,y+2);
			fourpixel(x,y+3);
				
		}		
	}

	gf4d_fractal_image_changed(gf,0,0,im->Xres,im->Yres);	
	gf4d_fractal_progress_changed(gf,1.0);	

}

void
fractal::calc(Gf4dFractal *gf, image *im)
{
	if(running) {
		/* we've been called from an idle callback : interrupt current
		   calculation and return */
		running = 0;
		return;
	}

	do {
		running = 1;
		fractFunc pf= fractFuncTable[fractal_type];
		fract_rot pr(this, im, colorize, pf,gf);
		
		try {
			gf4d_fractal_status_changed(gf,GF4D_FRACTAL_CALCULATING);
			
			pr.draw(4);
			while(pr.updateiters())
			{
				gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DEEPENING);
				pr.draw(1);
			}
			
			if(aa_profondeur > 1) {
				gf4d_fractal_status_changed(gf,GF4D_FRACTAL_ANTIALIASING);
				pr.draw_aa();
			}
		}
		catch(int i)
		{
			// interrupted
		}
	}while(!finished && !running);

	running=0;
	gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DONE);
	gf4d_fractal_progress_changed(gf,0.0);
}


