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

#include "fract_callbacks.h"
#include "fract.h"
#include "image.h"
#include "pointFunc.h"
#include "colorizer.h"
#include "threadpool.h"

/* enum for jobs */
typedef enum {
    JOB_NONE,
    JOB_BOX,
    JOB_BOX_ROW,
    JOB_ROW,
    JOB_ROW_AA
} job_type_t;

/* one unit of work */
typedef struct {
    job_type_t job;
    int x, y, param;
} job_info_t;

/* per-worker-thread fractal info */
class fractThreadFunc {
 public:
    fractFunc *ff;

    /* pointers to data also held in fractFunc */
    fractal_t *f; 
    image *im;    

    /* not a ctor because we always create a whole array then init them */
    bool init(fractFunc *ff, fractal_t *f, image *im);

    ~fractThreadFunc();

    // function object which calculates the colors of points 
    // this is per-thread-func so it doesn't have to be re-entrant
    // and can have member vars
    pointFunc *pf; 

    // n pixels correctly classified that would be wrong 
    // if we halved iterations
    int nhalfiters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int ndoubleiters; 
    int k;	// number of pixels calculated    
    int lastIter; // how many iterations did last pixel take?


    fractThreadFunc() {
        nhalfiters = ndoubleiters = k = 0;
        lastIter = 0;
    }
    // try that many without periodicity checking if it did bail out,
    // if it didn't bail, start periodicity checking immediately
    inline int periodGuess();

    // period guesser for when we have the last count to hand (as for antialias pass)
    inline int periodGuess(int last);

    // update whether last pixel bailed
    inline void periodSet(int *ppos);

    // top-level function for multi-threaded workers
    void work(job_info_t &tdata);

    // calculate a row of antialiased pixels
    void row_aa(int x, int y, int n);

    // calculate a row of pixels
    void row(int x, int y, int n);

    // calculate an rsize-by-rsize box of pixels
    void box(int x, int y, int rsize);

    // does the point at (x,y) have the same colour & iteration count
    // as the target?
    inline bool isTheSame(bool bFlat, int targetIter, int targetCol, int x, int y);

    // make an int corresponding to an RGB triple
    inline int RGB2INT(int y, int x);

    // calculate a row of boxes
    void box_row(int w, int y, int rsize);

    // calculate a single pixel
    void pixel(int x, int y, int h, int w);
    // calculate a single pixel in aa-mode
    void pixel_aa(int x, int y);

    // draw a rectangle of this colour
    void rectangle(struct rgb pixel, int x, int y, int w, int h);
    void rectangle_with_iter(struct rgb pixel, int iter, int x, int y, int w, int h);

    // calculate this point using antialiasing
    struct rgb antialias(int x, int y);

    void reset_counts();

};

/* this contains stuff which is useful for drawing the fractal,
   but can be recalculated at will, so isn't part of the fractal's
   persistent state. We create a new one each time we start drawing. This one
   parcels up the work which is actually performed by the fractThreadFuncs
 */

class fractFunc {
 public:
    fractFunc(
	fractal_t *_f, 
	image *_im, 
	Gf4dFractal *_gf,
	fract_callbacks *fcb);
    ~fractFunc();
   
    void draw_all();
    void draw(int rsize, int drawsize);    
    void draw_aa();
    int updateiters();

    friend class fractThreadFunc;
    friend class fractal;

    // callback wrappers
    inline void parameters_changed()
	{
	    if(fcb->parameters_changed) fcb->parameters_changed(gf);
	}
    inline void image_changed(int x1, int x2, int y1, int y2)
	{
	    if(fcb->image_changed) fcb->image_changed(gf,x1,x2,y1,y2);
	}
    inline void progress_changed(float progress)
	{
	    if(fcb->progress_changed) fcb->progress_changed(gf,progress);
	}
    inline void status_changed(int status_val)
	{
	    if(fcb->status_changed) fcb->status_changed(gf,status_val);
	}
    inline bool try_finished_cond()
	{
	    if(fcb->try_finished_cond) return fcb->try_finished_cond(gf);
	    return false; // if no callback, we can't be interrupted
	}

 private:
    // MEMBER VARS

    bool ok; // did this instance get constructed ok?
    // (* this should really be done with exns but they are unreliable 
    //  * in the presence of pthreads - grrr *)

    // do every nth pixel twice as deep as the others to
    // see if we need to auto-deepen
    enum { AUTO_DEEPEN_FREQUENCY = 30 };

    // for callbacks
    Gf4dFractal *gf;

    dmat4 rot; // scaled rotation matrix
    dvec4 deltax, deltay; // step from 1 pixel to the next in x,y directions
    dvec4 delta_aa_x, delta_aa_y; // offset between subpixels
    dvec4 topleft; // top left corner of screen
    dvec4 aa_topleft; // topleft - offset to 1st subpixel to draw

    int depth;    // antialias depth
    d ddepth;     // double version of antialias depth

    // n pixels correctly classified that would be wrong 
    // if we halved iterations
    int nTotalHalfIters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int nTotalDoubleIters; 
    int nTotalK;	// number of pixels calculated    

    // last time we redrew the image to this line
    int last_update_y; 


    fractal_t *f; // pointer to fract passed in to ctor
    image *im;    // pointer to image passed in to ctor
    fract_callbacks *fcb; // callbacks for reporting progress
    pointFunc *pf; // function for calculating 1 point

    int nThreadFuncs;
    fractThreadFunc *ptf;
    tpool<job_info_t,fractThreadFunc> *ptp;


    /* wait for a ready thread then give it some work */
    void send_cmd(job_type_t job, int x, int y, int param);
    void send_quit();

    // MEMBER FUNCTIONS

    void send_box(int x, int y, int rsize);
    void send_row(int x, int y, int n);
    void send_row_aa(int x, int y, int n);
    // ... in a worker thread
    void send_box_row(int w, int y, int rsize);

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

#endif /* _FRACTFUNC_H_ */
