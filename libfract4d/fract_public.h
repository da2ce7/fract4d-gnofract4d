#ifndef _FRACT_PUBLIC_H_
#define _FRACT_PUBLIC_H_

// current state of calculation
enum {
    GF4D_FRACTAL_DONE,
    GF4D_FRACTAL_CALCULATING,
    GF4D_FRACTAL_DEEPENING,
    GF4D_FRACTAL_ANTIALIASING,
    GF4D_FRACTAL_PAUSED,
    GF4D_FRACTAL_COMPILING
};

typedef enum {
    AA_NONE = 0,
    AA_FAST,
    AA_BEST,
    AA_DEFAULT /* used only for effective_aa - means use aa from fractal */
} e_antialias;

typedef enum {
    BAILOUT,
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

// colorFunc indices
#define OUTER 0
#define INNER 1
#define N_COLORFUNCS 2

#define N_PARAMS 12

typedef struct fractal fractal_t;
typedef struct image image_t;
//class colorizer;
typedef class colorizer colorizer_t;
typedef struct _Gf4dFractal Gf4dFractal;
typedef struct s_fract_callbacks fract_callbacks;

class iterFunc;

#include "pointFunc_public.h"

class IFractal
{
public:
    // factory method in lieu of ctor
    static IFractal *create();
    // equivalent to copy ctor
    static IFractal *clone(const IFractal *f); 


    virtual IFractal& operator=(const IFractal& f) =0; // assignment op
    virtual bool operator==(const IFractal& f) =0; // equality 

    virtual ~IFractal();


    // make this fractal like f but weirder
    virtual void set_inexact(const IFractal& f, double weirdness) = 0; 
    // make this fractal into a mixture of f1 and f2, 
    // in the proportion lambda of f1 : 1-lambda of f2
    virtual void set_mixed(const IFractal& f1, const IFractal& f2, double lambda) = 0;

    virtual void reset() = 0;
    virtual void calc(Gf4dFractal *gf4d, image *im, fract_callbacks *fcb) = 0;

    virtual void recolor(image *im) = 0;
    virtual void relocate(double x, double y, double zoom) = 0;
    virtual void flip2julia(double x, double y) = 0;
    virtual void move(param_t i, double distance) = 0;

    virtual bool write_params(const char *filename) = 0;
    virtual bool load_params(const char *filename) = 0;

    // accessors
    // FIXME: make this pair consistent
    // change the function type
    virtual void set_fractal_type(const char *type) = 0;
    // get fractal type
    virtual iterFunc *get_iterFunc() const = 0;
    virtual void set_iterFunc(iterFunc *) = 0;

    virtual bool set_param(param_t i, const char *val) = 0;
    virtual char *get_param(param_t i) const = 0;

    virtual void set_max_iterations(int val) = 0;
    virtual int get_max_iterations() const = 0;

    virtual void set_aa(e_antialias val) = 0;
    virtual e_antialias get_aa() const = 0;

    virtual void set_effective_aa(e_antialias val) = 0;
    virtual e_antialias get_effective_aa() const = 0;

    virtual void set_auto(bool val) = 0;
    virtual bool get_auto() const = 0;

    virtual bool set_precision(int digits) = 0; 
    virtual bool check_precision() = 0;

    virtual void set_bailFunc(e_bailFunc bf) = 0;
    virtual e_bailFunc get_bailFunc() const = 0;

    virtual void set_colorFunc(e_colorFunc cf, int which_cf) = 0;
    virtual e_colorFunc get_colorFunc(int which_cf) const = 0;

    virtual void set_threads(int n) = 0;
    virtual int get_threads() const = 0;

    // color functions
    virtual colorizer_t *get_colorizer() const = 0;
    virtual void set_colorizer(colorizer_t *cizer) = 0;
};

#endif /* _FRACT_PUBLIC_H_ */
