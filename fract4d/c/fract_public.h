#ifndef _FRACT_PUBLIC_H_
#define _FRACT_PUBLIC_H_

#include <pthread.h>

// current state of calculation
enum {
    GF4D_FRACTAL_DONE,
    GF4D_FRACTAL_CALCULATING,
    GF4D_FRACTAL_DEEPENING,
    GF4D_FRACTAL_ANTIALIASING,
    GF4D_FRACTAL_PAUSED
};

typedef enum {
    AA_NONE = 0,
    AA_FAST,
    AA_BEST,
    AA_DEFAULT /* used only for effective_aa - means use aa from fractal */
} e_antialias;

typedef enum {
    XCENTER,
    YCENTER,
    ZCENTER,
    WCENTER,
    MAGNITUDE,
    XYANGLE,
    XZANGLE,
    XWANGLE,
    YZANGLE,
    YWANGLE,
    ZWANGLE,
} param_t;

typedef enum {
    TWO_D,
    LANDSCAPE,
    THREE_D
} render_type_t;

// colorFunc indices
#define OUTER 0
#define INNER 1

#define N_PARAMS 11

//class colorizer;
class IImage;

#include "pointFunc_public.h"

// a type which must be implemented by the user of 
// libfract4d. We use this to inform them of the progress
// of an ongoing calculation

// WARNING: if nThreads > 1, these can be called back on a different
// thread, possibly several different threads at the same time. It is
// the callee's responsibility to handle mutexing.

// member functions are do-nothing rather than abstract in case you
// don't want to do anything with them
class calc_args;

class IFractalSite
{
 public:
    virtual ~IFractalSite() {};

    // the parameters have changed (usually due to auto-deepening)
    virtual void iters_changed(int numiters) {};
    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int y1, int x2, int y2) {};
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress) {};
    // one of the status values above
    virtual void status_changed(int status_val) {};

    // per-pixel callback for debugging
    virtual void pixel_changed(
	const double *params, int maxIters, bool checkPeriod,
	int x, int y, int aa,
	double dist, int fate, int nIters,
	int r, int g, int b, int a) {};
 
    // async support

    // return true if we've been interrupted and are supposed to stop
    virtual bool is_interrupted() { return false; };

    // tell an async fractal to stop calculating
    virtual void interrupt() { };

    // set things up before starting a new calc thread
    virtual void start(calc_args *params) {};

    // having started it, set the thread id of the calc thread to wait for
    virtual void set_tid(pthread_t tid) {};

    // wait for it to finish
    virtual void wait() {};
};


#endif /* _FRACT_PUBLIC_H_ */
