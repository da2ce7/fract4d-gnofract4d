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

#ifndef _FRACTFUNC_H_
#define _FRACTFUNC_H_

#include "image_public.h"
#include "pointFunc_public.h"
#include "fractWorker_public.h"
#include "vectors.h"
#include "fract_public.h"

typedef double d;
typedef vec4<d> dvec4;
typedef mat4<d> dmat4;



/* this contains stuff which is useful for drawing the fractal,
   but can be recalculated at will, so isn't part of the fractal's
   persistent state. We create a new one each time we start drawing. This one
   parcels up the work which is actually performed by the fractThreadFuncs
 */


class fractFunc {
 public:
    fractFunc(
	d *params,
	int eaa,
	int maxiter,
	int nThreads_,
	bool auto_deepen,
	IFractWorker *fw,
	IImage *_im, 
	IFractalSite *_site);
    ~fractFunc();
   
    void draw_all();
    void draw(int rsize, int drawsize);    
    void draw_aa();
    int updateiters();

    friend class STFractWorker;

    // callback wrappers
    inline void iters_changed(int iters)
	{
	    site->iters_changed(iters);
	}
    inline void image_changed(int x1, int x2, int y1, int y2)
	{
	    site->image_changed(x1,x2,y1,y2);
	}
    inline void progress_changed(float progress)
	{
	    site->progress_changed(progress);
	}
    inline void status_changed(int status_val)
	{
	    site->status_changed(status_val);
	}
    inline bool try_finished_cond()
	{
	    return site->is_interrupted();
	}

 private:
    // MEMBER VARS

    bool ok; // did this instance get constructed ok?
    // (* this should really be done with exns but they are unreliable 
    //  * in the presence of pthreads - grrr *)

    // do every nth pixel twice as deep as the others to
    // see if we need to auto-deepen
    enum { AUTO_DEEPEN_FREQUENCY = 30 };

    // used for calculating (x,y,z,w) pixel coords
    dmat4 rot; // scaled rotation matrix
    dvec4 deltax, deltay; // step from 1 pixel to the next in x,y directions
    dvec4 delta_aa_x, delta_aa_y; // offset between subpixels
    dvec4 topleft; // top left corner of screen
    dvec4 aa_topleft; // topleft - offset to 1st subpixel to draw
    d ddepth;     

    // params from ctor
    int depth;    
    int eaa;
    int maxiter;
    int nThreads;
    bool auto_deepen;
    d *params;

    IImage *im;    
    IFractWorker *worker;
    // for callbacks
    IFractalSite *site;

    // auto-deepening support

    // n pixels correctly classified that would be wrong 
    // if we halved iterations
    int nTotalHalfIters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int nTotalDoubleIters; 
    int nTotalK;	// number of pixels calculated    

    // last time we redrew the image to this line
    int last_update_y; 

    // private drawing methods
    void send_quit();

    // redraw the image to this line
    // also checks for interruptions & returns true if we should stop
    bool update_image(int i);

    // clear auto-deepen and last_update
    void reset_counts();
    void reset_progress(float progress);


    // calculate the whole image using worker threads
    void draw_threads(int rsize, int drawsize);

    // reset image
    void clear();
};


dmat4 rotated_matrix(double *params);

#ifdef __cplusplus
extern "C" {
#endif

extern void calc(	
    d *params,
    int eaa,
    int maxiter,
    int nThreads_,
    pf_obj *pfo, 
    cmap_t *cmap, 
    bool auto_deepen,
    IImage *im, 
    IFractalSite *site);

#ifdef __cplusplus
}
#endif

#endif /* _FRACTFUNC_H_ */