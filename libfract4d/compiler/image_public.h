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

/* An abstraction for the buffer into which we read and write image
 * data and associated per-pixel information.  An implementation must
 * be provided by the host program. */

#ifndef IMAGE_PUBLIC_H_
#define IMAGE_PUBLIC_H_

/* image must provide a rectangular (x by y) array of 
   rgb_t : r,g,b triple - this is the actual color of the pixel.
   iter: int - the number of iterations performed before bailout. 
         -1 indicates that this point did not bail out
   data: some fractal types want to store additional info. The 
         image type should allocate the number of bytes set by
	 set_data_size() per pixel. The data_size can be 0.


   pixel in this context is without antialiasing, that occurs before
   the data is stored.
*/
   
#include "color.h"

class IImage
{
public:
    //static IImage *create();
    //virtual IImage *clone();

    virtual ~IImage() {};
    // return true if this resulted in a change of size
    virtual bool set_resolution(int x, int y) = 0;
    // return true if this resulted in a changed amount of data stored
    virtual bool set_data_size(int size) = 0;

    // return xres()/yres()
    virtual double ratio() const = 0;
    // set every iter value to -1. Other data need not be cleared
    virtual void clear() = 0;

    // return number of pixels wide this image is
    virtual int Xres() const = 0;
    // number of pixels wide
    virtual int Yres() const = 0;
    
    // accessors for color data
    virtual void put(int x, int y, rgba_t pixel) = 0;
    virtual rgba_t get(int x, int y) const = 0;

    // accessors for iteration data
    virtual int getIter(int x, int y) const = 0;
    virtual void setIter(int x, int y, int iter) = 0;

    // we will both read & write data using the pointer returned by this method
    virtual void *getData(int x, int y) = 0;
};

#endif /* IMAGE_PUBLIC_H_ */

