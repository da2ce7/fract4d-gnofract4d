#ifndef FRACT_STDLIB_H_
#define FRACT_STDLIB_H_

#ifdef __cplusplus
extern "C" {
#endif

    void fract_rand(double *re, double *im);

    void *alloc_array1D(int element_size, int size);
    void *alloc_array2D(int element_size, int xsize, int ysize);
    void *alloc_array3D(int element_size, int xsize, int ysize, int zsize);
    void *alloc_array4D(int element_size, int xsize, int ysize, int zsize, int wsize);

    int read_int_array_1D(void *array, int x);

#ifdef __cplusplus
}
#endif

#endif
