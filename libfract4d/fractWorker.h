#include "threadpool.h"

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

class IFractWorker {
public:
    // calculate a row of antialiased pixels
    virtual void row_aa(int x, int y, int n) =0;

    // calculate a row of pixels
    virtual void row(int x, int y, int n) =0;

    // calculate an rsize-by-rsize box of pixels
    virtual void box(int x, int y, int rsize) =0;

    // calculate a row of boxes
    virtual void box_row(int w, int y, int rsize) =0;

    // calculate a single pixel
    virtual void pixel(int x, int y, int h, int w) =0;

    // calculate a single pixel in aa-mode
    virtual void pixel_aa(int x, int y) =0;

    // auto-deepening record keeping
    virtual void reset_counts() =0;
    virtual void stats(int *pnDoubleIters, int *pnHalfIters, int *pk) =0;

    virtual ~IFractWorker() {};
};

/* per-worker-thread fractal info */
class STFractWorker : public IFractWorker {
 public:
    fractFunc *ff;

    /* pointers to data also held in fractFunc */
    fractal_t *f; 
    IImage *im;    

    /* not a ctor because we always create a whole array then init them */
    bool init(fractFunc *ff, fractal_t *f, IImage *im);

    ~STFractWorker();

    // function object which calculates the colors of points 
    // this is per-thread-func so it doesn't have to be re-entrant
    // and can have member vars
    pointFunc *pf; 


    STFractWorker() {
	reset_counts();
        lastIter = 0;
    }
    // try that many without periodicity checking if it did bail out,
    // if it didn't bail, start periodicity checking immediately
    inline int periodGuess();

    // period guesser for when we have the last count to hand (as for antialias pass)
    inline int periodGuess(int last);

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
    void rectangle(struct rgb pixel, int x, int y, int w, int h);
    void rectangle_with_iter(struct rgb pixel, int iter, int x, int y, int w, int h);

    // calculate this point using antialiasing
    struct rgb antialias(int x, int y);

    void reset_counts();
    void stats(int *pnDoubleIters, int *pnHalfIters, int *pk);

 private:
    // n pixels correctly classified that would be wrong 
    // if we halved iterations
    int nhalfiters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int ndoubleiters; 
    int k;	// number of pixels calculated    
    int lastIter; // how many iterations did last pixel take?

};

// a composite subclass which holds an array of STFractWorkers and
// divides the work among them
class MTFractWorker : public IFractWorker
{
 public:
    MTFractWorker(int n, 
		  fractFunc *ff, 
		  fractal_t *f, 
		  IImage *im);
    ~MTFractWorker();

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

    tpool<job_info_t,STFractWorker> *ptp;
    STFractWorker *ptf;
    int nWorkers;
    bool ok;
};
