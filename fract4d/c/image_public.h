/* An abstraction for the buffer into which we read and write image
 * data and associated per-pixel information.  An implementation must
 * be provided by the host program. */

#ifndef IMAGE_PUBLIC_H_
#define IMAGE_PUBLIC_H_

/* image must provide a rectangular (x by y) array of 
   rgb_t : r,g,b triple - this is the actual color of the pixel.
   iter: int - the number of iterations performed before bailout. 
         -1 indicates that this point did not bail out

   pixel in this context is without antialiasing, that occurs before
   the data is stored.

   These fields are stored per subpixel, so there's an (x by y by 4) array
   of them.

   fate_t: what happened to this point. 
   index : the value of #index after calculating this point.

*/
   
#include "color.h"
#include "fate.h"

class IImage
{
public:
    virtual ~IImage() {};
    // return true if this resulted in a change of size
    virtual bool set_resolution(int x, int y) = 0;
    virtual bool ok() = 0;

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

    
    // accessors for fate data
    virtual bool hasFate() const = 0;
    virtual fate_t getFate(int x, int y, int sub) const = 0;
    virtual void setFate(int x, int y, int sub, fate_t fate) = 0;
    // set all subpixels equal to zero'th one
    virtual void fill_subpixels(int x, int y) = 0;

    // accessors for index data
    virtual float getIndex(int x, int y, int sub) const = 0;
    virtual void setIndex(int x, int y, int sub, float index) = 0;
    
    virtual int getNSubPixels() const = 0;
    virtual bool hasUnknownSubpixels(int x, int y) const = 0;
};

#endif /* IMAGE_PUBLIC_H_ */

