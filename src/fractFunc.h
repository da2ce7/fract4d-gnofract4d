/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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

// opaque declaration: must be some way of removing this nasty ifdef!
#ifdef _WIN32
class Gf4dFractal;
#else
typedef struct _Gf4dFractal Gf4dFractal;
#endif

#include "fract_callbacks.h"
#include "fract.h"
#include "image.h"
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

/* bootstrap info for worker threads */
typedef struct {
    fractFunc *ff;
    job_type_t job;
    int x, y, param;
} thread_data_t;

/* this contains stuff which is useful for drawing the fractal,
   but can be recalculated at will, so isn't part of the fractal's
   persistent state. We create a new one each time we start drawing */

class fractFunc {
 public:
    fractFunc(fractal_t *_f, image *_im, Gf4dFractal *_gf);
    ~fractFunc();
   
    void draw(int rsize, int drawsize);    
    void draw_aa();
    int updateiters();

    // top-level function for multi-threaded workers
    void work(thread_data_t *jobdata);

 private:
    // MEMBER VARS

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
    int nhalfiters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int ndoubleiters; 
    // last time we redrew the image to this line
    int last_update_y; 
    int k;	// number of pixels calculated    

    fractal_t *f; // pointer to fract passed in to ctor
    image *im;    // pointer to image passed in to ctor
    pointFunc *pf; // function for calculating 1 point

    tpool<thread_data_t> *ptp;

    /* wait for a ready thread then give it some work */
    void send_cmd(job_type_t job, int x, int y, int param);
    void send_quit();

    // MEMBER FUNCTIONS
    
    // calculate a single pixel
    void pixel(int x, int y, int h, int w);
    // calculate a single pixel in aa-mode
    void pixel_aa(int x, int y);

    // calculate an 8-by-8 box of pixels...
    void box(int x, int y, int rsize);
    // ... in a worker thread
    void send_box(int x, int y, int rsize);

    // calculate a row of pixels...
    void row(int x, int y, int n);
    // ... in a worker thread
    void send_row(int x, int y, int n);

    // calculate a row of antialiased pixels
    void row_aa(int x, int y, int n);
    // ... in a worker thread
    void send_row_aa(int x, int y, int n);

    // calculate a row of boxes
    void box_row(int w, int y, int rsize);

    // ... in a worker thread
    void send_box_row(int w, int y, int rsize);

    // redraw the image to this line
    // also checks for interruptions & returns true if we should stop
    bool update_image(int i);

    // clear auto-deepen and last_update
    void reset_counts();
    void reset_progress(float progress);

    // draw a rectangle of this colour
    void rectangle(struct rgb pixel, int x, int y, int w, int h);

    // calculate this point using antialiasing
    struct rgb antialias(int x, int y);

    // calculate the whole image using worker threads
    void draw_threads(int rsize, int drawsize);

    // reset image
    void clear();

    // make an int corresponding to an RGB triple
    inline int RGB2INT(int y, int x);

    // does the point at (x,y) have the same colour & iteration count
    // as the target?
    inline bool isTheSame(bool bFlat, int targetIter, int targetCol, int x, int y);

};

#endif /* _FRACTFUNC_H_ */
