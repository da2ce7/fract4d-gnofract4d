#include "fractFunc.h"
#include "pointFunc.h"

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
        f->potential);
    
    depth = f->antialias ? 2 : 1; 
    
    f->update_matrix();
    rot = f->rot/D_LIKE(im->Xres,f->params[MAGNITUDE]);
    deltax = rot[VX];
    deltay = rot[VY];
    ddepth = D_LIKE((double)(depth*2),f->params[MAGNITUDE]);
    delta_aa_x = deltax / ddepth;
    delta_aa_y = deltay / ddepth;
    
    debug_precision(deltax[VX],"deltax");
    debug_precision(f->params[XCENTER],"center");
    topleft = f->get_center() -
        deltax * D_LIKE(im->Xres / 2.0, f->params[MAGNITUDE])  -
        deltay * D_LIKE(im->Yres / 2.0, f->params[MAGNITUDE]);

    d depthby2 = ddepth/D_LIKE(2.0,ddepth);
    aa_topleft = topleft - (delta_aa_y + delta_aa_x) * depthby2;
    
    debug_precision(topleft[VX],"topleft");
    nhalfiters = ndoubleiters = k = 0;
    //p = im->iter_buf;
    clear();

    last_update_y = 0;
};

void 
fractFunc::clear()
{
    im->clear();    
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

inline struct rgb
fractFunc::antialias(const dvec4& cpos)
{
    struct rgb ptmp;
    unsigned int pixel_r_val=0, pixel_g_val=0, pixel_b_val=0;
    int i,j;
    dvec4 topleft = cpos;

    for(i=0;i<depth;i++) {
        dvec4 pos = topleft; 
        for(j=0;j<depth;j++) {
            int p;
            (*pf)(pos, f->maxiter,&ptmp,&p); 
            pixel_r_val += ptmp.r;
            pixel_g_val += ptmp.g;
            pixel_b_val += ptmp.b;
            pos+=delta_aa_x;
        }
        topleft += delta_aa_y;
    }
    ptmp.r = pixel_r_val / (depth * depth);
    ptmp.g = pixel_g_val / (depth * depth);
    ptmp.b = pixel_b_val / (depth * depth);
    return ptmp;
}

inline void 
fractFunc::pixel(int x, int y,int w, int h)
{
    int *ppos = im->iter_buf + y*im->Xres + x;
    struct rgb pixel;

    if(*ppos != -1) return;

    // calculate coords of this point
    dvec4 pos = topleft + 
        I2D_LIKE(x, f->params[MAGNITUDE]) * deltax + 
        I2D_LIKE(y, f->params[MAGNITUDE]) * deltay;
		
    (*pf)(pos, f->maxiter,&pixel,ppos); 
	
    // test for iteration depth
    if(f->auto_deepen && k++ % AUTO_DEEPEN_FREQUENCY == 0)
    {
        int i;

        (*pf)(pos, f->maxiter*2,NULL,&i);

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
    dvec4 pos = aa_topleft + I2D_LIKE(x, f->params[MAGNITUDE]) * deltax + 
        I2D_LIKE(y, f->params[MAGNITUDE]) * deltay;

    struct rgb pixel;

    // if aa type is fast, short-circuit some points
    if(f->antialias == AA_FAST &&
       x > 0 && x < im->Xres-1 && y > 0 && y < im->Yres-1)
    {
        // check to see if this point is surrounded by others of the same colour
        // if so, don't bother recalculating
        int iter = im->iter_buf[y * im->Xres + x];
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
    pixel = antialias(pos);

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

void
fractFunc::update_image(int i)
{
    gf4d_fractal_image_changed(gf,0,last_update_y,im->Xres,i);
    gf4d_fractal_progress_changed(gf,(float)i/(float)im->Yres);
    last_update_y = i;
}

// see if the image needs more (or less) iterations to display properly
// returns +ve if more are required, -ve if less are required, 0 if 
// it's correct. This is very heuristic - a histogram approach would
// be better

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
    int w = im->Xres;
    int h = im->Yres;

    reset_counts();

    gf4d_fractal_image_changed(gf,0,0,w,h);
    gf4d_fractal_progress_changed(gf,0.0);

    for(int y = 0; y < h ; y++) {
        for(int x = 0; x < w ; x++) {
            pixel_aa ( x, y);
        }
        update_image(y);
    }
    gf4d_fractal_image_changed(gf,0,0,w,h);		     
    gf4d_fractal_progress_changed(gf,1.0);	
}

inline int fractFunc::RGB2INT(int y, int x)
{
    rgb_t pixel = im->get(x,y);
	int ret = (pixel.r << 16) | (pixel.g << 8) | pixel.b;
    return ret;
}

/*
void
fractFunc::scan_rect(soidata_t& s)
{
    int w = s.x2 - s.x1;
    int h = s.y2 - s.y1;

    colorizer_t *cf = f->cizer;

    for(int y = 0; y < h ; ++y)
    {
        for(int x = 0; x < w; ++x)
        {			
            scratch_space scratch;
            s.interp_both(scratch,(double)x/w,(double)y/h);
            int iter = s.iter;
            do
            {
                mandelbrot_iter(scratch);
                if(iter++ >= f->maxiter) {
                    iter=-1; break;
                }
                mag_bailout(scratch,HAS_X2 | HAS_Y2);
            }while(scratch[EJECT_VAL] < 4.0);
			
            rgb_t pixel = (*cf)(iter,scratch,0);
            rectangle(pixel,s.x1+x,s.y1+y,1,1);		       
        } 
    }
    gf4d_fractal_image_changed(gf,s.x1,s.y1,s.x2,s.y2);
}
*/
#if 0
void fractFunc::soi()
{
    /* create first chunk of data, describing whole screen */
    soidata_t soi_init(0,0,im->Xres,im->Yres,0,topleft,deltax,deltay);
    soi_queue.push(soi_init);

    /* insert into queue */
	
    do
    {
        soidata_t s = soi_queue.front();
        /* remove element */
        soi_queue.pop();
		
        /* if too small, draw by scanning */
        if(s.x2 - s.x1 < 8) 
        {
            scan_rect(s);
            continue;
        }
        int old_iter = s.iter;
        /* iterate until it splits or maxiter */
        do {
            s.iterate();
            if(s.iter >= f->maxiter) 
            {
				/* draw black box */
                break;
            }
        }while(! s.needs_split());

        colorizer_t *cf = f->cizer;

        // this rect is entirely within the set
        if(s.iter >= f->maxiter)
        {
            rgb_t pixel = (*cf)(-1,s.data[0],0);
            /* draw interior rect */
            rectangle(pixel,s.x1,s.y1,s.x2-s.x1,s.y2-s.y1);
            gf4d_fractal_image_changed(gf,s.x1,s.y1,s.x2,s.y2);
        }
        else
        {
            // undo the last iteration, which broke tolerance
            s.revert(); 
			
            //printf("progress: %d\n",s.iter - old_iter);
            rgb_t pixel = (*cf)(s.iter,s.data[0],0);
			
            /* draw with split number of iterations */
            rectangle(pixel,s.x1,s.y1,s.x2-s.x1,s.y2-s.y1);
            gf4d_fractal_image_changed(gf,s.x1,s.y1,s.x2,s.y2);
			
            /* create 4 new rectangles & add to front of queue */
            soi_queue.push(s.topleft());
            soi_queue.push(s.topright());
            soi_queue.push(s.botleft());
            soi_queue.push(s.botright());			
        }
    }while(!(soi_queue.empty()));

    gf4d_fractal_status_changed(gf,GF4D_FRACTAL_DONE);
}
#endif

inline bool fractFunc::isTheSame(
    bool bFlat, int targetIter, int targetCol, int x, int y)
{
    if(bFlat)
    {
        // does this point have the target # of iterations?
        if(im->iter_buf[y * im->Xres + x] != targetIter) return false;
        // if we're using continuous potential, does it have
        // the same colour too?
        if(f->potential && RGB2INT(y,x) != targetCol) return false;
    }
    return bFlat;
}

void fractFunc::reset_counts()
{
    last_update_y=0;
    ndoubleiters=0;
    nhalfiters=0;
}

void fractFunc::draw(int rsize, int drawsize)
{
    int x,y;
    int w = im->Xres;
    int h = im->Yres;

    reset_counts();

    gf4d_fractal_image_changed(gf,0,0,w,h);
    gf4d_fractal_progress_changed(gf,0.0);

    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        update_image(y);
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
    }
    // remaining lines
    for ( ; y < h ; y++)
    {
        update_image(y);
        row(0,y,w);
    }

    reset_counts();

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) {
        update_image(y);
        for(x = 0; x < w - rsize ; x += rsize) {
            // calculate edges of box to see if they're all the same colour
            // if they are, we assume that the box is a solid colour and
            // don't calculate the interior points
            bool bFlat = true;
            int iter = im->iter_buf[y * w + x];
            int pcol = RGB2INT(y,x);

            for(int x2 = x; x2 < x + rsize; ++x2)
            {
                pixel(x2,y,1,1);
                bFlat = isTheSame(bFlat,iter,pcol,x2,y);
                pixel(x2,y+rsize-1,1,1);
                bFlat = isTheSame(bFlat,iter,pcol,x2,y+rsize-1);
            }
            for(int y2 = y+1; y2 < y + rsize; ++y2)
            {
                pixel(x,y2,1,1);
                bFlat = isTheSame(bFlat, iter, pcol, x+rsize-1, y2);
                pixel(x+rsize-1,y2,1,1);
                bFlat = isTheSame(bFlat,iter,pcol,x+rsize-1,y2);
            }

            if(!bFlat)
            {
                // we do need to calculate the interior 
                // points individually
                for(int y2 = y + 1 ; y2 < y + rsize - 1; ++y2)
                {
                    row(x+1,y2,rsize-2);
                }		
            }		
        }		
    }

    gf4d_fractal_image_changed(gf,0,0,im->Xres,im->Yres);	
    gf4d_fractal_progress_changed(gf,1.0);	
}
