#include "fractFunc.h"
#include "pointFunc.h"
#include "iterFunc.h"
#include <stdio.h>

/* redirect back to a member function */
void worker(thread_data_t &tdata)
{
    tdata.ff->work(&tdata);
}

fractFunc::fractFunc(fractal_t *_f, image *_im, Gf4dFractal *_gf)
{
    gf = _gf;
    im = _im;
    f = _f; 
    pf = pointFunc_new(
        f->pIterFunc, 
        f->bailout_type, 
        f->params[BAILOUT], 
        f->cizer, 
        f->colorFuncs[OUTER],
        f->colorFuncs[INNER]);
    
    depth = f->eaa ? 2 : 1; 
    
    f->update_matrix();
    rot = f->rot/D_LIKE(im->Xres(),f->params[MAGNITUDE]);
    deltax = rot[VX];
    deltay = rot[VY];
    ddepth = D_LIKE((double)(depth*2),f->params[MAGNITUDE]);
    delta_aa_x = deltax / ddepth;
    delta_aa_y = deltay / ddepth;
    
    debug_precision(deltax[VX],"deltax");
    debug_precision(f->params[XCENTER],"center");
    topleft = f->get_center() -
        deltax * D_LIKE(im->Xres() / 2.0, f->params[MAGNITUDE])  -
        deltay * D_LIKE(im->Yres() / 2.0, f->params[MAGNITUDE]);

    d depthby2 = ddepth/D_LIKE(2.0,ddepth);
    aa_topleft = topleft - (delta_aa_y + delta_aa_x) * depthby2;
    
    debug_precision(topleft[VX],"topleft");
    nhalfiters = ndoubleiters = k = 0;
    lastIter = 0;
    clear();

    /* threading */
    if(f->nThreads > 1)
    {
        ptp = new tpool<thread_data_t>(2,100);
    }
    else
    {
        ptp = NULL;
    }
    last_update_y = 0;
};

fractFunc::~fractFunc()
{
    delete ptp;
}

void 
fractFunc::clear()
{
    im->clear();    
}

/* we're in a worker thread */
void
fractFunc::work(thread_data_t *jobdata)
{
    int nRows=0;

    if(gf4d_fractal_try_finished_cond(gf))
    {
        // interrupted - just return without doing anything
        // this is less efficient than clearing the queue but easier
        return;
    }

    /* carry them out */
    switch(jobdata->job)
    {
    case JOB_BOX:
        //cout << "BOX " << jobdata->y << " " << pthread_self() << "\n";
        box(jobdata->x,jobdata->y,jobdata->param);
        nRows = jobdata->param;
        break;
    case JOB_ROW:
        //cout << "ROW " << jobdata->y << " " << pthread_self() << "\n";
        row(jobdata->x,jobdata->y,jobdata->param);
        nRows=1;
        break;
    case JOB_BOX_ROW:
        //cout << "BXR " << jobdata->y << " " << pthread_self() << "\n";
        box_row(jobdata->x, jobdata->y, jobdata->param);
        nRows = jobdata->param;
        break;
    case JOB_ROW_AA:
        //cout << "RAA " << jobdata->y << " " << pthread_self() << "\n";
        row_aa(jobdata->x,jobdata->y,jobdata->param);
        nRows=1;
        break;
    default:
        printf("Unknown job id %d ignored\n", (int) jobdata->job);
    }
    gf4d_fractal_image_changed(gf,0,jobdata->y,im->Xres(),jobdata->y+ nRows);
    gf4d_fractal_progress_changed(gf,(float)jobdata->y/(float)im->Yres());
}

void
fractFunc::send_cmd(job_type_t job, int x, int y, int param)
{
    //gf4d_fractal_try_finished_cond(gf);
    thread_data_t work;

    work.job = job; work.ff = this;
    work.x = x; work.y = y; work.param = param;

    ptp->add_work(worker, work);
}

void
fractFunc::send_row(int x, int y, int w)
{
    //cout << "sent ROW" << y << "\n";
    send_cmd(JOB_ROW,x,y,w);
}

void
fractFunc::send_box_row(int w, int y, int rsize)
{
    //cout << "sent BXR" << y << "\n";
    send_cmd(JOB_BOX_ROW, w, y, rsize);
}

void
fractFunc::send_box(int x, int y, int rsize)
{
    //cout << "sent BOX" << y << "\n";
    send_cmd(JOB_BOX,x,y,rsize);
}

void
fractFunc::send_row_aa(int x, int y, int w)
{
    //cout << "sent RAA" << y << "\n";
    send_cmd(JOB_ROW_AA, x, y, w);
}

inline void
fractFunc::rectangle(struct rgb pixel, int x, int y, int w, int h)
{
    for(int i = y ; i < y+h; i++)
    {
        for(int j = x; j < x+w; j++) {
            im->put(j,i,pixel);
        }
    }
}

rgb_t
fractFunc::antialias(int x, int y)
{
    dvec4 topleft = aa_topleft + I2D_LIKE(x, f->params[MAGNITUDE]) * deltax + 
        I2D_LIKE(y, f->params[MAGNITUDE]) * deltay;

    dvec4 pos = topleft; 

    struct rgb ptmp;
    unsigned int pixel_r_val=0, pixel_g_val=0, pixel_b_val=0;    
    int p=0;

    int single_iters = im->getIter(x,y);
    int nNoPeriodIters = periodGuess(single_iters); 
    
    // top left
    (*pf)(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;
    pos+=delta_aa_x;

    // top right
    (*pf)(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;
    pos = topleft + delta_aa_y;

    // bottom left
    (*pf)(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;
    pos+=delta_aa_x;

    // bottom right
    (*pf)(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;

    ptmp.r = pixel_r_val / 4;
    ptmp.g = pixel_g_val / 4;
    ptmp.b = pixel_b_val / 4;
    return ptmp;
}


inline void 
fractFunc::pixel(int x, int y,int w, int h)
{
    int *ppos = im->iter_buf + y*im->Xres() + x;
    struct rgb pixel;

    if(*ppos != -1) return;

    // calculate coords of this point
    dvec4 pos = topleft + 
        I2D_LIKE(x, f->params[MAGNITUDE]) * deltax + 
        I2D_LIKE(y, f->params[MAGNITUDE]) * deltay;
		
    (*pf)(pos, f->maxiter,periodGuess(), &pixel,ppos); 
    periodSet(ppos);

    // test for iteration depth
    if(f->auto_deepen && k++ % AUTO_DEEPEN_FREQUENCY == 0)
    {
        int i=0;

        (*pf)(pos, f->maxiter*2,periodGuess()*2,NULL,&i);

        if( (i > f->maxiter/2) && (i < f->maxiter))
        {
            /* we would have got this wrong if we used 
             * half as many iterations */
            nhalfiters++;
        }
        else if( (i > f->maxiter) && (i < f->maxiter*2))
        {
            /* we would have got this right if we used
             * twice as many iterations */
            ndoubleiters++;
        }
    }

    rectangle(pixel,x,y,w,h);
}

inline void
fractFunc::pixel_aa(int x, int y)
{
    struct rgb pixel;

    int iter = im->getIter(x,y);
    // if aa type is fast, short-circuit some points
    if(f->eaa == AA_FAST &&
       x > 0 && x < im->Xres()-1 && y > 0 && y < im->Yres()-1)
    {
        // check to see if this point is surrounded by others of the same colour
        // if so, don't bother recalculating
        int pcol = RGB2INT(y,x);
        bool bFlat = true;

        // this could go a lot faster if we cached some of this info
        bFlat = isTheSame(bFlat,iter,pcol,x-1,y-1);
        bFlat = isTheSame(bFlat,iter,pcol,x,y-1);
        bFlat = isTheSame(bFlat,iter,pcol,x+1,y-1);
        bFlat = isTheSame(bFlat,iter,pcol,x-1,y);
        bFlat = isTheSame(bFlat,iter,pcol,x+1,y);
        bFlat = isTheSame(bFlat,iter,pcol,x-1,y+1);
        bFlat = isTheSame(bFlat,iter,pcol,x,y+1);
        bFlat = isTheSame(bFlat,iter,pcol,x+1,y+1);
        if(bFlat) 
        {
            return;
        }
    }
    pixel = antialias(x,y);

    rectangle(pixel,x,y,1,1);
}

inline void
fractFunc::row(int x, int y, int n)
{
    for(int i = 0; i < n; ++i)
    {
        pixel(x+i,y,1,1);
    }
}

bool
fractFunc::update_image(int i)
{
    gf4d_fractal_image_changed(gf,0,last_update_y,im->Xres(),i);
    gf4d_fractal_progress_changed(gf,(float)i/(float)im->Yres());
    last_update_y = i;
    return gf4d_fractal_try_finished_cond(gf);
}

// see if the image needs more (or less) iterations to display
// properly returns +ve if more are required, -ve if less are
// required, 0 if it's correct. This is a very poor heuristic - a
// histogram approach would be better

int
fractFunc::updateiters()
{
    double doublepercent = ((double)ndoubleiters*AUTO_DEEPEN_FREQUENCY*100)/k;
    double halfpercent = ((double)nhalfiters*AUTO_DEEPEN_FREQUENCY*100)/k;
		
    if(doublepercent > 1.0) 
    {
        // more than 1% of pixels are the wrong colour! 
        // quelle horreur!
        return 1;
    }

    if(doublepercent == 0.0 && halfpercent < 0.5 && 
       f->maxiter > 32)
    {
        // less than .5% would be wrong if we used half as many iters
        // therefore we are working too hard!
        return -1;
    }
    return 0;
}

void fractFunc::draw_aa()
{
    int w = im->Xres();
    int h = im->Yres();

    reset_counts();

    reset_progress(0.0);

    for(int y = 0; y < h ; y++) {
        if(f->nThreads > 1)
        {
            send_row_aa(0,y,w);
        }
        else
        {
            row_aa(0,y,w);
            if(update_image(y))
            {
                break;
            }
        }
    }

    reset_progress(1.0);
}

inline int fractFunc::RGB2INT(int y, int x)
{
    rgb_t pixel = im->get(x,y);
	int ret = (pixel.r << 16) | (pixel.g << 8) | pixel.b;
    return ret;
}

inline bool fractFunc::isTheSame(
    bool bFlat, int targetIter, int targetCol, int x, int y)
{
    if(bFlat)
    {
        // does this point have the target # of iterations?
        if(im->getIter(x,y) != targetIter) return false;
        // does it have the same colour too?
        if(RGB2INT(y,x) != targetCol) return false;
    }
    return bFlat;
}

void fractFunc::reset_counts()
{
    last_update_y=0;
    ndoubleiters=0;
    nhalfiters=0;
}

void fractFunc::reset_progress(float progress)
{
    if(ptp)
    {
        ptp->flush();
    }
    gf4d_fractal_image_changed(gf,0,0,im->Xres(),im->Yres());
    gf4d_fractal_progress_changed(gf,progress);
}

void fractFunc::box(int x, int y, int rsize)
{
    // calculate edges of box to see if they're all the same colour
    // if they are, we assume that the box is a solid colour and
    // don't calculate the interior points
    bool bFlat = true;
    int iter = im->getIter(x,y);
    int pcol = RGB2INT(y,x);
    
    // check top and bottom of box for flatness
    for(int x2 = x+1; x2 <= x + rsize; ++x2)
    {
        bFlat = isTheSame(bFlat,iter,pcol,x2,y);
        bFlat = isTheSame(bFlat,iter,pcol,x2,y+rsize);
    }
    // calc left of next box over & check for flatness
    for(int y2 = y+1; y2 <= y + rsize; ++y2)
    {
        bFlat = isTheSame(bFlat, iter, pcol, x, y2);
        pixel(x+rsize,y2,1,1);
        bFlat = isTheSame(bFlat,iter,pcol,x+rsize,y2);
    }
    
    if(bFlat)
    {
        // just draw a solid rectangle
        struct rgb pixel = im->get(x,y);
        rectangle(pixel,x+1,y+1,rsize-1,rsize-1);
    }
    else
    {
        // we do need to calculate the interior 
        // points individually
        for(int y2 = y + 1 ; y2 < y + rsize; ++y2)
        {
            row(x+1,y2,rsize-1);
        }		
    }		
}

void fractFunc::draw(int rsize, int drawsize)
{
    if(f->nThreads > 1)
    {
        draw_threads(rsize, drawsize);
        return;
    }

    int x,y;
    int w = im->Xres();
    int h = im->Yres();

    /* reset progress indicator & clear screen */
    reset_counts();

    reset_progress(0.0);

    // first pass - big blocks and edges
    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        // main large blocks 
        for ( x = 0 ; x< w - rsize ; x += rsize) 
        {
            pixel ( x, y, drawsize, drawsize);
        }
        // extra pixels at end of lines
        for(int y2 = y; y2 < y + rsize; ++y2)
        {
            row (x, y2, w-x);
        }
        if(update_image(y)) 
        {
            goto done;
        }
    }
    // remaining lines
    for ( ; y < h ; y++)
    {
        row(0,y,w);
        if(update_image(y)) 
        {
            goto done;
        }
    }

    reset_counts();

    // second pass - fill in the remaining pixels

    // calculate tops of next row down
    for ( y = 0; y < h - rsize; y += rsize) {        
        for(x = 0; x < w - rsize ; x += rsize) {
            for(int x2 = x+1; x2 < x + rsize; ++x2)
            {
                pixel(x2,y,1,1);
            }
        }        
        if(update_image(y))
        {
            goto done;
        }
    }

    reset_counts();

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) {
        if(update_image(y))
        {
            goto done;
        }

        // calculate left edge of the row
        for(int y2 = y+1; y2 < y + rsize; ++y2)
        {
            pixel(0,y2,1,1);
        }

        for(x = 0; x < w - rsize ; x += rsize) {
            box(x,y,rsize);
        }		
    }

 done:
    /* refresh entire image & reset progress bar */
    reset_progress(1.0);
}

void fractFunc::draw_threads(int rsize, int drawsize)
{
    int x,y;
    int w = im->Xres();
    int h = im->Yres();

    reset_counts();
    reset_progress(0.0);

    // first pass - big blocks and edges
    // do this in current thread - it's fast anyway
    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        // main large blocks 
        for ( x = 0 ; x< w - rsize ; x += rsize) 
        {
            pixel ( x, y, drawsize, drawsize);
        }
        // extra pixels at end of lines
        for(int y2 = y; y2 < y + rsize; ++y2)
        {
            row (x, y2, w-x);
        }
        update_image(y);
    }

    // remaining lines
    for ( y = h > rsize ? h - rsize : 0 ; y < h ; y++)
    {
        send_row(0,y,w);
        update_image(y);
    }

    reset_progress(0.0);
    reset_counts();

    // second pass - fill in the remaining pixels
    
    // calculate tops of boxes for future cross-reference
    for ( y = 0; y < h - rsize; y += rsize) {
        send_row(0,y,w);
        update_image(y);
    }

    reset_counts();

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) {
        // calculate left edge of the row
        for(int y2 = y+1; y2 < y + rsize; ++y2)
        {
            pixel(0,y2,1,1);
        }

        send_box_row(w,y,rsize);

        update_image(y);
    }

    reset_progress(1.0);
}

void 
fractFunc::box_row(int w, int y, int rsize)
{
    for(int x = 0; x < w - rsize ; x += rsize) {
        box(x,y,rsize);            
    }		
}

void
fractFunc::row_aa(int, int y, int w)
{
    for(int x = 0; x < w ; x++) {
        pixel_aa ( x, y);
    }
}
