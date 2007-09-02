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


