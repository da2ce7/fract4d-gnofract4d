#ifndef _FRACT_PUBLIC_H_
#define _FRACT_PUBLIC_H_

enum {
    GF4D_FRACTAL_DONE,
    GF4D_FRACTAL_CALCULATING,
    GF4D_FRACTAL_DEEPENING,
    GF4D_FRACTAL_ANTIALIASING
};

typedef enum {
    BAILOUT,
    XCENTER,
    YCENTER,
    ZCENTER,
    WCENTER,
    SIZE,
    XYANGLE,
    XZANGLE,
    XWANGLE,
    YZANGLE,
    YWANGLE,
    ZWANGLE,
} param_t;

#define N_PARAMS 12

typedef struct fractal fractal_t;
typedef struct image image_t;

#endif /* _FRACT_PUBLIC_H_ */
