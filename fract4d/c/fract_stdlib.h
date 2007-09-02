#ifndef FRACT_STDLIB_H_
#define FRACT_STDLIB_H_

#ifdef __cplusplus
extern "C" {
#endif

    void fract_rand(double *re, double *im);

    void *alloc_array(int size);

#ifdef __cplusplus
}
#endif

#endif
