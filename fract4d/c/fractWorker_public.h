#ifndef FRACT_WORKER_PUBLIC_H_
#define FRACT_WORKER_PUBLIC_H_

class fractFunc;
class IImage;

#include "vectors.h" 
#include "pf.h"
#include "cmap.h"

class IFractalSite;

typedef enum
{
    DEEPEN_STATS,
    TOLERANCE_STATS
} stat_type_t;

typedef struct s_pixel_stat pixel_stat_t;

struct s_pixel_stat{
    // n pixels correctly classified that would be wrong 
    // if we calculated less carefully
    int nworsepixels;
    // n pixels currenty misclassified that would be correct 
    // if we doubled the iterations
    int nbetterpixels; 
    int k;	// number of pixels calculated    
    s_pixel_stat() {
	reset();
    };
    void reset() {
	nworsepixels=0;
	nbetterpixels=0;
	k=0;
    };
    void add(const pixel_stat_t& other) {
	nworsepixels += other.nworsepixels;
	nbetterpixels += other.nbetterpixels;
	k += other.k;
    };

};

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
    virtual pixel_stat_t stats(stat_type_t type) =0;

    // ray-tracing machinery
    virtual bool find_root(const dvec4& eye, const dvec4& look, dvec4& root) = 0;

    virtual ~IFractWorker() {};

    virtual void flush() = 0;
    virtual bool ok() = 0;
};

#endif /* FRACT_WORKER_PUBLIC_H_ */
