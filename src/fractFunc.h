#ifndef _FRACTFUNC_H_
#define _FRACTFUNC_H_

// opaque declaration
typedef struct _Gf4dFractal Gf4dFractal;

#include "fract_callbacks.h"
#include "fract.h"
#include "image.h"
#include "colorizer.h"

/* this contains stuff which is useful for drawing the fractal,
   but can be recalculated at will, so isn't part of the fractal's
   persistent state. We create a new one each time we start drawing */

class fractFunc {
 public:
    fractFunc(fractal_t *_f, image *_im, Gf4dFractal *_gf);
    ~fractFunc() {
        delete pf;
    }
    void draw(int rsize, int drawsize);
    void draw_aa();
    bool updateiters();

 private:
    // MEMBER VARS

    // do every nth pixel twice as deep as the others to
    // see if we need to auto-deepen
    enum { AUTO_DEEPEN_FREQUENCY = 30 };

    // for callbacks
    Gf4dFractal *gf;

    dmat4 rot; // scaled rotation matrix
    dvec4 deltax, deltay; // step from 1 pixel to the next in x,y directions
    dvec4 delta_aa_x, delta_aa_y; // offset between subpixels
    dvec4 topleft; // top left corner of screen
    dvec4 aa_topleft; // topleft - offset to 1st subpixel to draw

    int depth;    // antialias depth
    d ddepth;     // double version of antialias depth

    // n pixels correctly classified that would be wrong 
    // if we halved iterations
    int nhalfiters;
    // n pixels misclassified that would be correct 
    // if we doubled the iterations
    int ndoubleiters; 
    // last time we redrew the image to this line
    int last_update_y; 
    int k;	// number of pixels calculated    

    fractal_t *f; // pointer to fract passed in to ctor
    image *im;    // pointer to image passed in to ctor
    pointFunc *pf; // function for calculating 1 point
    
    // MEMBER FUNCTIONS

    // calculate a single pixel
    void pixel(int x, int y, int h, int w);
    // calculate a single pixel in aa-mode
    void pixel_aa(int x, int y);

    // calculate a row of pixels
    void row(int x, int y, int n);
    
    // redraw the image to this line
    void update_image(int i);
    // clear auto-deepen and last_update
    void reset_counts();

    // draw a rectangle of this colour
    void rectangle(struct rgb pixel, int x, int y, int w, int h);

    // calculate this point using antialiasing
    struct rgb antialias(const dvec4& pos);

    void soi(); // broken

    // make an int corresponding to an RGB triple
    inline int RGB2INT(int y, int x);

    // does the point at (x,y) have the same colour & iteration count
    // as the target?
    inline bool isTheSame(bool bFlat, int targetIter, int targetCol, int x, int y);
};

#endif /* _FRACTFUNC_H_ */
