#include "fractFunc.h" // FIXME should be fractWorker

/* redirect back to a member function */
void worker(job_info_t& tdata, STFractWorker *pFunc)
{
    pFunc->work(tdata);
}

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
    if(nWorkers > 1)
    {
	send_row_aa(0,y,n);
    }
    else
    {
	ptf->row_aa(0,y,n);
    }
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
    *pnDoubleIters = 0;
    *pnHalfIters = 0;
    *pk = 0;
    for(int i = 0; i < nWorkers; ++i)
    {
	int nd, nh, k;
	ptf[i].stats(&nd,&nh,&k);
        *pnDoubleIters += nd;
        *pnHalfIters += nh;
        *pk += k;
    }
}

void
MTFractWorker::send_cmd(job_type_t job, int x, int y, int param)
{
    //gf4d_fractal_try_finished_cond(gf);
    job_info_t work;

    work.job = job; 
    work.x = x; work.y = y; work.param = param;

    ptp->add_work(worker, work);
}

void
MTFractWorker::send_row(int x, int y, int w)
{
    //cout << "sent ROW" << y << "\n";
    send_cmd(JOB_ROW,x,y,w);
}

void
MTFractWorker::send_box_row(int w, int y, int rsize)
{
    //cout << "sent BXR" << y << "\n";
    send_cmd(JOB_BOX_ROW, w, y, rsize);
}

void
MTFractWorker::send_box(int x, int y, int rsize)
{
    //cout << "sent BOX" << y << "\n";
    send_cmd(JOB_BOX,x,y,rsize);
}

void
MTFractWorker::send_row_aa(int x, int y, int w)
{
    //cout << "sent RAA" << y << "\n";
    send_cmd(JOB_ROW_AA, x, y, w);
}
