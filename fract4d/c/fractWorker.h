
#ifndef FRACT_WORKER_H_
#define FRACT_WORKER_H_

#include "fractWorker_public.h"
#include "pointFunc_public.h"

/* enum for jobs */
typedef enum {
    JOB_NONE,
    JOB_BOX,
    JOB_BOX_ROW,
    JOB_ROW,
    JOB_ROW_AA
} job_type_t;

/* one unit of work */
typedef struct {
    job_type_t job;
    int x, y, param;
} job_info_t;

/* per-worker-thread fractal info */
class STFractWorker : public IFractWorker {
 public:
    void set_fractFunc(fractFunc *ff); 

    /* pointers to data also held in fractFunc */
    IImage *im;    

    /* not a ctor because we always create a whole array then init them */
    bool init(pf_obj *pfo, cmap_t *cmap, IImage *im, IFractalSite *site);

    ~STFractWorker();


    STFractWorker() {
	reset_counts();
        lastIter = 0;
    }

    // heuristic to see if we should use periodicity checking for next point
    inline bool periodGuess();

    // periodicity guesser for when we have the last count to hand 
    // (as for antialias pass)
    inline bool periodGuess(int last);

    // update whether last pixel bailed
    inline void periodSet(int *ppos);

    // top-level function for multi-threaded workers
    void work(job_info_t &tdata);

    // calculate a row of antialiased pixels
    void row_aa(int x, int y, int n);

    // calculate a row of pixels
    void row(int x, int y, int n);

    // calculate an rsize-by-rsize box of pixels
    void box(int x, int y, int rsize);

    // does the point at (x,y) have the same colour & iteration count
    // as the target?
    inline bool isTheSame(bool bFlat, int targetIter, int targetCol, int x, int y);

    // make an int corresponding to an RGB triple
    inline int RGB2INT(int y, int x);

    // calculate a row of boxes
    void box_row(int w, int y, int rsize);

    // calculate a single pixel
    void pixel(int x, int y, int h, int w);
    // calculate a single pixel in aa-mode
    void pixel_aa(int x, int y);

    // draw a rectangle of this colour
    void rectangle(rgba_t pixel, int x, int y, int w, int h);
    void rectangle_with_iter(rgba_t pixel, int iter, int x, int y, int w, int h);

    // calculate this point using antialiasing
    rgba_t antialias(int x, int y);

    void reset_counts();
    void stats(int *pnDoubleIters, int *pnHalfIters, int *pk);

    void flush() {};
    bool ok() { return m_ok; }
 
 private:
    fractFunc *ff;

    // function object which calculates the colors of points 
    // this is per-thread-func so it doesn't have to be re-entrant
    // and can have member vars
    pointFunc *pf; 

    // n pixels correctly classified that would be wrong 
    // if we halved iterations
    int nhalfiters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int ndoubleiters; 
    int k;	// number of pixels calculated    
    int lastIter; // how many iterations did last pixel take?

    bool m_ok;
};

#include "threadpool.h"

void worker(job_info_t& tdata, STFractWorker *pFunc);

// a composite subclass which holds an array of STFractWorkers and
// divides the work among them
class MTFractWorker : public IFractWorker
{
 public:
    MTFractWorker(int n, 
		  pf_obj *obj,
		  cmap_t *cmap,
		  IImage *im,
		  IFractalSite *site);
    ~MTFractWorker();

    void set_fractFunc(fractFunc *ff); 

    // operations
    virtual void row_aa(int x, int y, int n) ;
    virtual void row(int x, int y, int n) ;
    virtual void box(int x, int y, int rsize) ;
    virtual void box_row(int w, int y, int rsize);
    virtual void pixel(int x, int y, int h, int w);
    virtual void pixel_aa(int x, int y);

    // auto-deepening record keeping
    virtual void reset_counts();
    virtual void stats(int *pnDoubleIters, int *pnHalfIters, int *pk);

    virtual void flush();

    virtual bool ok();
    int nWorkers;
private:

    /* wait for a ready thread then give it some work */
    void send_cmd(job_type_t job, int x, int y, int param);
    void send_quit();

    // MEMBER FUNCTIONS

    void send_box(int x, int y, int rsize);
    void send_row(int x, int y, int n);
    void send_row_aa(int x, int y, int n);
    // ... in a worker thread
    void send_box_row(int w, int y, int rsize);

    STFractWorker *ptf;
    tpool<job_info_t,STFractWorker> *ptp;
    bool m_ok;
};

#endif /* FRACT_WORKER_H_ */
