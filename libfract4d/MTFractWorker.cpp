#include "fractFunc.h" // FIXME should be fractWorker

MTFractWorker::MTFractWorker(
    int n, 
    fractFunc *ff,
    fractal_t *f, 
    IImage *im)
{
    /* 0'th ftf is in this thread for calculations we don't want to offload */
    nWorkers = n > 1 ? n + 1 : 1;

    ptf = new STFractWorker[nWorkers];
    for(int i = 0; i < nWorkers; ++i)
    {
        if(!ptf[i].init(ff,f,im))
        {
            // failed to create - mark this dead 
            ok = false;	    
        }
    }

    if(n > 1)
    {
        ptp = new tpool<job_info_t,STFractWorker>(n,100,ptf);
    }
    else
    {
        ptp = NULL;
    }

}

MTFractWorker::~MTFractWorker()
{
    delete ptp;
    delete[] ptf;
}

void
MTFractWorker::row_aa(int x, int y, int n)
{

}

void
MTFractWorker::row(int x, int y, int n)
{

}
void
MTFractWorker::box(int x, int y, int rsize)
{

}
void
MTFractWorker::box_row(int w, int y, int rsize)
{

}
void
MTFractWorker::pixel(int x, int y, int h, int w)
{

}
void
MTFractWorker::pixel_aa(int x, int y)
{

}

void
MTFractWorker::reset_counts()
{

}

void
MTFractWorker::stats(int *pnDoubleIters, int *pnHalfIters, int *pk)
{

}
