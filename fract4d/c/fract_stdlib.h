
#ifndef FRACT_STDLIB_H_
#define FRACT_STDLIB_H_

#ifdef __cplusplus
extern "C" {
#endif

    void fract_rand(double *re, double *im);

    typedef struct s_arena *arena_t;
    arena_t arena_create(int page_size, int max_pages);
    void *arena_alloc(arena_t arena, int element_size, int n_elements);
    void arena_delete(arena_t arena);

    void array_get_int(void *allocation, int i, int *pRetVal, int *pInBounds);
    int array_set_int(void *allocation, int i, int val);

    void *alloc_array1D(arena_t arena, int element_size, int size);
    void *alloc_array2D(arena_t arena, int element_size, int xsize, int ysize);
    void *alloc_array3D(arena_t arena, int element_size, int xsize, int ysize, int zsize);
    void *alloc_array4D(arena_t arena, int element_size, int xsize, int ysize, int zsize, int wsize);

    int read_int_array_1D(void *array, int x);
    int write_int_array_1D(void *array, int i, int val);

#ifdef __cplusplus
}
#endif

#endif
