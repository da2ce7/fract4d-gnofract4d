#include "fractFunc.h"
#include <stdio.h>
#include <stdlib.h>

#include <cassert>


dmat4
rotated_matrix(double *params)
{
    d one = d(1.0);
    d zero = d(0.0);
    dmat4 id = identity3D<d>(params[MAGNITUDE],zero);

    return id * 
        rotXY<d>(params[XYANGLE],one,zero) *
        rotXZ<d>(params[XZANGLE],one,zero) * 
        rotXW<d>(params[XWANGLE],one,zero) *
        rotYZ<d>(params[YZANGLE],one,zero) *
        rotYW<d>(params[YWANGLE],one,zero) *
        rotZW<d>(params[ZWANGLE],one,zero);
}

// The eye vector is the line between the center of the screen and the
// point where the user's eye is deemed to be. It's effectively the line
// perpendicular to the screen in the -Z direction, scaled by the "eye distance"

dvec4
test_eye_vector(double *params, double dist)
{
    dmat4 mat = rotated_matrix(params);
    return mat[VZ] * -dist;
}
 
fractFunc::fractFunc(
        d *params_,
	int eaa_,
	int maxiter_,
	int nThreads_,
	bool auto_deepen_,
	bool yflip,
	bool periodicity_,
	render_type_t render_type_,
	IFractWorker *fw,
	IImage *im_, 
	IFractalSite *site_)
{
    site = site_;
    im = im_;
    ok = true;
    render_type = render_type_;
    //printf("render type %d\n", render_type);
    worker = fw;
    params = params_;

    eaa = eaa_;
    depth = eaa == AA_NONE ? 1 : 2;
    maxiter = maxiter_;
    nThreads = nThreads_;
    auto_deepen = auto_deepen_;
    periodicity = periodicity_;

    dvec4 center = dvec4(
	params[XCENTER],params[YCENTER],
	params[ZCENTER],params[WCENTER]);

    rot = rotated_matrix(params);

    dvec4 rotvz = rot[VZ];

    eye_point = center + rot[VZ] * -10.0; // FIXME add eye distance parameter

    rot = rot/im->Xres();
    // distance to jump for one pixel down or across
    deltax = rot[VX];
    // if yflip, draw Y axis down, otherwise up
    deltay = yflip ? rot[VY] : -rot[VY]; 

    // half that distance
    delta_aa_x = deltax / 2.0;    
    delta_aa_y = deltay / 2.0;

    // topleft is now top left corner of top left pixel...
    topleft = center -
        deltax * im->Xres() / 2.0 -
        deltay * im->Yres() / 2.0;


    // .. then offset to center of pixel
    topleft += delta_aa_x + delta_aa_y;

    // antialias: offset to middle of top left quadrant of pixel
    aa_topleft = topleft - (delta_aa_y + delta_aa_x) / 2.0;
    
    nTotalHalfIters = nTotalDoubleIters = nTotalK = 0;

    worker->set_fractFunc(this);

    last_update_y = 0;
};

fractFunc::~fractFunc()
{    

}

bool
fractFunc::update_image(int i)
{
    bool done = try_finished_cond();
    if(!done)
    {
	image_changed(0,last_update_y,im->Xres(),i);
	progress_changed((float)i/(float)im->Yres());
    }
    last_update_y = i;
    return done; 
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
       maxiter > 32)
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

    // if we have multiple threads,make sure they don't modify
    // pixels the other thread will look at - that wouldn't be 
    // an error per se but would make drawing nondeterministic,
    // which I'm trying to avoid
    // We do this by drawing every even line, then every odd one.
    for(int i = 0; i < 2 ; ++i)
    {
        last_update_y = 0;
        for(int y = i; y < h ; y+= 2) {
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

// change everything with a fate of IN to UNKNOWN, because 
// image got deeper
void fractFunc::clear_in_fates()
{
    // FIXME can end up with some subpixels known and some unknown
    for(int y = 0; y < im->Yres(); ++y)
    {
	for(int x = 0; x < im->Xres(); ++x)
	{
	    for(int n = 0; n < im->getNSubPixels(); ++n)
	    {
		fate_t f = im->getFate(x,y,n);
		if(f & ~FATE_SOLID != 0)
		{
		    im->setFate(x,y,n, FATE_UNKNOWN);
		}
	    }
	}
    }
}


void fractFunc::draw_all()
{
    status_changed(GF4D_FRACTAL_CALCULATING);
    
#if !defined(NO_CALC)
    // NO_CALC is used to stub out the actual fractal stuff so we can
    // profile & optimize the rest of the code without it confusing matters
    draw(8,8);
    
    
    int deepen;
    while((deepen = updateiters()) > 0)
    {
        maxiter *= 2;
	iters_changed(maxiter);
        status_changed(GF4D_FRACTAL_DEEPENING);
	clear_in_fates();
        draw(8,1);
    }
    
    if(eaa > AA_NONE) {
        status_changed(GF4D_FRACTAL_ANTIALIASING);
        draw_aa();
    }
    
    // we do this after antialiasing because otherwise sometimes the
    // aa pass makes the image shallower, which is distracting
    if(deepen < 0)
    {
        maxiter /= 2;
	iters_changed(maxiter);
    }
#endif

    progress_changed(0.0);
    status_changed(GF4D_FRACTAL_DONE);
}

void fractFunc::draw(int rsize, int drawsize)
{
    //printf("drawing: %d\n", render_type);
    reset_counts();

    // init RNG based on time before generating image
    time_t now;
    time(&now);
    srand((unsigned int)now);

    if(nThreads > 1)
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

dvec4
fractFunc::vec_for_point(double x, double y)
{
    dvec4 point = topleft + x * deltax + y * deltay;
    dvec4 vec = point - eye_point;
    vec.norm();
    return vec;
}

void 
calc(	
    d *params,
    int eaa,
    int maxiter,
    int nThreads,
    pf_obj *pfo, 
    ColorMap *cmap, 
    bool auto_deepen,
    bool yflip,
    bool periodicity,
    bool dirty,
    render_type_t render_type,
    IImage *im, 
    IFractalSite *site)
{
    assert(NULL != im && NULL != site && 
	   NULL != cmap && NULL != pfo && NULL != params);
    IFractWorker *worker = IFractWorker::create(nThreads,pfo,cmap,im,site);

    if(worker && worker->ok())
    {
	fractFunc ff(
	    params, 
	    eaa,
	    maxiter,
	    nThreads,
	    auto_deepen,
	    yflip,
	    periodicity,
	    render_type,
	    worker,
	    im,
	    site);

	if(dirty)
	{
	    im->clear();
	}
	ff.draw_all();
    }
    delete worker;
}
