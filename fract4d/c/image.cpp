#include <stdlib.h>
#include <stdio.h>

#include <new>

#include "image.h"

#define RED 0
#define GREEN 1
#define BLUE 2

const int 
image::N_SUBPIXELS = 4;

#define MAX_RECOLOR_SIZE (1024*768)

image::image()
{
    m_Xres = m_Yres = 0;
    m_totalXres = m_totalYres = 0;
    m_xoffset = m_yoffset = 0;
    buffer = NULL;
    iter_buf = NULL;
    fate_buf = NULL;
    index_buf = NULL;
}

image::image(const image& im)
{
    m_Xres = im.m_Xres;
    m_Yres = im.m_Yres;
    m_totalXres = im.m_totalXres;
    m_totalYres = im.m_totalYres;
    m_xoffset = im.m_xoffset;
    m_yoffset = im.m_yoffset;
    alloc_buffers();
}

image::~image()
{
    delete_buffers();
}


void
image::delete_buffers()
{
    delete[] buffer;
    delete[] iter_buf;
    delete[] fate_buf;
    delete[] index_buf;
    buffer = NULL;
    iter_buf = NULL;
    fate_buf = NULL;
    index_buf = NULL;
}

bool
image::alloc_buffers()
{
    buffer = new(std::nothrow) char[bytes()];
    iter_buf = new(std::nothrow) int[m_Xres * m_Yres];
    // FIXME remove true 
    if(true || m_Xres * m_Yres <= MAX_RECOLOR_SIZE)
    {
	index_buf = new(std::nothrow) float[m_Xres * m_Yres * N_SUBPIXELS];
	fate_buf = new(std::nothrow) fate_t[m_Xres * m_Yres * N_SUBPIXELS];
	if(!index_buf || !fate_buf)
	{
	    delete_buffers();
	    return false;
	}
    }
    else
    {
	// use less memory for big images. Sadly not working yet
	index_buf = NULL;
	fate_buf = NULL;
    }
    if(!buffer || !iter_buf)
    {
	delete_buffers();
	return false;
    }

    clear();

    return true;
}

int
image::bytes() const
{
    return row_length() * m_Yres;
}

void 
image::put(int x, int y, rgba_t pixel)
{
    int off = x*3 + y * row_length();
    assert(off  + BLUE < bytes());
    char *start = buffer + off;
    start[RED] = pixel.r;
    start[GREEN] = pixel.g;
    start[BLUE] = pixel.b;
}

rgba_t 
image::get(int x, int y) const
{
    char *start = buffer + x*3 + y * row_length();
    assert(start  + 2 - buffer <= bytes());
    rgba_t pixel;
    pixel.r = start[RED];
    pixel.g = start[GREEN];
    pixel.b = start[BLUE];
    
    return pixel;
}

bool 
image::set_resolution(int x, int y, int totalx, int totaly)
{
    totalx = totalx == -1 ? x : totalx;
    totaly = totaly == -1 ? y : totaly;

    if(buffer && 
       m_Xres == x && m_Yres == y && 
       m_totalXres == totalx && m_totalYres == totaly) 
    {
	// nothing to do
	return false;
    }

    m_Xres = x;
    m_Yres = y;
    m_totalXres = totalx;
    m_totalYres = totaly;

    delete_buffers();

    if(! alloc_buffers())
    {
	return true;
    }

    rgba_t pixel = { 
	0,0,0,255 // soothing black
    };

    for(int i = 0; i < y; ++i)
    {
	for(int j = 0; j < x; ++j)
	{
	    put(j,i,pixel);
	}
    }

    return true;
}

bool
image::set_offset(int x, int y)
{
    if(x < 0 || x + m_Xres > m_totalXres || y < 0 || y + m_Yres > m_totalYres)
    {
	return false;
    }
    if(x == m_xoffset && y == m_yoffset)
    {
	// nothing to do, succeed already
	return true;
    }

    m_xoffset = x; m_yoffset = y;
    clear();
    return true;
}

double 
image::ratio() const
{
    return ((double)m_Yres / m_Xres);
}

void 
image::fill_subpixels(int x, int y)
{
    fate_t fate = getFate(x,y,0);
    float index = getIndex(x,y,0);
    for(int i = 1; i < N_SUBPIXELS; ++i)
    {
	setFate(x,y,i,fate);
	setIndex(x,y,i,index);
    }
}

void
image::clear_fate(int x, int y)
{
    if(!fate_buf) return;

    int base = index_of_subpixel(x,y,0);
    for(int i = base; i < base+ N_SUBPIXELS; ++i)
    {
	fate_buf[i] = FATE_UNKNOWN;

#ifndef NDEBUG
	// index is only meaningful if fate is known, but set this for
	// testing purposes
	index_buf[i] = 1e30;
#endif
    }
}

fate_t
image::getFate(int x, int y, int subpixel) const
{
    assert(fate_buf != NULL);
    return fate_buf[index_of_subpixel(x,y,subpixel)];
}

void 
image::setFate(int x, int y, int subpixel, fate_t fate)
{
    assert(fate_buf != NULL);
    int i = index_of_subpixel(x,y,subpixel);
    fate_buf[i] = fate;
}

float
image::getIndex(int x, int y, int subpixel) const
{
    assert(index_buf != NULL);
    return index_buf[index_of_subpixel(x,y,subpixel)];
}

void 
image::setIndex(int x, int y, int subpixel, float index)
{
    assert(index_buf != NULL);
    int i = index_of_subpixel(x,y,subpixel);
    index_buf[i] = index;
}

void 
image::clear()
{
    // no need to clear image buffer
    for(int y = 0; y < m_Yres; ++y) 
    {
	for(int x = 0; x < m_Xres; ++x)
	{
	    iter_buf[y * m_Xres + x]=-1;
	    clear_fate(x,y);
	}
    }
}

       
