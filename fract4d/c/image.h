/* The RGB buffer which the fractal-drawing process writes into. */

#ifndef _IMAGE_H_
#define _IMAGE_H_

#include "image_public.h"

#include <cassert>

class image : public IImage
{
    static const int N_SUBPIXELS;
    int m_Xres;
    int m_Yres;

    /* the RGB colours of the image */
    char *buffer;

    /* the iteration count for each pixel */
    int * iter_buf;

    /* the value of #index for each pixel */
    float *index_buf;

    /* the fate of each pixel */
    fate_t *fate_buf;

    void delete_buffers();
    void alloc_buffers();
    void clear_fate(int x, int y);

public:
    image();
    image(const image& im);
    ~image();

    inline int Xres() const { return m_Xres; };
    inline int Yres() const { return m_Yres; };
    inline char *getBuffer() { return buffer; };
    inline fate_t *getFateBuffer() { return fate_buf; };

    // utilities
    inline int row_length() const {return m_Xres * 3; };

    int bytes() const;

    // accessors
    void put(int x, int y, rgba_t pixel);
    rgba_t get(int x, int y) const;

    int getIter(int x, int y) const {
      return iter_buf[x + y * m_Xres];
    };

    void setIter(int x, int y, int iter) { 
      iter_buf[x + y * m_Xres] = iter;
    };

    fate_t getFate(int x, int y, int subpixel);
    void setFate(int x, int y, int subpixel, fate_t fate);

    int index_of_subpixel(int x, int y, int subpixel) {
	assert(subpixel >= 0 && subpixel < N_SUBPIXELS);
	assert(x >= 0 && x < m_Xres);
	assert(y >= 0 && y < m_Yres);

	return (y * m_Xres + x ) * N_SUBPIXELS + subpixel;
    };

    // one beyond last pixel
    int index_of_sentinel_subpixel() {
	return m_Xres * m_Yres * N_SUBPIXELS;
    };

    bool set_resolution(int x, int y);

    double ratio() const;
    void clear();

    bool save(const char *filename);
};

#endif /* _IMAGE_H_ */
