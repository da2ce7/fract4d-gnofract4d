/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

/* The RGB buffer which the fractal-drawing process writes into. This
   is needlessly complicated by my abortive attempts to support
   Windows' fscked-up DIB format */

#ifndef _IMAGE_H_
#define _IMAGE_H_

#ifdef _WIN32
#include <windows.h>
#include <atlbase.h>
#endif

#include "colorizer_public.h"

class image
{
    int m_Xres;
    int m_Yres;

    /* the RGB colours of the image */
    char *buffer;

 public:
    /* the iteration count for each (antialiased) pixel */
    int * iter_buf;

    image();
    ~image();

    inline int Xres() { return m_Xres; };
    inline int Yres() { return m_Yres; };
    inline char *getBuffer() { return buffer; };

    // utilities
    inline int row_length();
    inline int image_bytes();
    inline int bytes();

    // accessors
    void put(int x, int y, rgb_t pixel);
    rgb_t get(int x, int y);

    int getIter(int x, int y);

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
