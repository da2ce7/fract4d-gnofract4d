#include "fractFunc.h"
#include "pointFunc.h"
#include "iterFunc.h"
#include <stdio.h>

bool
fractThreadFunc::init(fractFunc *ff_,fractal_t *f_, image *im_)
{
    ff = ff_;
    f = f_;
    im = im_;

    pf = pointFunc_new(
        f->pIterFunc, 
        f->bailout_type, 
        f->params[BAILOUT], 
        f->cizer, 
        f->colorFuncs[OUTER],
        f->colorFuncs[INNER]);

    if(NULL == pf)
    {
        return false;
    }
    return true;
}

fractThreadFunc::~fractThreadFunc()
{
    pointFunc_delete(pf);
}

/* we're in a worker thread */
void
fractThreadFunc::work(job_info_t& tdata)
{
    int nRows=0;

    int x = tdata.x;
    int y = tdata.y;
    int param = tdata.param;
    job_type_t job = tdata.job;

    if(gf4d_fractal_try_finished_cond(ff->gf))
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
    gf4d_fractal_image_changed(ff->gf,0,y,im->Xres(),y+ nRows);
    gf4d_fractal_progress_changed(ff->gf,(float)y/(float)im->Yres());
}

void
fractThreadFunc::row_aa(int x, int y, int w)
{
    for(int x = 0; x < w ; x++) {
        pixel_aa ( x, y);
    }
}

inline int 
fractThreadFunc::periodGuess()
{ 
    return (lastIter == -1 && f->maxiter > 4096) ? 0 : f->maxiter; //lastIter;
}

inline int 
fractThreadFunc::periodGuess(int last) {
    return (last == -1 /*&& f->maxiter > 4096*/) ? 0 : f->maxiter;
}

inline void 
fractThreadFunc::periodSet(int *ppos) {
    lastIter = *ppos;
}

void
fractThreadFunc::row(int x, int y, int n)
{
    for(int i = 0; i < n; ++i)
    {
        pixel(x+i,y,1,1);
    }
}

void
fractThreadFunc::reset_counts()
{
    ndoubleiters=0;
    nhalfiters=0;
}

inline int 
fractThreadFunc::RGB2INT(int y, int x)
{
    rgb_t pixel = im->get(x,y);
    int ret = (pixel.r << 16) | (pixel.g << 8) | pixel.b;
    return ret;
}

inline bool fractThreadFunc::isTheSame(
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

rgb_t
fractThreadFunc::antialias(int x, int y)
{
    dvec4 topleft = ff->aa_topleft + I2D_LIKE(x, f->params[MAGNITUDE]) * ff->deltax + 
        I2D_LIKE(y, f->params[MAGNITUDE]) * ff->deltay;

    dvec4 pos = topleft; 

    struct rgb ptmp;
    unsigned int pixel_r_val=0, pixel_g_val=0, pixel_b_val=0;    
    int p=0;

    int single_iters = im->getIter(x,y);
    int nNoPeriodIters = periodGuess(single_iters); 
    
    // top left
    (*(pf))(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;
    pos+=ff->delta_aa_x;

    // top right
    (*(pf))(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;
    pos = topleft + ff->delta_aa_y;

    // bottom left
    (*(pf))(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;
    pos+= ff->delta_aa_x;

    // bottom right
    (*(pf))(pos, f->maxiter,nNoPeriodIters,&ptmp,&p); 
    pixel_r_val += ptmp.r;
    pixel_g_val += ptmp.g;
    pixel_b_val += ptmp.b;

    ptmp.r = pixel_r_val / 4;
    ptmp.g = pixel_g_val / 4;
    ptmp.b = pixel_b_val / 4;
    return ptmp;
}


void 
fractThreadFunc::pixel(int x, int y,int w, int h)
{
    int *ppos = im->iter_buf + y*im->Xres() + x;
    struct rgb pixel;

    if(*ppos != -1) return;

    // calculate coords of this point
    dvec4 pos = ff->topleft + 
        I2D_LIKE(x, f->params[MAGNITUDE]) * ff->deltax + 
        I2D_LIKE(y, f->params[MAGNITUDE]) * ff->deltay;
		
    (*(pf))(pos, f->maxiter,periodGuess(), &pixel,ppos); 
    periodSet(ppos);

    // test for iteration depth
    if(f->auto_deepen && k++ % ff->AUTO_DEEPEN_FREQUENCY == 0)
    {
        int i=0;

        (*(pf))(pos, f->maxiter*2,periodGuess()*2,NULL,&i);

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

void 
fractThreadFunc::box_row(int w, int y, int rsize)
{
    // calculate left edge of the row
    for(int y2 = y+1; y2 < y + rsize; ++y2)
    {
        pixel(0,y2,1,1);
    }

    for(int x = 0; x < w - rsize ; x += rsize) {
        box(x,y,rsize);            
    }		
}

void
fractThreadFunc::pixel_aa(int x, int y)
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

void 
fractThreadFunc::box(int x, int y, int rsize)
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

inline void
fractThreadFunc::rectangle(struct rgb pixel, int x, int y, int w, int h)
{
    for(int i = y ; i < y+h; i++)
    {
        for(int j = x; j < x+w; j++) {
            im->put(j,i,pixel);
        }
    }
}

