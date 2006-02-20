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
    buffer = NULL;
    iter_buf = NULL;
    fate_buf = NULL;
    index_buf = NULL;
    m_totalXres = m_totalYres = m_xoffset = m_yoffset = 0;
}

image::image(const image& im)
{
    m_Xres = im.m_Xres;
    m_Yres = im.m_Yres;

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

void
image::set_total_resolution(int x, int y)
{
    m_totalXres = x; 
    m_totalYres = y;
}

void
image::set_offset(int x, int y)
{
    m_xoffset = x;
    m_yoffset = y;
}

bool 
image::set_resolution(int x, int y)
{
    if(buffer && m_Xres == x && m_Yres == y) return false;
    m_Xres = x;
    m_Yres = y;

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

	       
bool image::save(const char *filename)
{
    //printf("saving to %s\n",filename);
    FILE *fp = fopen(filename,"wb");
    if(!fp) return false;
    unsigned char tga_header[] = {
	0, // 0: imageid len
	0, // 1: cmap type
	2, // 2: image type = uncompressed 24 bit color
	0,0,0,0,0, // 3 cmap spec
	0,0,0,0, // 8: ?
	0,0,0,0, // 12: filled in with width, height
	24, 32 // 16: ?
    };
    tga_header[12] = m_Xres & 0xFF;
    tga_header[13] = m_Xres >> 8;
    tga_header[14] = m_Yres & 0xFF;
    tga_header[15] = m_Yres >> 8;

    unsigned char tga_footer[] = {
	0, 0, //extoffs
	0, 0, //?
	'T', 'R', 'U', 'E', 'V', 'I', 'S', 'I', 'O','N',
	'-', 'X', 'F', 'I', 'L', 'E', '.'
    };

    int written = fwrite(tga_header, 1, sizeof(tga_header), fp);
    if(written != sizeof(tga_header)) goto error;

    for (int y = 0; y < m_Yres; y++)
    {
        for (int x = 0; x < m_Xres; x++)
	{
            rgba_t pixel = get(x, y);
            fputc(pixel.b,fp);
	    fputc(pixel.g,fp);
	    fputc(pixel.r,fp);
	}
    }

    written = fwrite(tga_footer, 1, sizeof(tga_footer), fp);
    if(written != sizeof(tga_footer)) goto error;

    fclose(fp);
    return true;
 error:
    fclose(fp);
    return false;
}
