#include <stdlib.h>
#include <stdio.h>

#include "image.h"

#undef NDEBUG

#include <assert.h>

#define RED 0
#define GREEN 1
#define BLUE 2

image::~image()
{
    delete[] buffer;
    delete[] iter_buf;
    //free(data_buf);
}

image::image()
{
    m_Xres = m_Yres = 0;
    buffer = NULL;
    iter_buf = NULL;
    data_buf = NULL;
    data_size = 0;
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

image::image(const image& im)
{
    m_Xres = im.m_Xres;
    m_Yres = im.m_Yres;
    data_size = im.data_size;
    buffer = new char[bytes()];
    iter_buf = new int[m_Xres * m_Yres];
    //data_buf = malloc(data_size * m_Xres * m_Yres);
}

bool image::set_resolution(int x, int y)
{
    if(buffer && m_Xres == x && m_Yres == y) return 0;
    m_Xres = x;
    m_Yres = y;
    delete[] buffer;
    delete[] iter_buf;
    //free(data_buf);
    buffer = new char[bytes()];
    iter_buf = new int[m_Xres * m_Yres];
    //data_buf = malloc(data_size * m_Xres * m_Yres);

    rgba_t pixel = { 200, 178, 98, 255};

    for(int i = 0; i < y; ++i)
    {
	for(int j = 0; j < x; ++j)
	{
	    put(j,i,pixel);
	}
    }

    return 1;
}

double image::ratio() const
{
    return ((double)m_Yres / m_Xres);
}

void image::clear()
{
    // no need to clear image buffer
    for(int i = 0; i < m_Xres * m_Yres; i++) {
        iter_buf[i]=-1;
    }
}

bool image::set_data_size(int size)
{
    if(size == data_size) return false;
    data_size = size;
    //data_buf = realloc(data_buf,size * m_Xres * m_Yres);
    return true;
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
