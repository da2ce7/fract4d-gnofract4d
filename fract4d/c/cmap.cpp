/* a cmap is a mapping from double [0.0,1.0] (#index) -> color */

#include "cmap.h"

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>

#include <new>

rgba_t black = {0,0,0,255};

ColorMap::ColorMap()
{
    ncolors = 0;
    solids[0] = solids[1] = black;
    transfers[0] = TRANSFER_LINEAR; // outer
    transfers[1] = TRANSFER_LINEAR; // inner
}

void 
ColorMap::set_transfer(int which, e_transferType type)
{
    if(which >= 0 && which < 2)
    {
	if(type < TRANSFER_SIZE && type >= 0)
	{
	    transfers[which] = type;
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
ColorMap::set_solid(int which, int r, int g, int b, int a)
{
    rgba_t color;
    color.r = (unsigned char)r;
    color.g = (unsigned char)g;
    color.b = (unsigned char)b;
    color.a = (unsigned char)a;

    if(which >= 0 && which < 2)
    {
	solids[which] = color;
    }
    else
    {
	assert("set bad color" && 0);
    }
}

rgba_t 
ColorMap::get_solid(int which) const
{
    rgba_t color = {0,0,0,1};
    if(which >= 0 && which < 2)
    {
	color = solids[which];
    }
    else
    {
	assert("get bad color" && 0);
    }
    return color;
} 

void
cmap_delete(ColorMap *cmap)
{
    delete cmap;
}

ColorMap::~ColorMap()
{ 
    // NO OP
}

/* finds the indices in t of the largest item which is <= key 
   and the next item above it.
   If there are multiple identical items, returns one at random
 */

/* binary search algorithm from Programming Pearls.
   sadly C stdlib's bsearch is no good because it won't tell us the position
   of nearest match if there's no exact one */

int 
find(double key, list_item_t *array, int n)
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
ColorMap::lookup_with_transfer(int fate, double index, int solid) const
{
    if(fate >= 0 && fate < 2)
    {
	if(solid)
	{
	    return solids[fate];
	}

	e_transferType t = transfers[fate];
	switch(t)
	{
	case TRANSFER_NONE:
	    return solids[fate];
	case TRANSFER_LINEAR:
	    return lookup(index);
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
 
GradientColorMap::GradientColorMap() : ColorMap()
{
    //items = NULL;
}

GradientColorMap::~GradientColorMap()
{
    // NO OP
}

ListColorMap::ListColorMap() : ColorMap()
{
    items = NULL;
}

ListColorMap::~ListColorMap()
{
    delete[] items;
}

bool
ListColorMap::init(int ncolors_)
{
    if(ncolors_ == 0)
    {
	printf("No colors\n");
	return false;
    }

    ncolors = ncolors_; 

    items = new(std::nothrow) list_item_t[ncolors];
    if(!items)
    {
	printf("No color alloc\n");
	return false;
    }

    for(int i = 0; i < ncolors; ++i)
    {
	items[i].color = black;
	items[i].index = 0;
    }
    return true;
}

void 
ListColorMap::set(int i, double d, int r, int g, int b, int a)
{
    rgba_t color;
    color.r = (unsigned char)r;
    color.g = (unsigned char)g;
    color.b = (unsigned char)b;
    color.a = (unsigned char)a;

    items[i].color = color;
    items[i].index = d;
} 

rgba_t 
ListColorMap::lookup(double index) const
{
    int i,j;
    rgba_t mix, left, right;
    double dist, r;

    index = index == 1.0 ? 1.0 : fmod(index,1.0);
    i = find(index, items, ncolors); 
    assert(i >= 0 && i < ncolors);

    /* printf("%g->%d\n",index,i); */
    if(index <= items[i].index || i == ncolors-1) 
    {
	return items[i].color;
    }

    j = i+1;

    /* mix colors i & j in proportion to the distance between them */
    dist = items[j].index - items[i].index;

    /* printf("dist: %g\n",dist); */
    if(dist == 0.0)
    {
	return items[i].color;
    }
    
    r = (index - items[i].index)/dist;
    /* printf("r:%g\n",r); */

    left = items[i].color;
    right = items[j].color;

    mix.r = (unsigned char)((left.r * (1.0-r) + right.r * r));
    mix.g = (unsigned char)((left.g * (1.0-r) + right.g * r));
    mix.b = (unsigned char)((left.b * (1.0-r) + right.b * r));
    mix.a = (unsigned char)((left.a * (1.0-r) + right.a * r));

    return mix;
}
