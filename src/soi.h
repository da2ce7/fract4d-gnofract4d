#ifndef _SOI_H_
#define _SOI_H_

#include "calc.h"
#include "test-fonction.h"

#define S_X 0
#define S_Y 1
#define S_CX 2
#define S_CY 3

// 9 corner points, 4 test points
#define N_DATA (9+4)

#define NW 0
#define N 1
#define NE 2
#define W 3
#define C 4
#define E 5
#define SW 6
#define S 7
#define SE 8

#define TEST_TOPLEFT 9
#define TEST_TOPRIGHT 10
#define TEST_BOTLEFT 11
#define TEST_BOTRIGHT 12

double interpolate(double x0, double x1, double x2, double t);
void soi_mandel_iter(double *p, double *squares);
bool soi_mag_bailout(double *squares, double eject_val);

/* memory usage optimization:
 * stuff that needs to be saved in the queue - we can recompute 
 * the rest easily 
 */
struct soi_save_data_t
{

};

/* describes a rectangle of 9 points & 4 test points. We apply
 * the mandelbrot iteration repeatedly until the points are no longer
 * a good approximation to a quadratic patch
 */

struct soidata_t
{
	scratch_space data[N_DATA]; 
	scratch_space last[N_DATA]; // last state for revert

	int x1, x2, y1, y2; // pixel coordinates
	static const double twidth = 0.1 / 1024.0; // should be / im->Xres
	int iter;

	// member fns
	soidata_t() {};

	soidata_t(int _x1, int _y1, int _x2, int _y2, int _iter,
		  const dvec4& topleft,
		  const dvec4& delta_x,
		  const dvec4& delta_y) {

		x1 = _x1; y1 = _y1 ; x2 = _x2 ; y2 = _y2; iter = _iter;
		for(int i = 0; i < N_DATA; i++)
		{
			data[i][X] = data[i][Y] = 0.0;
		}
		dvec4 west_dx = (double)x1 * delta_x;
		dvec4 east_dx = (double)(x2-1) *delta_x;
		dvec4 mid_dx = 0.5 * (west_dx + east_dx);
		dvec4 quarter_dx = 0.5 * mid_dx;

		dvec4 north_dy = (double)y1 * delta_y;
		dvec4 south_dy = (double)(y2-1) * delta_y;
		dvec4 mid_dy = 0.5 * (north_dy + south_dy);
		dvec4 quarter_dy = 0.5 * mid_dy;

		dvec4 t = topleft + west_dx + north_dy;
		set_c(data[NW],t);

		t = topleft + mid_dx + north_dy;
		set_c(data[N],t);

		t = topleft + east_dx + north_dy;
		set_c(data[NE],t);

	        t = topleft + west_dx + mid_dy;
		set_c(data[W],t);

		t = topleft + mid_dx + mid_dy;
		set_c(data[C],t);

		t = topleft + east_dx + mid_dy;
		set_c(data[E],t);

		t = topleft + west_dx + south_dy;
		set_c(data[SW],t);

		t = topleft + mid_dx + south_dy;
		set_c(data[S],t);

		t = topleft + east_dx + south_dy;
		set_c(data[SE],t);

		// test points
		dvec4 base_t = topleft + quarter_dx + quarter_dy;
		set_c(data[TEST_TOPLEFT],base_t);
			
		t = base_t + mid_dx;
		set_c(data[TEST_TOPRIGHT],t);

		t = base_t + mid_dy;
		set_c(data[TEST_BOTLEFT],t);

		t = base_t + mid_dx + mid_dy;
		set_c(data[TEST_BOTRIGHT],t);
	} 

	void set_c(double *dst, dvec4& src) {
		dst[CX] = src[VX];
		dst[CY] = src[VY];
	};

	void iterate() {
		for(int i = 0; i < N_DATA ; i++)
		{
			last[i] = data[i];
			mandelbrot_iter(data[i]);
		}
		++iter;
	}
	void revert() {
		for(int i = 0; i < N_DATA ; i++)
		{
			data[i] = last[i];
		}
		--iter;
	}
	bool bailout() {
		for(int i = 0; i < N_DATA; i++)
		{
			mag_bailout(data[i], HAS_X2|HAS_Y2 );
			if(data[i][EJECT_VAL] > 4.0) return true;
		}
		return false;
	}
	double interp_xy(int dim,double x, double y) {
		double y0 = interpolate(data[NW][dim],data[N][dim],data[NE][dim],x);
		double y1 = interpolate(data[W][dim], data[C][dim],data[E][dim],x);
		double y2 = interpolate(data[SW][dim],data[S][dim],data[SE][dim],x);
		return interpolate(y0,y1,y2,y);
	}
	void interp_both(double *d,double x, double y) {
		d[X] = interp_xy(X,x,y);
		d[Y] = interp_xy(Y,x,y);
		d[CX] = interp_xy(CX,x,y);
		d[CY] = interp_xy(CY,x,y);
	}

	bool compare(double a, double b) {
		// do b / a, allowing for div by zero
		double factor;
		if(a == 0.0)
		{
			if(b == 0.0)
			{
				factor = 1.0;
			}
			else
			{
				factor = 1.0e8; // ie, a big number: we nearly divide by zero
			}
		}
		else
		{
			factor = b / a;
		}
		if(fabs(1.0-factor) > twidth) return true;
		return false;
	}
	bool compare_xy(double a[2], double b[2]) {
		return compare(a[0],b[0]) || compare(a[1],b[1]);
	}
	// has interpolation broken down?
	bool interp_check() {
		// for each test point, see if it's within |tolerance|
		// of where the interpolating polynomial says it is
		double z[2];
		z[0] = interp_xy(0,0.25,0.25);
		z[1] = interp_xy(1,0.25,0.25);
		
		if(compare_xy(z,data[TEST_TOPLEFT])) return true;

		z[0] = interp_xy(0,0.75,0.25);
		z[1] = interp_xy(1,0.75,0.25);
		
		if(compare_xy(z,data[TEST_TOPRIGHT])) return true;

		z[0] = interp_xy(0,0.25,0.75);
		z[1] = interp_xy(1,0.25,0.75);
		
		if(compare_xy(z,data[TEST_BOTLEFT])) return true;

		z[0] = interp_xy(0,0.75,0.75);
		z[1] = interp_xy(1,0.75,0.75);
		
		if(compare_xy(z,data[TEST_BOTRIGHT])) return true;

		return false;
	}
	bool needs_split() {
		return bailout() || interp_check();
	}

	void interp_new_points(soidata_t& s, double xoff, double yoff) {
		/* interpolate middle of edges */
		interp_both(s.data[N],xoff + 0.25, yoff + 0.0);
		interp_both(s.data[W],xoff + 0.0,  yoff + 0.25);
		interp_both(s.data[E],xoff + 0.5,  yoff + 0.25);
		interp_both(s.data[S],xoff + 0.25, yoff + 0.5);

		/* interpolate new test points */
		interp_both(s.data[TEST_TOPLEFT], xoff + 0.125, yoff + 0.125);
		interp_both(s.data[TEST_TOPRIGHT],xoff + 0.375, yoff + 0.125);
		interp_both(s.data[TEST_BOTLEFT], xoff + 0.125, yoff + 0.375);
		interp_both(s.data[TEST_BOTRIGHT],xoff + 0.375, yoff + 0.375);
	}
	soidata_t topleft() {
		soidata_t s;
		s.x1 = x1;
		s.x2 = (x1+x2)/2;
		s.y1 = y1;
		s.y2 = (y1+y2)/2;
		s.iter = iter;

		/* corners are exact copies */
		s.data[NW] = data[NW];
		s.data[NE] = data[N];
		s.data[SW] = data[W];
		s.data[SE] = data[C];
		s.data[C]  = data[TEST_TOPLEFT];

		interp_new_points(s,0.0,0.0);
		return s;
	}
	soidata_t topright() {
		soidata_t s;
		s.x1 = (x1+x2)/2;
		s.x2 = x2;
		s.y1 = y1;
		s.y2 = (y1+y2)/2;
		s.iter = iter;

		/* corners are exact copies */
		s.data[NW] = data[N];
		s.data[NE] = data[NE];
		s.data[SW] = data[C];
		s.data[SE] = data[E];
		s.data[C]  = data[TEST_TOPRIGHT];

		interp_new_points(s,0.5,0.0);
		return s;
	}
	soidata_t botleft() {
		soidata_t s;
		s.x1 = x1;
		s.x2 = (x1+x2)/2;
		s.y1 = (y1+y2)/2;
		s.y2 = y2;
		s.iter = iter;

		/* corners are exact copies */
		s.data[NW] = data[W];
		s.data[NE] = data[C];
		s.data[SW] = data[SW];
		s.data[SE] = data[S];
		s.data[C]  = data[TEST_BOTLEFT];

		interp_new_points(s,0.0,0.5);
		return s;
	}
	soidata_t botright() {
		soidata_t s;
		s.x1 = (x1+x2)/2;
		s.x2 = x2;
		s.y1 = (y1+y2)/2;
		s.y2 = y2;
		s.iter = iter;

		/* corners are exact copies */
		s.data[NW] = data[C];
		s.data[NE] = data[E];
		s.data[SW] = data[S];
		s.data[SE] = data[SE];
		s.data[C]  = data[TEST_BOTRIGHT];

		interp_new_points(s,0.5,0.5);
		return s;
	}
	
};


#endif /* _SOI_H_ */
