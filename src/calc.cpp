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
#include "test-fonction.h"
#include <strstream>

struct _fractal
{
	char *tmp_img;
	int Xres; 
	int Yres;
	d params[N_PARAMS];
	int nbit_max;
	int fractal_type;
	int aa_profondeur;
	int auto_deepen;
	double r;
	double g;
	double b;
	d move_by;
	int digits;
	bool running;
	bool finished;
};

void 
debug_precision(const d& s, char *location)
{
#if !defined(NDEBUG) && defined(HAVE_CLN)
	ostrstream os;
	os << float_epsilon(cl_float_format(s)) << std::ends;
	g_print("%s : %s\n",location,os.str());
#endif
}

fractal_t *
fract_new()
{
	fractal_t *f = new fractal_t;

	// image params
	f->tmp_img = NULL;
	f->Xres = 400;
	f->Yres = 300;
	fract_reset(f);

	// display params
	f->aa_profondeur = 2;
	f->auto_deepen = 1;
	f->r = 1.0;
	f->g = 0.0;
	f->b = 0.0;

	f->move_by = M_PI/20.0;
	f->digits = 0;
	
	f->running = false;
	f->finished = false;
	return f;
}

void
fract_delete(fractal_t **fp)
{
	fractal_t *f = *fp;
	delete f;
	*fp = NULL;
}

void fract_finish(fractal_t *f)
{
	f->running = 0;
	f->finished = 1;
}

fractal_t *
fract_copy(fractal_t *f)
{
	fractal_t *new_f = new fractal_t;
	*new_f = *f;
	new_f->tmp_img = (char *)calloc(1 * 3 * f->Xres * f->Yres,1);
	return new_f;
}

void fract_reset(fractal_t *f)
{
	f->params[XCENTER] = f->params[YCENTER] = 0.0;
	f->params[ZCENTER] = f->params[WCENTER] = 0.0;

	f->params[SIZE] = 4.0;
	f->params[BAILOUT] = 4.0;
	for(int i = XYANGLE; i < ZWANGLE+1; i++) {
		f->params[i] = 0.0;
	}

	f->nbit_max = 64;
	f->fractal_type = 1;
}

int fract_get_xres(fractal_t *p)
{
	return p->Xres;
}

int fract_get_yres(fractal_t *p)
{
	return p->Yres;
}

char *fract_get_tmp_img(fractal_t *p)
{
	return p->tmp_img;
}

void fract_write_params(fractal_t *p, FILE *file)
{
	for(int i = 0; i < N_PARAMS; i++) {
		fprintf(file,"%s\n",fract_get_param(p,(param_t)i));
	}

	fprintf(file,"%d\n",p->nbit_max);
	fprintf(file,"%d\n",p->fractal_type);
	fprintf(file,"%d\n",p->aa_profondeur);
	fprintf(file,"%g\n%g\n%g\n",p->r, p->g, 
		p->b);
}

void
fract_load_params(fractal_t *p, FILE *file)
{
	char buf[1024];

	for(int i = 0; i < N_PARAMS; i++) {
		fscanf(file,"%s",buf);
		fract_set_param(p,(param_t)i,buf);
	}

	fscanf(file,"%d",&p->nbit_max);
	fscanf(file,"%d",&p->fractal_type);
	fscanf(file,"%d",&p->aa_profondeur);
	
	fscanf(file,"%lf\n%lf\n%lf\n",&p->r, &p->g, &p->b);
}

void fract_set_max_iterations(fractal_t *p, int val)
{
	p->nbit_max = val;
}

int fract_get_max_iterations(fractal_t *p)
{
	return p->nbit_max;
}

void fract_set_aa(fractal_t *p, int val)
{
	p->aa_profondeur = val;
}

int fract_get_aa(fractal_t *p)
{
	return p->aa_profondeur;
}

void fract_set_auto(fractal_t *p, int val)
{
	p->auto_deepen = val;
}

int fract_get_auto(fractal_t *p)
{
	return p->auto_deepen;
}

int fract_set_resolution(fractal_t *p, int x, int y)
{
	if(p->tmp_img && p->Xres == x && p->Yres == y) return 0;
	p->Xres = x;
	p->Yres = y;
	fract_realloc_image(p);
	return 1;
}

void fract_set_color(fractal_t *p, double r, double g, double b)
{
	p->r = r; p->g = g; p->b = b;
}

double fract_get_r(fractal_t *p)
{
	return p->r;
}

double fract_get_g(fractal_t *p)
{
	return p->g;
}

double fract_get_b(fractal_t *p)
{
	return p->b;
}

void fract_move(fractal_t *p, int data)
{
	d amount = p->move_by;

	if(data < 0.0 ) {
		amount = -amount;
		data = -data;
	}

	p->params[data] += amount;
}

void
fract_realloc_image(fractal_t *p)
{
	p->tmp_img = (char *)realloc(p->tmp_img, 3 * p->Xres * p->Yres);
}

void
fract_delete_image(fractal_t *p)
{
	g_free(p->tmp_img);
	p->tmp_img=NULL;
}

double fract_get_ratio(fractal_t *f)
{
	return ((double)f->Yres / f->Xres);
}

int fract_set_precision(fractal_t *f, int digits)
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
int fract_check_precision(fractal_t *p)
{
	d delta = (p->params[SIZE])/p->Xres;

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

void fract_set_param(fractal_t *f, param_t pnum, char *val)
{
	g_return_if_fail(pnum > -1 && pnum < N_PARAMS);
	f->params[pnum] = A2D(val);
}

char *fract_get_param(fractal_t *f, param_t pnum)
{
	D2ADECL;
	g_return_val_if_fail(pnum > -1 && pnum < N_PARAMS,NULL);
	return D2A(f->params[pnum]);
}

dmat4 get_rotated_matrix(fractal_t *f)
{
	debug_precision(f->params[XYANGLE],"xyangle");
	debug_precision(f->params[SIZE]/f->Xres,"t1");
	d one = D_LIKE(1.0,f->params[SIZE]);
	d zero = D_LIKE(0.0, f->params[SIZE]);
	dmat4 id = identity3D<d>(f->params[SIZE]/f->Xres,zero);

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

dvec4 get_deltax(fractal_t *f)
{
	return get_rotated_matrix(f)[VX];
}


dvec4 get_deltay(fractal_t *f)
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
recenter(fractal_t *p, const dvec4& delta)
{
	debug_precision(p->params[XCENTER],"recenter 1:x");
	p->params[XCENTER] += delta.n[VX];
	p->params[YCENTER] += delta.n[VY];
	p->params[ZCENTER] += delta.n[VZ];
	p->params[WCENTER] += delta.n[VW];
	debug_precision(p->params[XCENTER],"recenter 2:x");

}

void
fract_relocate(fractal_t *f, int x, int y, double zoom)
{
	dvec4 deltax,deltay;

	// offset to clicked point from center
	d dx = D_LIKE((x - f->Xres /2),f->params[SIZE]);
	d dy = D_LIKE((y - f->Yres /2),f->params[SIZE]);  

	deltax=get_deltax(f);	
	deltay=get_deltay(f);

	debug_precision(deltax[VX],"relocate:deltax");
	recenter(f,dx *deltax + dy *deltay);

	debug_precision(f->params[SIZE],"relocate 1");

	f->params[SIZE] /= D(zoom);

	debug_precision(f->params[SIZE],"relocate 2");

	fract_check_precision(f);
}	

template<class T>
void swap(T& a, T& b)
{
	T tmp(a);
	a = b;
	b = tmp;
}

void
fract_flip2julia(fractal_t *f, int x, int y)
{
	static double rot=M_PI/2;

	dvec4 deltax,deltay;
	// offset to clicked point from center
	d dx = (double)x - f->Xres /2.0;
	d dy = (double)y - f->Yres /2.0;  
	
	deltax=get_deltax(f);
	deltay=get_deltay(f);
	
	recenter(f, dx*deltax + dy *deltay);
	
	f->params[XZANGLE] += D(rot);
	f->params[YWANGLE] += D(rot);

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
	fract_rot(fractal_t *_f, colorFunc _cf, fractFunc _pf, Gf4dFractal *_gf) {
		gf = _gf;
		f = _f; cf = _cf ; pf = _pf;
		depth = f->aa_profondeur ? f->aa_profondeur : 1; 

		rot = get_rotated_matrix(f);
		deltax = rot[VX];
		deltay = rot[VY];
		ddepth = D_LIKE((double)depth,f->params[SIZE]);
		delta_aa_x = deltax / ddepth;
		delta_aa_y = deltay / ddepth;

		debug_precision(deltax[VX],"deltax");
		debug_precision(f->params[XCENTER],"center");
		topleft = get_center(f) -
		deltax * D_LIKE(f->Xres / 2.0, f->params[SIZE])  -
		deltay * D_LIKE(f->Yres / 2.0, f->params[SIZE]);

		debug_precision(topleft[VX],"topleft");
		nhalfiters = ndoubleiters = k = 0;
		p = new int[f->Xres * f->Yres];
		for(int i = 0; i < f->Xres * f->Yres; i++) {
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
		char *tmp = f->tmp_img  + (i * f->Xres + x )*3;
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
	int *ppos = p + y*f->Xres + x;
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
	gf4d_fractal_image_changed(gf,0,last_update_y,f->Xres,i);
	gf4d_fractal_progress_changed(gf,(gfloat)i/(gfloat)f->Yres);
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
	int w = f->Xres;
	int h = f->Yres;

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
	int w = f->Xres;
	int h = f->Yres;

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

	gf4d_fractal_image_changed(gf,0,0,f->Xres,f->Yres);	
	gf4d_fractal_progress_changed(gf,1.0);	

}

void
fract_calc(fractal_t *f, Gf4dFractal *gf)
{
	if(f->running) {
		/* we've been called from an idle callback : interrupt current
		   calculation and return */
		f->running = 0;
		return;
	}

	do {
		f->running = 1;
		fractFunc pf= fractFuncTable[f->fractal_type];
		fract_rot pr(f, colorize, pf,gf);
		
		try {
			gf4d_fractal_status_changed(gf,GF4D_FRACTAL_CALCULATING);
			
			pr.draw(4);
			while(pr.updateiters())
			{
				gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DEEPENING);
				pr.draw(1);
			}
			
			if(f->aa_profondeur > 1) {
				gf4d_fractal_status_changed(gf,GF4D_FRACTAL_ANTIALIASING);
				pr.draw_aa();
			}
		}
		catch(int i)
		{
			// interrupted
		}
	}while(!f->finished && !f->running);

	f->running=0;
	gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DONE);
	gf4d_fractal_progress_changed(gf,0.0);
}


