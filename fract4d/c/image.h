/* The RGB buffer which the fractal-drawing process writes into. */

#ifndef _IMAGE_H_
#define _IMAGE_H_

#include "image_public.h"

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
    inline int row_length() const {return m_Xres * 3; };

    int bytes() const;

    // accessors
    void put(int x, int y, rgba_t pixel);
    rgba_t get(int x, int y) const;

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

    bool save(const char *filename);
};

#endif /* _IMAGE_H_ */
