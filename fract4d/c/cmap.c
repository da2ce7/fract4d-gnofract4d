/* a cmap is a mapping from double [0.0,1.0] (#index) -> color */

#include "cmap.h"

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>

typedef struct 
{
    double index;
    rgba_t color;
} item_t;

struct s_cmap
{
    int ncolors;
    item_t *items;
    rgba_t solids[2];
    e_transferType transfers[2];
};

rgba_t black = {0,0,0,255};

cmap_t *
cmap_new(int ncolors)
{
    cmap_t *cmap = NULL;
    int i =0;

    if(ncolors == 0)
    {
	goto cleanup;
    }

    cmap = malloc(sizeof(cmap_t));
    if(!cmap) 
    {  
	goto cleanup;
    }

    cmap->ncolors = ncolors; cmap->items = NULL; 
    cmap->solids[0] = cmap->solids[1] = black;
    cmap->transfers[0] = TRANSFER_LINEAR; // outer
    cmap->transfers[1] = TRANSFER_LINEAR; // inner

    cmap->items = (item_t *)malloc(sizeof(item_t) * ncolors);
    if(!cmap->items) goto cleanup;

    for(i = 0; i < ncolors; ++i)
    {
	cmap->items[i].color = black;
	cmap->items[i].index = 0;
    }
    return cmap;
 cleanup:
    if(cmap)
    {
	free(cmap->items);
    }
    free(cmap);
    return NULL;
}

void 
cmap_set(cmap_t *cmap, int i, double d, int r, int g, int b, int a)
{
    assert(NULL != cmap);

    rgba_t color;
    color.r = (unsigned char)r;
    color.g = (unsigned char)g;
    color.b = (unsigned char)b;
    color.a = (unsigned char)a;

    cmap->items[i].color = color;
    cmap->items[i].index = d;
} 

void 
cmap_set_transfer(cmap_t *cmap, int which, e_transferType type)
{
    assert(NULL != cmap);

    if(which >= 0 && which < 2)
    {
	if(type < TRANSFER_SIZE && type >= 0)
	{
	    cmap->transfers[which] = type;
	}
	else
	{
	    assert("bad transfer type" && 0);
	}
    }
    else
    {
	assert("bad transfer index" && 0);
    }
}

void
cmap_set_solid(cmap_t *cmap, int which, int r, int g, int b, int a)
{
    assert(NULL != cmap);

    rgba_t color;
    color.r = (unsigned char)r;
    color.g = (unsigned char)g;
    color.b = (unsigned char)b;
    color.a = (unsigned char)a;

    if(which >= 0 && which < 2)
    {
	cmap->solids[which] = color;
    }
    else
    {
	assert("set bad color" && 0);
    }
}

rgba_t 
cmap_get_solid(cmap_t *cmap, int which)
{
    assert(NULL != cmap);

    rgba_t color = {0,0,0,1};
    if(which >= 0 && which < 2)
    {
	color = cmap->solids[which];
    }
    else
    {
	assert("get bad color" && 0);
    }
    return color;
} 

void 
cmap_delete(cmap_t *cmap)
{
    if(cmap)
    {
	free(cmap->items);
    }
    free(cmap);
}

/* finds the indices in t of the largest item which is <= key 
   and the next item above it.
   If there are multiple identical items, returns one at random
 */

/* binary search algorithm from Programming Pearls.
   sadly C stdlib's bsearch is no good because it won't tell us the position
   of nearest match if there's no exact one */

int 
find(double key, item_t *array, int n)
{
    int left=0,right=n-1;
    do
    {
	int middle;
	if(left > right)
	{
	    return left-1 < 0 ? 0 : left-1 ;
	}
	middle = (left + right) / 2;
	if(array[middle].index < key)
	{ 
	    left = middle+1;
	}
	else if(array[middle].index == key)
	{
	    return middle;
	}
	else
	{
	    right = middle-1;
	}
    }while(1);
}

rgba_t 
cmap_lookup_with_transfer(cmap_t *cmap, int fate, double index, int solid)
{
    assert(NULL != cmap);

    if(fate >= 0 && fate < 2)
    {
	if(solid)
	{
	    return cmap->solids[fate];
	}

	e_transferType t = cmap->transfers[fate];
	switch(t)
	{
	case TRANSFER_NONE:
	    return cmap->solids[fate];
	case TRANSFER_LINEAR:
	    return cmap_lookup(cmap,index);
	default:
	    assert("bad transfer type" && 0);
	    return black;
	}
    }
    else
    {

	assert("bad fate" && 0);
	return black;
    }
}
 
rgba_t 
cmap_lookup(cmap_t *cmap, double index)
{
    int i,j;
    rgba_t mix, left, right;
    double dist, r;

    index = index == 1.0 ? 1.0 : fmod(index,1.0);
    i = find(index, cmap->items, cmap->ncolors); 
    assert(i >= 0 && i < cmap->ncolors);

    /* printf("%g->%d\n",index,i); */
    if(index <= cmap->items[i].index || i == cmap->ncolors-1) 
    {
	return cmap->items[i].color;
    }

    j = i+1;

    /* mix colors i & j in proportion to the distance between them */
    dist = cmap->items[j].index - cmap->items[i].index;

    /* printf("dist: %g\n",dist); */
    if(dist == 0.0)
    {
	return cmap->items[i].color;
    }
    
    r = (index - cmap->items[i].index)/dist;
    /* printf("r:%g\n",r); */

    left = cmap->items[i].color;
    right = cmap->items[j].color;

    mix.r = (unsigned char)((left.r * (1.0-r) + right.r * r));
    mix.g = (unsigned char)((left.g * (1.0-r) + right.g * r));
    mix.b = (unsigned char)((left.b * (1.0-r) + right.b * r));
    mix.a = (unsigned char)((left.a * (1.0-r) + right.a * r));

    return mix;
}

