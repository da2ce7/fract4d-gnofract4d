#ifndef _FRACT_PUBLIC_H_
#define _FRACT_PUBLIC_H_

// current state of calculation
enum {
    GF4D_FRACTAL_DONE,
    GF4D_FRACTAL_CALCULATING,
    GF4D_FRACTAL_DEEPENING,
    GF4D_FRACTAL_ANTIALIASING
};

typedef enum {
    AA_NONE = 0,
    AA_FAST,
    AA_BEST
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

#define N_PARAMS 12

#define SECTION_STOP "[endsection]"

typedef struct fractal fractal_t;
typedef struct image image_t;

#endif /* _FRACT_PUBLIC_H_ */
