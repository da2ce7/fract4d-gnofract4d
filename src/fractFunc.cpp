#include "fractFunc.h"
#include "pointFunc.h"
#include "iterFunc.h"
#include <stdio.h>

/* redirect back to a member function */
void worker(job_info_t& tdata, fractThreadFunc *pFunc)
{
    pFunc->work(tdata);
}

fractFunc::fractFunc(fractal_t *_f, image *_im, Gf4dFractal *_gf)
{
    gf = _gf;
    im = _im;
    f = _f; 
    ok = true;

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

    /* 0'th ftf is in this thread for calculations we don't want to offload */
    nThreadFuncs = f->nThreads > 1 ? f->nThreads + 1 : 1;

    ptf = new fractThreadFunc[nThreadFuncs];
    for(int i = 0; i < nThreadFuncs; ++i)
    {
        if(!ptf[i].init(this,f,im))
        {
            // failed to create - mark this dead 
            ok = false;
        }
    }

    /* threading */
    if(f->nThreads > 1)
    {
        ptp = new tpool<job_info_t,fractThreadFunc>(f->nThreads,100,ptf);
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
    delete[] ptf;
}

void 
fractFunc::clear()
{
    im->clear();    
}

void
fractFunc::send_cmd(job_type_t job, int x, int y, int param)
{
    //gf4d_fractal_try_finished_cond(gf);
    job_info_t work;

    work.job = job; 
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
    // add up all the subtotals
    for(int i = 0; i < nThreadFuncs; ++i)
    {
        nTotalDoubleIters += ptf[i].ndoubleiters;
        nTotalHalfIters += ptf[i].nhalfiters;
        nTotalK += ptf[i].k;
    }

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
            if(f->nThreads > 1)
            {
                send_row_aa(0,y,w);
            }
            else
            {
                ptf->row_aa(0,y,w);
                if(update_image(y))
                {
                    break;
                }
            }
        }
        reset_progress(1.0);
    }

}

void fractFunc::reset_counts()
{
    for(int i = 0; i < nThreadFuncs ; ++i)
    {
        ptf[i].reset_counts();
    }

    
    nTotalHalfIters = nTotalDoubleIters = nTotalK = 0;
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
            ptf->pixel ( x, y, drawsize, drawsize);
        }
        // extra pixels at end of lines
        for(int y2 = y; y2 < y + rsize; ++y2)
        {
            ptf->row (x, y2, w-x);
        }
        if(update_image(y)) 
        {
            goto done;
        }
    }
    // remaining lines
    for ( ; y < h ; y++)
    {
        ptf->row(0,y,w);
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
            ptf->box(x,y,rsize);
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
            ptf->pixel ( x, y, drawsize, drawsize);
        }
        // extra pixels at end of lines
        for(int y2 = y; y2 < y + rsize; ++y2)
        {
            ptf->row (x, y2, w-x);
        }
        if(update_image(y))
        {
            goto done;
        }
    }

    // remaining lines
    for ( y = h > rsize ? h - rsize : 0 ; y < h ; y++)
    {
        send_row(0,y,w);
        if(update_image(y)) goto done;
    }

    reset_progress(0.0);

    last_update_y = 0;
    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) {
        send_box_row(w,y,rsize);
        if(update_image(y)) goto done;
    }
    
 done:
    reset_progress(1.0);
}

