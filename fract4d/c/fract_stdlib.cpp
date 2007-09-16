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
    void *prev; // an allocation_t
} allocation_t;

// an arena
struct s_arena {
    int free_slots;
    int page_size;
    int pages_left;
    allocation_t *prev_arena;
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

void *alloc_array1D(arena_t arena, int element_size, int size)
{
    return arena_alloc(arena, element_size, 1, &size);
}

void *alloc_array2D(arena_t arena, int element_size, int xsize, int ysize)
{
    return NULL;
}

void *alloc_array3D(arena_t arena, int element_size, int xsize, int ysize, int zsize)
{
    return NULL;
}

void *alloc_array4D(arena_t arena, int element_size, int xsize, int ysize, int zsize, int wsize)
{
    return NULL;
}

int read_int_array_1D(void *array, int x)
{

    int retval;
    int inbounds = 0;
    array_get_int(array, 1, &x, &retval, &inbounds);

    return retval;
}

int write_int_array_1D(void *array, int i, int val)
{
    return array_set_int(array, 1, &i, val);
}

bool
arena_add_page(arena_t arena)
{
    if(arena->pages_left <= 0)
    {
	return false;
    }

    allocation_t *newalloc = new(std::nothrow) allocation_t[arena->page_size+1];
    if(NULL == newalloc)
    {
	return false;
    }

    // first slot holds a pointer to previous page
    newalloc[0].prev = arena->base_allocation;
    
    for(int i = 1; i < arena->page_size+1; ++i)
    {
	newalloc[i].d = 0.0;
    }
    
    arena->pages_left--;
    arena->base_allocation = newalloc;
    arena->free_slots = arena->page_size;
    arena->next_allocation = &(arena->base_allocation[1]);

#ifdef DEBUG_ALLOCATION
    fprintf(stderr,"%p: ARENA PAGE : CTOR\n", newalloc);
#endif

    return true;
}

arena_t 
arena_create(int page_size, int max_pages)
{
    if(page_size <= 0 || max_pages <= 0)
    {
	return NULL;
    }
    arena_t arena = (arena_t)new(std::nothrow) struct s_arena();

    if(NULL == arena)
    {
	return NULL;
    }

    arena->free_slots = 0;
    arena->pages_left = max_pages;    
    arena->page_size = page_size;
    arena->base_allocation = NULL;

#ifdef DEBUG_ALLOCATION
    fprintf(stderr,"%p: ARENA : CTOR(%d,%d)\n", arena, page_size, max_pages);
#endif
    return arena;
}

void *
arena_alloc(
    arena_t arena, int element_size, 
    int n_dimensions,
    int *n_elements)
{
    if(n_dimensions <= 0)
    {
	return NULL;
    }

    if(NULL == n_elements)
    {
	return NULL;
    }

    int total_elements = 1;
    for(int i = 0; i < n_dimensions; ++i)
    {
	total_elements *= n_elements[i];
    }

    // add 1 per dimension for size record
    int slots_required = \
	std::max(total_elements * element_size/sizeof(allocation_t),
		 (unsigned long)1) + n_dimensions;

    if(slots_required > arena->page_size)
    {
	// we can never allocate this
	return NULL;
    }

    if(arena->free_slots < slots_required)
    {
	//try to make a new page
	if(! arena_add_page(arena))
	{
	    return NULL;
	}
    }

    allocation_t *newchunk = (allocation_t *)arena->next_allocation;
    for(int i = 0; i < n_dimensions; ++i)
    {
	newchunk[i].i = n_elements[i];
    }
    arena->next_allocation+= slots_required;
    arena->free_slots -= slots_required;

#ifdef DEBUG_ALLOCATION
    fprintf(stderr,"%p: ALLOC : (req=%d,esize=%d,nelem=%d)\n", 
	   newchunk, slots_required, element_size, total_elements);

#endif
    return newchunk;
}

static void
arena_delete_page(allocation_t *alloc)
{
    if(NULL != alloc[0].prev)
    {
	// recursively delete previous page
	arena_delete_page((allocation_t *)alloc[0].prev);
    }
#ifdef DEBUG_ALLOCATION
    fprintf(stderr,"%p: ARENA PAGE : DTOR\n", alloc);
#endif
    delete[] alloc;
}

void 
arena_delete(arena_t arena)
{
    if(NULL != arena->base_allocation)
    {
	arena_delete_page(arena->base_allocation);
    }
    
    delete arena;

#ifdef DEBUG_ALLOCATION
    fprintf(stderr,"%p: ARENA : DTOR()\n", arena);
#endif
}

void 
array_get_int(
    void *vallocation, int n_dimensions, 
    int *indexes, int *pRetVal, int *pInBounds)
{
    allocation_t *allocation = (allocation_t *)vallocation;
    int pos = 1;
    int lastdim = 1;
    for(int i = 0; i < n_dimensions; ++i)
    {
	int index = indexes[i];
	int dim = allocation[i].i;

	if(index < 0 || index >= dim)
	{
	    // out of bounds
	    *pRetVal = -1;
	    *pInBounds = 0;
	    return;
	}
	pos = (pos * lastdim) + index;
	lastdim = dim;
    }
    int *array = (int *)(&allocation[n_dimensions]);
    *pRetVal = array[pos];
    *pInBounds = 1;
}

int
array_set_int(void *vallocation, int n_dimensions, int *indexes, int val)
{
    allocation_t *allocation = (allocation_t *)vallocation;

    int pos = 1;
    int lastdim = 1;
    for(int i = 0; i < n_dimensions; ++i)
    {
	int index = indexes[i];
	int dim = allocation[i].i;

	if(index < 0 || index >= dim)
	{
	    // out of bounds
	    return 0;
	}
	pos = (pos * lastdim) + index;
	lastdim = dim;
    }

    int *array = (int *)(&allocation[n_dimensions]);
    array[pos] = val;
    return 1;
}
