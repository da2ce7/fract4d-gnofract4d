#include "fractFunc.h"
#include "pointFunc_public.h"
#include "fractWorker.h"
#include <stdio.h>

IFractWorker *
IFractWorker::create(
    int nThreads,pf_obj *pfo, cmap_t *cmap, IImage *im_, IFractalSite *site)
{
// can IFDEF here if threads are not available
    if ( nThreads > 1)
    {
	return new MTFractWorker(nThreads,pfo,cmap,im_,site);
    }
    else
    {
	STFractWorker *w = new STFractWorker();
	if(!w) return w;
	w->init(pfo,cmap,im_,site);
	return w;
    }
} 

bool
STFractWorker::init(
    pf_obj *pfo, cmap_t *cmap, IImage *im_, IFractalSite *site)
{
    ff = NULL;
    im = im_;
    m_ok = true;

    pf = pointFunc::create(pfo,cmap,site);
    if(NULL == pf)
    {
	m_ok = false;
    }
    return m_ok;
}

STFractWorker::~STFractWorker()
{
    delete pf;
}

void
STFractWorker::set_fractFunc(fractFunc *ff_)
{
    ff = ff_;
}

/* we're in a worker thread */
void
STFractWorker::work(job_info_t& tdata)
{
    int nRows=0;

    int x = tdata.x;
    int y = tdata.y;
    int param = tdata.param;
    job_type_t job = tdata.job;

    if(ff->try_finished_cond())
    {
        // interrupted - just return without doing anything
        // this is less efficient than clearing the queue but easier
        return;
    }

    /* carry them out */
    switch(job)
    {
    case JOB_BOX:
        //cout << "BOX " << y << " " << pthread_self() << "\n";
        box(x,y,param);
        nRows = param;
        break;
    case JOB_ROW:
        //cout << "ROW " << y << " " << pthread_self() << "\n";
        row(x,y,param);
        nRows=1;
        break;
    case JOB_BOX_ROW:
        //cout << "BXR " << y << " " << pthread_self() << "\n";
        box_row(x, y, param);
        nRows = param;
        break;
    case JOB_ROW_AA:
        //cout << "RAA " << y << " " << pthread_self() << "\n";
        row_aa(x,y,param);
        nRows=1;
        break;
    default:
        printf("Unknown job id %d ignored\n", (int) job);
    }
    ff->image_changed(0,y,im->Xres(),y+ nRows);
    ff->progress_changed((float)y/(float)im->Yres());
}

void
STFractWorker::row_aa(int x, int y, int w)
{
    for(int x = 0; x < w ; x++) {
        pixel_aa ( x, y);
    }
}

inline bool 
STFractWorker::periodGuess()
{ 
    return (ff->periodicity && lastIter == -1 && ff->maxiter > 4096);
}

inline bool 
STFractWorker::periodGuess(int last) {
    return ff->periodicity && last == -1;
}

inline void 
STFractWorker::periodSet(int *ppos) {
    lastIter = *ppos;
}

void
STFractWorker::row(int x, int y, int n)
{
    for(int i = 0; i < n; ++i)
    {
        pixel(x+i,y,1,1);
    }
}

void
STFractWorker::reset_counts()
{
    ndoubleiters=0;
    nhalfiters=0;
    k=0;
}

void 
STFractWorker::stats(int *pnDoubleIters, int *pnHalfIters, int *pk)
{
    *pnDoubleIters = ndoubleiters;
    *pnHalfIters = nhalfiters;
    *pk = k;
}

inline int 
STFractWorker::RGB2INT(int y, int x)
{
    rgba_t pixel = im->get(x,y);
    int ret = (pixel.r << 16) | (pixel.g << 8) | pixel.b;
    return ret;
}

inline bool STFractWorker::isTheSame(
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

rgba_t
STFractWorker::antialias(int x, int y)
{
    dvec4 topleft = ff->aa_topleft + x * ff->deltax + y * ff->deltay;

    dvec4 pos = topleft; 

    rgba_t ptmp;
    unsigned int pixel_r_val=0, pixel_g_val=0, pixel_b_val=0;    
    int p=0;

    int single_iters = im->getIter(x,y);
    bool checkPeriod = periodGuess(single_iters); 

    // top left
    pf->calc(pos.n, ff->maxiter,checkPeriod,x,y,1,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;

    // top right
    pos+=ff->delta_aa_x;
    pf->calc(pos.n, ff->maxiter,checkPeriod,x,y,2,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;

    // bottom left
    pos = topleft + ff->delta_aa_y;
    pf->calc(pos.n, ff->maxiter,checkPeriod,x,y,3,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;

    // bottom right
    pos+= ff->delta_aa_x;
    pf->calc(pos.n, ff->maxiter,checkPeriod,x,y,4,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;

    ptmp.r = pixel_r_val / 4;
    ptmp.g = pixel_g_val / 4;
    ptmp.b = pixel_b_val / 4;
    return ptmp;
}


void 
STFractWorker::pixel(int x, int y,int w, int h)
{
    int iter = im->getIter(x,y);
    rgba_t pixel;
    if(iter != -1) return;

    // calculate coords of this point
    dvec4 pos = ff->topleft + x * ff->deltax + y * ff->deltay;

    //printf("(%g,%g,%g,%g)\n",pos[VX],pos[VY],pos[VZ],pos[VW]);

    assert(pf != NULL && m_ok == true);
    pf->calc(pos.n, ff->maxiter,periodGuess(), x,y,0,&pixel,&iter); 
    periodSet(&iter);
    im->setIter(x,y,iter);

    rectangle(pixel,x,y,w,h);

    // test for iteration depth
    if(ff->auto_deepen && k++ % ff->AUTO_DEEPEN_FREQUENCY == 0)
    {
        int i=0;

        pf->calc(pos.n, ff->maxiter*2,periodGuess(),x,y,-1,&pixel,&i);

        if( (i > ff->maxiter/2) && (i < ff->maxiter))
        {
            /* we would have got this wrong if we used 
             * half as many iterations */
            nhalfiters++;
        }
        else if( (i > ff->maxiter) && (i < ff->maxiter*2))
        {
            /* we would have got this right if we used
             * twice as many iterations */
            ndoubleiters++;
        }
    }
}

void 
STFractWorker::box_row(int w, int y, int rsize)
{
    for(int x = 0; x < w - rsize ; x += rsize) {
        box(x,y,rsize);            
    }		
}

void
STFractWorker::pixel_aa(int x, int y)
{
    rgba_t pixel;

    int iter = im->getIter(x,y);
    // if aa type is fast, short-circuit some points
    if(ff->eaa == AA_FAST &&
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

void 
STFractWorker::box(int x, int y, int rsize)
{
    // calculate edges of box to see if they're all the same colour
    // if they are, we assume that the box is a solid colour and
    // don't calculate the interior points
    bool bFlat = true;
    int iter = im->getIter(x,y);
    int pcol = RGB2INT(y,x);
    
    // calculate top and bottom of box + remember flatness
    for(int x2 = x; x2 < x + rsize; ++x2)
    {
        pixel(x2,y,1,1);
        bFlat = isTheSame(bFlat,iter,pcol,x2,y);
        pixel(x2,y+rsize-1,1,1);        
        bFlat = isTheSame(bFlat,iter,pcol,x2,y+rsize-1);
    }
    // calc left of next box over & check for flatness
    for(int y2 = y; y2 <= y + rsize; ++y2)
    {
        pixel(x,y2,1,1);
        bFlat = isTheSame(bFlat, iter, pcol, x, y2);
        pixel(x+rsize-1,y2,1,1);
        bFlat = isTheSame(bFlat,iter,pcol,x+rsize-1,y2);
    }
    
    if(bFlat)
    {
        // just draw a solid rectangle
        rgba_t pixel = im->get(x,y);
        rectangle_with_iter(pixel,iter,x+1,y+1,rsize-2,rsize-2);
    }
    else
    {
        // we do need to calculate the interior 
        // points individually
        for(int y2 = y + 1 ; y2 < y + rsize -1; ++y2)
        {
            row(x+1,y2,rsize-2);
        }		
    }		
}

inline void
STFractWorker::rectangle(rgba_t pixel, int x, int y, int w, int h)
{
    for(int i = y ; i < y+h; i++)
    {
        for(int j = x; j < x+w; j++) {
            im->put(j,i,pixel);
        }
    }
}

inline void
STFractWorker::rectangle_with_iter(
    rgba_t pixel, int iter, int x, int y, int w, int h)
{
    for(int i = y ; i < y+h; i++)
    {
        for(int j = x; j < x+w; j++) {
            im->put(j,i,pixel);
            im->setIter(j,i,iter);
        }
    }
}

