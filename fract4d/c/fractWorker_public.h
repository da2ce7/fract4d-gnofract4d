#ifndef FRACT_WORKER_PUBLIC_H_
#define FRACT_WORKER_PUBLIC_H_

class fractFunc;
class IImage;

#include "pf.h"
#include "cmap.h"

class IFractalSite;

class IFractWorker {
public:

    static IFractWorker *create(
	int nThreads,pf_obj *pfo, ColorMap *cmap, IImage *im_, IFractalSite *site);

    virtual void set_fractFunc(fractFunc *ff_) =0;

    // calculate a row of antialiased pixels
    virtual void row_aa(int x, int y, int n) =0;

    // calculate a row of pixels
    virtual void row(int x, int y, int n) =0;

    // calculate an rsize-by-rsize box of pixels
    virtual void box(int x, int y, int rsize) =0;

    // calculate a row of boxes
    virtual void box_row(int w, int y, int rsize) =0;

    // calculate a single pixel
    virtual void pixel(int x, int y, int w, int h) =0;

    // calculate a single pixel in aa-mode
    virtual void pixel_aa(int x, int y) =0;

    // auto-deepening record keeping
    virtual void reset_counts() =0;
    virtual void stats(int *pnDoubleIters, int *pnHalfIters, int *pk) =0;

    virtual ~IFractWorker() {};

    virtual void flush() = 0;
    virtual bool ok() = 0;
};

#endif /* FRACT_WORKER_PUBLIC_H_ */
