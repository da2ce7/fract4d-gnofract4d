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

#include "image_public.h"
#include "colorizer_public.h"

class image : public IImage
{
    int m_Xres;
    int m_Yres;

    /* the RGB colours of the image */
    char *buffer;

    /* the iteration count for each (antialiased) pixel */
    int * iter_buf;

    int data_size;
    void * data_buf;
public:
    image();
    ~image();

    inline int Xres() const { return m_Xres; };
    inline int Yres() const { return m_Yres; };
    inline char *getBuffer() { return buffer; };

    // utilities
    inline int row_length() const;
    inline int bytes() const;

    // accessors
    void put(int x, int y, rgb_t pixel);
    rgb_t get(int x, int y) const;

    int getIter(int x, int y) const{
      return iter_buf[x + y * m_Xres];
    };

    void setIter(int x, int y, int iter) { 
      iter_buf[x + y * m_Xres] = iter;
    };

    void *getData(int x, int y) {
      if(data_buf == NULL)
      {
	  return NULL;
      }
      return (void *)((char *)data_buf + data_size * (x + y * m_Xres));
    };
    image(const image& im);
    bool set_resolution(int x, int y);
    bool set_data_size(int size);
    double ratio() const;
    void clear();

#ifdef _WIN32
    BITMAPINFO m_bmi;

    void resetDIB();

#endif
};

#endif /* _IMAGE_H_ */
