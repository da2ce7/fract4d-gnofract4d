#include <stdlib.h>

#include "image.h"
#include "iterFunc.h"

// byte order in a DIB is, obviously, as fucked up as everything else
#ifdef _WIN32
#	define RED 2
#	define GREEN 1
#	define BLUE 0
#else
#	define RED 0
#	define GREEN 1
#	define BLUE 2
#endif

image::~image()
{
    delete[] buffer;
    delete[] iter_buf;
}

image::image()
{
    m_Xres = m_Yres = 0;
    buffer = NULL;
    iter_buf = NULL;

#ifdef _WIN32
	resetDIB();
#endif
}

inline int
image::row_length()
{
#ifdef _XX_WIN32
	// round up to nearest multiple of 4 
	int adj = (m_Xres * 3) % 4;
	return m_Xres * 3 + adj;
#else
	// GdkRGB needs no such steenkin' adjustment
	return m_Xres * 3;
#endif
}

inline int
image::bytes()
{
	return row_length() * m_Yres;
}

void 
image::put(int x, int y, rgb_t pixel)
{
#ifdef _WIN32
	char *start = buffer + bytes() - row_length() + x*3 - y * row_length();
	ATLASSERT(start >= buffer && start + 2 < buffer + bytes());
#else
	char *start = buffer + x*3 + y * row_length();
#endif	
	start[RED] = pixel.r;
	start[GREEN] = pixel.g;
	start[BLUE] = pixel.b;
}

rgb_t 
image::get(int x, int y)
{
#ifdef _WIN32
	char *start = buffer + bytes() - row_length() + x*3 - y * row_length();
#else
	char *start = buffer + x*3 + y * row_length();
#endif
	rgb_t pixel;
	pixel.r = start[RED];
	pixel.g = start[GREEN];
	pixel.b = start[BLUE];

	return pixel;
}

int 
image::getIter(int x, int y)
{
    return iter_buf[x + y * m_Xres];
}

#ifdef _WIN32
void
image::resetDIB()
{
	m_bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
	m_bmi.bmiHeader.biWidth = m_Xres;
	m_bmi.bmiHeader.biHeight = m_Yres;
	m_bmi.bmiHeader.biPlanes = 1;
	m_bmi.bmiHeader.biBitCount = 24;
	m_bmi.bmiHeader.biCompression = BI_RGB; // no compression
	m_bmi.bmiHeader.biSizeImage = bytes();
	m_bmi.bmiHeader.biXPelsPerMeter = 0;
	m_bmi.bmiHeader.biYPelsPerMeter = 0;
	m_bmi.bmiHeader.biClrUsed = 0;
	m_bmi.bmiHeader.biClrImportant = 0;

	// pointless color
	m_bmi.bmiColors[0].rgbBlue = 0;
	m_bmi.bmiColors[0].rgbRed = 0;
	m_bmi.bmiColors[0].rgbGreen = 0;
	m_bmi.bmiColors[0].rgbReserved = 0;
}

#endif
image::image(const image& im)
{
    m_Xres = im.m_Xres;
    m_Yres = im.m_Yres;
    buffer = new char[bytes()];
    iter_buf = new int[m_Xres * m_Yres];
}

bool image::set_resolution(int x, int y)
{
    if(buffer && m_Xres == x && m_Yres == y) return 0;
    m_Xres = x;
    m_Yres = y;
    delete[] buffer;
    delete[] iter_buf;
    buffer = new char[bytes()];
    iter_buf = new int[m_Xres * m_Yres];
#ifdef _WIN32
	resetDIB();
#endif
    return 1;
}

double image::ratio()
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
