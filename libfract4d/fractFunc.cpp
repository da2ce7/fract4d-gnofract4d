#include "fractFunc.h"
#include "pointFunc.h"
#include "iterFunc.h"
#include <stdio.h>


fractFunc::fractFunc(
    fractal_t *f_, 
    IFractWorker *fw,
    IImage *im_, 
    IFractalSite *site_)
{
    site = site_;
    im = im_;
    f = f_; 
    ok = true;
    worker = fw;

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
    nTotalHalfIters = nTotalDoubleIters = nTotalK = 0;
    clear();

    status_changed(GF4D_FRACTAL_COMPILING);

    worker->set_fractFunc(this);

    last_update_y = 0;
};

fractFunc::~fractFunc()
{

}

void 
fractFunc::clear()
{
    im->clear();    
}

bool
fractFunc::update_image(int i)
{
    image_changed(0,last_update_y,im->Xres(),i);
    progress_changed((float)i/(float)im->Yres());
    last_update_y = i;
    return try_finished_cond();
}

// see if the image needs more (or less) iterations to display
// properly returns +ve if more are required, -ve if less are
// required, 0 if it's correct. This is a very poor heuristic - a
// histogram approach would be better

int
fractFunc::updateiters()
{
    // add up all the subtotals
    worker->stats(&nTotalDoubleIters,&nTotalHalfIters,&nTotalK);

    double doublepercent = ((double)nTotalDoubleIters*AUTO_DEEPEN_FREQUENCY*100)/nTotalK;
    double halfpercent = ((double)nTotalHalfIters*AUTO_DEEPEN_FREQUENCY*100)/nTotalK;
		
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

    for(int i = 0; i < f->nThreads; ++i)
    {
        last_update_y = 0;
        for(int y = i; y < h ; y+= f->nThreads) {
	    worker->row_aa(0,y,w);
	    if(update_image(y))
	    {
		break;
	    }
        }
        reset_progress(1.0);
    }

}

void fractFunc::reset_counts()
{
    worker->reset_counts();
    
    nTotalHalfIters = nTotalDoubleIters = nTotalK = 0;
}

void fractFunc::reset_progress(float progress)
{
    worker->flush();
    image_changed(0,0,im->Xres(),im->Yres());
    progress_changed(progress);
}

void fractFunc::draw_all()
{
    status_changed(GF4D_FRACTAL_CALCULATING);
    
    draw(8,8);
    
    int deepen;
    while((deepen = updateiters()) > 0)
    {
        f->maxiter *= 2;
        status_changed(GF4D_FRACTAL_DEEPENING);
        draw(8,1);
    }
    
    if(f->eaa > AA_NONE) {
        status_changed(GF4D_FRACTAL_ANTIALIASING);
        draw_aa();
    }
    
    // we do this after antialiasing because otherwise sometimes the
    // aa pass makes the image shallower, which is distracting
    if(deepen < 0)
    {
        f->maxiter /= 2;
    }
    status_changed(GF4D_FRACTAL_DONE);
    progress_changed(0.0);
}

void fractFunc::draw(int rsize, int drawsize)
{
    reset_counts();

    if(f->nThreads > 1)
    {
        draw_threads(rsize, drawsize);
        return;
    }

    int x,y;
    int w = im->Xres();
    int h = im->Yres();

    /* reset progress indicator & clear screen */
    last_update_y = 0;
    reset_progress(0.0);

    // first pass - big blocks and edges
    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        // main large blocks 
        for ( x = 0 ; x< w - rsize ; x += rsize) 
        {
            worker->pixel ( x, y, drawsize, drawsize);
        }
        // extra pixels at end of lines
        for(int y2 = y; y2 < y + rsize; ++y2)
        {
            worker->row (x, y2, w-x);
        }
        if(update_image(y)) 
        {
            goto done;
        }
    }
    // remaining lines
    for ( ; y < h ; y++)
    {
        worker->row(0,y,w);
        if(update_image(y)) 
        {
            goto done;
        }
    }

    last_update_y = 0;
    reset_progress(0.0);

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) {
        for(x = 0; x < w - rsize ; x += rsize) {
            worker->box(x,y,rsize);
        }
        if(update_image(y))
        {
            goto done;
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

    last_update_y = 0;
    reset_progress(0.0);

    // first pass - big blocks and edges
    // do this in current thread - it's fast anyway
    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        // main large blocks 
        for ( x = 0 ; x< w - rsize ; x += rsize) 
        {
            worker->pixel ( x, y, drawsize, drawsize);
        }
        // extra pixels at end of lines
        for(int y2 = y; y2 < y + rsize; ++y2)
        {
            worker->row (x, y2, w-x);
        }
        if(update_image(y))
        {
            goto done;
        }
    }

    // remaining lines
    for ( y = h > rsize ? h - rsize : 0 ; y < h ; y++)
    {
        worker->row(0,y,w);
        if(update_image(y)) goto done;
    }

    reset_progress(0.0);

    last_update_y = 0;
    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) {
        worker->box_row(w,y,rsize);
        if(update_image(y)) goto done;
    }
    
 done:
    reset_progress(1.0);
}

