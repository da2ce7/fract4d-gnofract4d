#include "fract_stdlib.h"

#include "math.h"
#include "stdlib.h"

#include <new>
#include <algorithm>

// These functions are called by the compiled formulas

// random number generation
// Code adapted from Fractint. 
// I'm a bit suspicious of the RNG here, but compatibility is God.

#define rand15() (rand() & 0x7FFF)

static unsigned long RandNum; // FIXME: not thread-safe

unsigned long NewRandNum(void)
{
   return(RandNum = ((RandNum << 15) + rand15()) ^ RandNum);
}

void fract_rand(double *re, double *im)
{
   long x, y;

   /* Use the same algorithm as for fixed math so that they will generate
	  the same fractals when the srand() function is used. */
   // FIXME :can't (be bothered to) work out how Fractint sets the bitshift, so hard-coding 29
#define bitshift 29

   x = NewRandNum() >> (32 - bitshift);
   y = NewRandNum() >> (32 - bitshift);
   *re = ((double)x / (1L << bitshift));
   *im = ((double)y / (1L << bitshift));
    
}

// end of copied code

// allocation and accessor functions used for arrays

// the union of all the C types we'll ever allocate
// this ensures that we have the strictest alignment 
// we need (sometimes stricter than was actually required)
typedef union {
    int i;
    double d;
} allocation_t;

// an arena
struct s_arena {
    arena_t prev_arena;
    int free_slots;
    allocation_t *base_allocation;
    allocation_t *next_allocation;
};

typedef struct {
    union {
	int length;
	double packing_space; // to ensure double-aligned
    } header;
    union {
	int i;
	double d;
    } first_element;
} allocation;

void *alloc_array1D(int element_size, int size)
{
    return NULL;
}

void *alloc_array2D(int element_size, int xsize, int ysize)
{
    return NULL;
}

void *alloc_array3D(int element_size, int xsize, int ysize, int zsize)
{
    return NULL;
}

void *alloc_array4D(int element_size, int xsize, int ysize, int zsize, int wsize)
{
    return NULL;
}

int read_int_array_1D(void *array, int x)
{
    return 0;
}

arena_t 
arena_create(int size)
{
    if(size <= 0)
    {
	return NULL;
    }
    arena_t arena = (arena_t)new(std::nothrow) struct s_arena();

    if(NULL == arena)
    {
	return NULL;
    }

    arena->base_allocation = new(std::nothrow) allocation_t[size];
    if(NULL == arena->base_allocation)
    {
	delete arena;
	return NULL;
    }
    for(int i = 0; i < size; ++i)
    {
	arena->base_allocation[i].d = 0.0;
    }

    arena->next_allocation = arena->base_allocation;
    arena->free_slots = size;

#ifdef DEBUG_ALLOCATION
    printf("%p: ARENA : CTOR(%d)\n", arena, size);
#endif
    return arena;
}

void *
arena_alloc(arena_t arena, int element_size, int n_elements)
{
    // add 1 for size record
    int slots_required = \
	std::max(n_elements * element_size/sizeof(allocation_t),
		 (unsigned long)1) + 1;

    if(arena->free_slots < slots_required)
    {
	return NULL;
    }
    allocation_t *newchunk = (allocation_t *)arena->next_allocation;
    newchunk[0].i = n_elements;
    arena->next_allocation+= slots_required;
    arena->free_slots -= slots_required;

#ifdef DEBUG_ALLOCATION
    printf("%p: ALLOC : (req=%d,esize=%d,nelem=%d)\n", 
	   newchunk, slots_required, element_size, n_elements);

#endif
    return newchunk;
}

void 
arena_delete(arena_t arena)
{
    delete[] arena->base_allocation;
    delete arena;
}

void 
array_get_int(void *vallocation, int i, int *pRetVal, int *pInBounds)
{
    allocation_t *allocation = (allocation_t *)vallocation;
    if(i < 0 || i >= allocation[0].i)
    {
	// out of bounds
	*pRetVal = -1;
	*pInBounds = 0;
	return;
    }

    int *array = (int *)(&allocation[1]);
    *pRetVal = array[i+1];
    *pInBounds = 1;
}
