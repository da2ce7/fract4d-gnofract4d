#ifndef _IMAGE_H_
#define _IMAGE_H_

#ifdef _WIN32
#include <windows.h>
#include <atlbase.h>
#endif

#include "colorizer_public.h"

struct image
{
    int Xres;
    int Yres;
    char *buffer;
    int * iter_buf;

    image();
    ~image();

    void put(int x, int y, rgb_t pixel);
    rgb_t get(int x, int y);
    int getIter(int x, int y);

    inline int row_length();
    inline int image_bytes();
    inline int bytes();

    image(const image& im);
    bool set_resolution(int x, int y);
    double ratio();
    void clear();

#ifdef _WIN32
	BITMAPINFO m_bmi;

	void resetDIB();

#endif
};

#endif /* _IMAGE_H_ */
