/* a cmap is a mapping from double [0.0,1.0] (#index) -> color */

#include "cmap.h"

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>

#include <new>

rgba_t black = {0,0,0,255};

#define EPSILON 1.0e-10

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
    items = NULL;
}

GradientColorMap::~GradientColorMap()
{
    delete[] items;
}

bool
GradientColorMap::init(int ncolors_)
{
    if(ncolors_ == 0)
    {
	return false;
    }

    ncolors = ncolors_; 

    items = new(std::nothrow) gradient_item_t[ncolors];
    if(!items)
    {
	return false;
    }

    for(int i = 0; i < ncolors; ++i)
    {
	gradient_item_t *p = &items[i];
	p->left = p->right = 0;
	p->bmode = BLEND_LINEAR;
	p->cmode = RGB;
    }
    return true;
}

void 
GradientColorMap::set(
    int i,
    double left, double right, double mid,
    double *left_col,
    double *right_col,
    e_blendType bmode, e_colorType cmode)
{
    items[i].left = left;
    items[i].right = right;
    items[i].mid = mid;
    for(int j = 0; j < 4 ; ++j)
    {
	items[i].left_color[j] = left_col[j];
	items[i].right_color[j] = right_col[j];
    }
    items[i].bmode = bmode;
    items[i].cmode = cmode;
	
/*
    printf("left: %g [%g,%g,%g,%g]\nright: %g [%g,%g,%g,%g]\n%d %d\n",
	   left, left_col[0], left_col[1], left_col[2], left_col[3],
	   right, right_col[0], right_col[1], right_col[2], right_col[3], 
	   (int)bmode, (int)cmode);
*/

}

int 
grad_find(double index, gradient_item_t *items, int ncolors)
{
    for(int i = 0; i < ncolors; ++i)
    {
	if(index < items[i].right)
	{
	    return i;
	} 
    }
    assert(0 && "Didn't find an entry");
    return -1;
}

static double
calc_linear_factor (double middle, double pos)
{
  if (pos <= middle)
    {
      if (middle < EPSILON)
	return 0.0;
      else
	return 0.5 * pos / middle;
    }
  else
    {
      pos -= middle;
      middle = 1.0 - middle;

      if (middle < EPSILON)
	return 1.0;
      else
	return 0.5 + 0.5 * pos / middle;
    }
}

static double
calc_curved_factor (double middle,double pos)
{
  if (middle < EPSILON)
    middle = EPSILON;

  return pow (pos, log (0.5) / log (middle));
}

static double
calc_sine_factor (double middle, double pos)
{
    pos = calc_linear_factor (middle, pos);
    return (sin ((-M_PI / 2.0) + M_PI * pos) + 1.0) / 2.0;
}

static double
calc_sphere_increasing_factor (double middle,
			       double pos)
{
    pos = calc_linear_factor (middle, pos) - 1.0;
    return sqrt (1.0 - pos * pos); 
}

static double
calc_sphere_decreasing_factor (double middle,
			       double pos)
{
    pos = calc_linear_factor (middle, pos);
    return 1.0 - sqrt(1.0 - pos * pos);
}

rgba_t 
GradientColorMap::lookup(double index) const
{
    index = index == 1.0 ? 1.0 : fmod(index,1.0);
    int i = grad_find(index, items, ncolors); 
    assert(i >= 0 && i < ncolors);

    gradient_item_t *seg = &items[i];

    double seg_len = seg->right - seg->left;
    
    double middle;
    double pos;
    if (seg_len < EPSILON)
    {
	middle = 0.5;
	pos    = 0.5;
    }
    else
    {
	middle = (seg->mid - seg->left) / seg_len;
	pos    = (pos - seg->left) / seg_len;
    }
    
    double factor;
    switch (seg->bmode)
    {
    case BLEND_LINEAR:
	factor = calc_linear_factor (middle, pos);
	break;
    
    case BLEND_CURVED:
	factor = calc_curved_factor (middle, pos);
	break;
      
    case BLEND_SINE:
	factor = calc_sine_factor (middle, pos);
	break;
    
    case BLEND_SPHERE_INCREASING:
	factor = calc_sphere_increasing_factor (middle, pos);
	break;
    
    case BLEND_SPHERE_DECREASING:
	factor = calc_sphere_decreasing_factor (middle, pos);
	break;
    
    default:
	assert(0 && "Unknown gradient type");
	return black;
    }


    /* Calculate color components */
    rgba_t result;
    double *lc = seg->left_color;
    double *rc = seg->right_color;
    if (seg->cmode == RGB)
    {
	result.r = (unsigned char)(255.0 * (lc[0] + (rc[0] - lc[0]) * factor));
	result.g = (unsigned char)(255.0 * (lc[1] + (rc[1] - lc[1]) * factor));
	result.b = (unsigned char)(255.0 * (lc[2] + (rc[2] - lc[2]) * factor));
    }
    else
    {
	/*
	GimpHSV left_hsv;
	GimpHSV right_hsv;

	gimp_rgb_to_hsv (&seg->left_color,  &left_hsv);
	gimp_rgb_to_hsv (&seg->right_color, &right_hsv);

	left_hsv.s = left_hsv.s + (right_hsv.s - left_hsv.s) * factor;
	left_hsv.v = left_hsv.v + (right_hsv.v - left_hsv.v) * factor;

	switch (seg->color)
	{
	case GIMP_GRADIENT_SEGMENT_HSV_CCW:
	    if (left_hsv.h < right_hsv.h)
	    {
		left_hsv.h += (right_hsv.h - left_hsv.h) * factor;
	    }
	    else
	    {
		left_hsv.h += (1.0 - (left_hsv.h - right_hsv.h)) * factor;

		if (left_hsv.h > 1.0)
		    left_hsv.h -= 1.0;
	    }
	    break;

	case GIMP_GRADIENT_SEGMENT_HSV_CW:
	    if (right_hsv.h < left_hsv.h)
	    {
		left_hsv.h -= (left_hsv.h - right_hsv.h) * factor;
	    }
	    else
	    {
		left_hsv.h -= (1.0 - (right_hsv.h - left_hsv.h)) * factor;

		if (left_hsv.h < 0.0)
		    left_hsv.h += 1.0;
	    }
	    break;

	default:
	    g_warning ("%s: Unknown coloring mode %d",
		       G_STRFUNC, (gint) seg->color);
	    break;
	}

	gimp_hsv_to_rgb (&left_hsv, &rgb);
	*/
	result = black;
    }

    /* Calculate alpha */
    result.a = (unsigned char)(255.0 * (lc[3] + (rc[3] - lc[3]) * factor));
    return result;
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
	return false;
    }

    ncolors = ncolors_; 

    items = new(std::nothrow) list_item_t[ncolors];
    if(!items)
    {
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

