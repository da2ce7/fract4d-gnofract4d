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
#include <queue>

#include "soi.h"

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

	digits = 0;
	
	running = false;
	finished = false;
	cizer = colorizer_new(COLORIZER_RGB);
	potential=1;
}

/* dtor */
fractal::~fractal()
{
	colorizer_delete(&cizer);
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
fractal::fractal(const fractal& f)
{	
	for(int i = 0 ; i < N_PARAMS ; i++)
	{
		params[i] = f.params[i];
	}
	nbit_max = f.nbit_max;
	fractal_type = f.fractal_type;
	aa_profondeur = f.aa_profondeur;
	auto_deepen = f.auto_deepen;
	digits = f.digits;
	running = f.running;
	finished = f.finished;
	rot_by = f.rot_by;

	rot = f.rot;

	cizer = f.cizer->clone();
	potential = f.potential;
}

fractal&
fractal::operator=(const fractal& f)
{
	for(int i = 0 ; i < N_PARAMS ; i++)
	{
		params[i] = f.params[i];
	}
	nbit_max = f.nbit_max;
	fractal_type = f.fractal_type;
	aa_profondeur = f.aa_profondeur;
	auto_deepen = f.auto_deepen;
	digits = f.digits;
	running = f.running;
	finished = f.finished;
	rot_by = f.rot_by;

	rot = f.rot;

	colorizer_delete(&cizer);
	cizer = f.cizer->clone();
	potential = f.potential;
	return *this;
}

/* x & y vary by up to 50% of the size */

static double
xy_random(double current, double size)
{
	return current + 0.5 * size * (drand48() - 0.5);
}

/* z & w vary by up to 1.0 / log(size) 
   small size = gradually diminishing changes 
*/

static double
zw_random(double current, double size)
{
	double factor = fabs(1.0 - log(size)) + 1.0;
	return current + (drand48() - 0.5 ) * 1.0 / factor;
}

/* scale independent, but skewed distribution:
   50% no change, 25% += pi/2, 25% += rand() * pi/4;
*/

static double
angle_random()
{
	int type = rand()/(RAND_MAX/5);
	switch(type){
	case 0:
	case 1:
	case 2:
		return 0.0;
	case 3:
		return drand48() > 0.5 ? M_PI/2.0 : -M_PI/2.0;
	default:
		return (drand48() - 0.5) * M_PI/4.0;
	}
}

void
fractal::set_inexact(const fractal& f)
{
	*this = f; // invoke op=

	params[XCENTER] = xy_random(params[XCENTER],params[SIZE]);
	params[YCENTER] = xy_random(params[YCENTER],params[SIZE]);
	params[ZCENTER] = zw_random(params[ZCENTER],params[SIZE]);
	params[WCENTER] = zw_random(params[WCENTER],params[SIZE]);

	for(int i = XYANGLE; i <= ZWANGLE ; i++)
	{	       
		params[i] += angle_random();
	}
	if(drand48() > 0.75)
	{
		params[SIZE] *= drand48() * 2.0;
	}
}

/* return to mandelbrot set */
void 
fractal::reset()
{
	digits=10;
	d zero = D(0.0);
	d four = D(4.0);
	params[XCENTER] = zero;
	params[YCENTER] = zero;
	params[ZCENTER] = zero;
	params[WCENTER] = zero;
	
	params[SIZE] = four;
	params[BAILOUT] = four;
	for(int i = XYANGLE; i < ZWANGLE+1; i++) {
		params[i] = zero;
	}

	nbit_max = 64;
	fractal_type = 0;
	rot_by = M_PI/2.0;
}

e_colorizer
fractal::get_color_type()
{
	return cizer->type();
}

void
fractal::set_color_type(e_colorizer type)
{
	if(type == cizer->type()) return;

	colorizer_delete(&cizer);
	cizer = colorizer_new(type);
}

void
fractal::set_cmap_file(const char *filename)
{
	cmap_colorizer *cmap_cizer = dynamic_cast<cmap_colorizer *>(cizer);
	if(cmap_cizer)
	{
		if(strcmp(cmap_cizer->name.c_str(),filename)==0)
		{
			return; // already set to same file
		}
		cmap_cizer->set_cmap_file(filename);
	}
	else
	{
		g_warning("set_cmap_file on non-cmap colorizer");
	}
}

char *
fractal::get_cmap_file()
{
	cmap_colorizer *cmap_cizer = dynamic_cast<cmap_colorizer *>(cizer);
	if(!cmap_cizer) return NULL;
	return g_strdup(cmap_cizer->name.c_str());
}

bool 
fractal::write_params(const char *filename)
{
	std::ofstream os(filename);

	if(!os) return false;

	for(int i = 0; i < N_PARAMS; i++) {
		os << params[i] << "\n";
	}

	os << nbit_max << "\n";
	os << fractal_type << "\n";
	os << aa_profondeur << "\n";
	os << *cizer << "\n";

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
	colorizer *cizer_tmp = colorizer_read(is);
	if(cizer_tmp)
	{
		colorizer_delete(&cizer);
		cizer = cizer_tmp;
	}
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

void 
fractal::set_color(double _r, double _g, double _b)
{
	rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
	if(!rgb_cizer) return;
	rgb_cizer->set_colors(_r,_g,_b);
}

double 
fractal::get_r()
{
	rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
	if(!rgb_cizer) return 0.0;
	return rgb_cizer->r;
}

double 
fractal::get_g()
{
	rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
	if(!rgb_cizer) return 0.0;
	return rgb_cizer->g;
}

double 
fractal::get_b()
{
	rgb_colorizer *rgb_cizer = dynamic_cast<rgb_colorizer *>(cizer);
	if(!rgb_cizer) return 0.0;
	return rgb_cizer->b;
}


bool 
fractal::set_precision(int digits)
{
#ifdef HAVE_CLN
	cl_float_format_t fmt = cl_float_format(digits);
	for(int i = 0; i < N_PARAMS; i++) {
		params[i] = cl_float(params[i],fmt);
	}

	debug_precision(params[XCENTER],"set precision:x");
	g_print("new bits of precision: %d\n",float_digits(params[SIZE]));
	if(float_digits(params[SIZE]) > 53)
	{
		fractal_type = 1;
	} else {
		fractal_type = 0;
	}
	return 1;
#else
	return 0;
#endif
}

/* see if we have run out of precision. either extend float format or 
 * (if CLN isn't available) warn user 
 */
bool
fractal::check_precision()
{
	// assume image < 1024 pixels wide
	d delta = (params[SIZE])/D_LIKE(1024.0,params[SIZE]);

	debug_precision(params[SIZE],"check precision");

#ifdef HAVE_CLN
	if (delta < float_epsilon(cl_float_format(params[SIZE]))*D_LIKE(10.0,params[SIZE])) { 
		g_print("increasing precision from %d\n",float_digits(delta)); 
		// float_digits gives bits of precision,
		// cl_float takes decimal digits. / by 3 should be safe?
		set_precision(float_digits(delta)/3 +4);
		return false;
	}
#else
	if ( delta < 1.0e-15)
	{
		gtk_widget_show(gnome_warning_dialog(_("Sorry, max precision was reached, the image will become horrible !")));
		return false;
	}	
#endif

	return true;
}

bool 
fractal::set_param(param_t pnum, const char *val)
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

void
fractal::update_matrix()
{
	debug_precision(params[XYANGLE],"xyangle");
	d one = D_LIKE(1.0,params[SIZE]);
	d zero = D_LIKE(0.0, params[SIZE]);
	dmat4 id = identity3D<d>(params[SIZE],zero);

	debug_precision(id[VX][VY],"id 1");

	rot =  id * 
		rotXY<d>(params[XYANGLE],one,zero) *
		rotXZ<d>(params[XZANGLE],one,zero) * 
		rotXW<d>(params[XWANGLE],one,zero) *
		rotYZ<d>(params[YZANGLE],one,zero) *
		rotYW<d>(params[YWANGLE],one,zero) *
		rotZW<d>(params[ZWANGLE],one,zero);

	debug_precision(rot[VX][VY],"id 3");
}

dvec4 
fractal::get_center()
{
	return dvec4(params[XCENTER],params[YCENTER],
		     params[ZCENTER],params[WCENTER]);
}

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

	update_matrix();
	deltax=rot[VX];
	deltay=rot[VY];

	debug_precision(deltax[VX],"relocate:deltax");
	recenter(dx *deltax + dy *deltay);

	debug_precision(params[SIZE],"relocate 1");

	params[SIZE] /= D_LIKE(zoom,params[SIZE]);

	debug_precision(params[SIZE],"relocate 2");

	check_precision();
}	

void
fractal::flip2julia(double x, double y)
{
	relocate(x,y,1.0);
	
	params[XZANGLE] += D_LIKE(rot_by,params[SIZE]);
	params[YWANGLE] += D_LIKE(rot_by,params[SIZE]);

	rot_by = -rot_by;
}

class fract_rot {
public:
	Gf4dFractal *gf;
	dmat4 rot;
	dvec4 deltax, deltay;
	dvec4 delta_aa_x, delta_aa_y;
	dvec4 topleft;
	dvec4 aa_topleft; // topleft - offset to 1st subpixel to draw
	int depth;
	d ddepth;
	// n pixels correctly classified that would be wrong if we halved iterations
	int nhalfiters;
        // n pixels misclassified that would be correct if we doubled the iterations
	int ndoubleiters; 
	int k;	
	int last_update_y;
	fractal_t *f;
	fractFunc pf;
	int *p;
	image *im;
	std::queue<soidata_t> soi_queue;
	fract_rot(fractal_t *_f, image *_im, fractFunc _pf, Gf4dFractal *_gf) {
		gf = _gf;
		im = _im;
		f = _f; pf = _pf;
		depth = f->aa_profondeur ? f->aa_profondeur : 1; 

		f->update_matrix();
		rot = f->rot/D_LIKE(im->Xres,f->params[SIZE]);
		deltax = rot[VX];
		deltay = rot[VY];
		ddepth = D_LIKE((double)(depth*2),f->params[SIZE]);
		delta_aa_x = deltax / ddepth;
		delta_aa_y = deltay / ddepth;

		debug_precision(deltax[VX],"deltax");
		debug_precision(f->params[XCENTER],"center");
		topleft = f->get_center() -
			deltax * D_LIKE(im->Xres / 2.0, f->params[SIZE])  -
			deltay * D_LIKE(im->Yres / 2.0, f->params[SIZE]);

		d depthby2 = ddepth/D_LIKE(2.0,ddepth);
		aa_topleft = topleft - (delta_aa_y + delta_aa_x) * depthby2;

		debug_precision(topleft[VX],"topleft");
		nhalfiters = ndoubleiters = k = 0;
		p = im->iter_buf;
		for(int i = 0; i < im->Xres * im->Yres; i++) {
			p[i]=-1;
		}
		last_update_y = 0;
	};
	~fract_rot() {
		
	}
	void pixel(int x, int y, int h, int w);
	void check_update(int i);
	void rectangle(struct rgb pixel, int x, int y, int w, int h);
	void fourpixel(int x, int y);
	struct rgb antialias(const dvec4& pos);
	bool updateiters();
	void draw(int rsize);
	void soi();
	void draw_aa();
	void pixel_aa(int x, int y);
	inline int RGB2INT(int y, int x);
	void scan_rect(soidata_t& s);
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
	scratch_space scratch;

	dvec4 topleft = cpos;
		
	for(i=0;i<depth;i++) {
		dvec4 pos = topleft; 
		for(j=0;j<depth;j++) {
			colorizer *cf = f->cizer;
			int p = (pf(pos, f->params[BAILOUT], scratch, f->nbit_max)); 
			ptmp = (*cf)(p,scratch,f->potential);
			pixel_r_val += ptmp.r;
			pixel_g_val += ptmp.g;
			pixel_b_val += ptmp.b;
			pos+=delta_aa_x;
		}
		topleft += delta_aa_y;
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

	dvec4 pos = topleft + I2D_LIKE(x, f->params[SIZE]) * deltax + 
		              I2D_LIKE(y, f->params[SIZE]) * deltay;

	struct rgb pixel;
	scratch_space scratch;

	//debug_precision(pos[VX],"pixel");
	if(*ppos != -1) return;
		
	*ppos = pf(pos, f->params[BAILOUT], scratch, f->nbit_max); 
	colorizer *cf = f->cizer;
	pixel=(*cf)(*ppos, scratch, f->potential);

	rectangle(pixel,x,y,w,h);
	
	// test for iteration depth
	int i=0;
	if(f->auto_deepen && k++ % 30 == 0)
	{
		i = pf(pos,f->params[BAILOUT], scratch, f->nbit_max*2);
		if( (i > f->nbit_max/2) && (i < f->nbit_max))
		{
			/* we would have got this wrong if we used 
			 * half as many iterations */
			nhalfiters++;
		}
		else if( (i > f->nbit_max) && (i < f->nbit_max*2))
		{
			/* we would have got this right if we used
			 * twice as many iterations */
			ndoubleiters++;
		}
	}
};

inline void
fract_rot::pixel_aa(int x, int y)
{
	dvec4 pos = aa_topleft + I2D_LIKE(x, f->params[SIZE]) * deltax + 
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

inline int fract_rot::RGB2INT(int y, int x)
{
	char *p = im->buffer + (y*im->Xres + x)*3;
	int ret = *p++ << 16;
	ret |= *p++ << 8;
	ret |= *p;
	return ret;
}


void
fract_rot::scan_rect(soidata_t& s)
{
	int w = s.x2 - s.x1;
	int h = s.y2 - s.y1;

	colorizer_t *cf = f->cizer;

	for(int y = 0; y < h ; ++y)
	{
		for(int x = 0; x < w; ++x)
		{			
			scratch_space scratch;
			s.interp_both(scratch,(double)x/w,(double)y/h);
			int iter = s.iter;
			do
			{
				mandelbrot_iter(scratch);
				if(iter++ >= f->nbit_max) {
					iter=-1; break;
				}
				mag_bailout(scratch,HAS_X2 | HAS_Y2);
			}while(scratch[EJECT_VAL] < 4.0);
			
			rgb_t pixel = (*cf)(iter,scratch,0);
			rectangle(pixel,s.x1+x,s.y1+y,1,1);		       
		} 
	}
	gf4d_fractal_image_changed(gf,s.x1,s.y1,s.x2,s.y2);
}

void fract_rot::soi()
{
	/* create first chunk of data, describing whole screen */
	soidata_t soi_init(0,0,im->Xres,im->Yres,0,topleft,deltax,deltay);
	soi_queue.push(soi_init);

	/* insert into queue */
	
	do
	{
		soidata_t s = soi_queue.front();
		/* remove element */
		soi_queue.pop();
		
		/* if too small, draw by scanning */
		if(s.x2 - s.x1 < 8) 
		{
			scan_rect(s);
			continue;
		}
		int old_iter = s.iter;
		/* iterate until it splits or maxiter */
		do {
			s.iterate();
			if(s.iter >= f->nbit_max) 
			{
				/* draw black box */
				break;
			}
		}while(! s.needs_split());

		colorizer_t *cf = f->cizer;

		// this rect is entirely within the set
		if(s.iter >= f->nbit_max)
		{
			rgb_t pixel = (*cf)(-1,s.data[0],0);
			/* draw interior rect */
			rectangle(pixel,s.x1,s.y1,s.x2-s.x1,s.y2-s.y1);
			gf4d_fractal_image_changed(gf,s.x1,s.y1,s.x2,s.y2);
		}
		else
		{
			// undo the last iteration, which broke tolerance
			s.revert(); 
			
			//printf("progress: %d\n",s.iter - old_iter);
			rgb_t pixel = (*cf)(s.iter,s.data[0],0);
			
			/* draw with split number of iterations */
			rectangle(pixel,s.x1,s.y1,s.x2-s.x1,s.y2-s.y1);
			gf4d_fractal_image_changed(gf,s.x1,s.y1,s.x2,s.y2);
			
			/* create 4 new rectangles & add to front of queue */
			soi_queue.push(s.topleft());
			soi_queue.push(s.topright());
			soi_queue.push(s.botleft());
			soi_queue.push(s.botright());			
		}
	}while(!(soi_queue.empty()));

	gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DONE);
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
			/* need to do comparison in both iteration space
			 * and (if potential is on) color space */
			int piter = im->iter_buf[y * w + x];
			if(piter == im->iter_buf[y * w + x + 4] &&
			   piter == im->iter_buf[(y+4) * w + x] &&
			   piter == im->iter_buf[(y+4) * w + x + 4])
			{
				if(f->potential)
				{
					int pcol = RGB2INT(y,x);
					if(pcol == RGB2INT(y,x+4) &&
					   pcol == RGB2INT(y+4,x) &&
					   pcol == RGB2INT(y+4,x+4)) {
						
						continue;
					}
				}
				else
				{
					continue;
				}
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
	fractFunc pf= fractFuncTable[fractal_type];
	fract_rot pr(this, im, pf,gf);

	gf4d_fractal_status_changed(gf,GF4D_FRACTAL_CALCULATING);

	//pr.soi();
	//return;
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
	
	gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DONE);
	gf4d_fractal_progress_changed(gf,0.0);
}


