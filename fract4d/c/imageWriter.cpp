#include <stdlib.h>
#include <stdio.h>

#include "image_public.h"

class image_writer : public ImageWriter
{
public:
    virtual ~image_writer() {};
protected:
    image_writer(FILE *fp_, IImage *image_) {
	fp = fp_;
	im = image_;
    }

    FILE *fp;
    IImage *im;
};

class tga_writer : public image_writer 
{
public:
    tga_writer(FILE *fp, IImage *image) : image_writer(fp,image) {};
  
    bool save_header();
    bool save_tile();
    bool save_footer();
};

bool tga_writer::save_header()
{
    unsigned char tga_header[] = {
	0, // 0: imageid len
	0, // 1: cmap type
	2, // 2: image type = uncompressed 24 bit color
	0,0,0,0,0, // 3 cmap spec
	0,0,0,0, // 8: ?
	0,0,0,0, // 12: filled in with width, height
	24, 32 // 16: ?
    };
    tga_header[12] = im->totalXres() & 0xFF;
    tga_header[13] = im->totalXres() >> 8;
    tga_header[14] = im->totalYres() & 0xFF;
    tga_header[15] = im->totalYres() >> 8;

    int written = fwrite(tga_header, 1, sizeof(tga_header), fp);
    if(written != sizeof(tga_header)) 
    {
	return false;
    }	
    return true;
}

bool tga_writer::save_tile()
{
    for (int y = 0; y < im->Yres(); y++)
    {
        for (int x = 0; x < im->Xres(); x++)
	{
            rgba_t pixel = im->get(x, y);
            fputc(pixel.b,fp);
	    fputc(pixel.g,fp);
	    fputc(pixel.r,fp);
	}
    }
    return true;
}
	
bool tga_writer::save_footer()
{
    static unsigned char tga_footer[] = {
	0, 0, //extoffs
	0, 0, //?
	'T', 'R', 'U', 'E', 'V', 'I', 'S', 'I', 'O','N',
	'-', 'X', 'F', 'I', 'L', 'E', '.'
    };

    int written = fwrite(tga_footer, 1, sizeof(tga_footer), fp);
    if(written != sizeof(tga_footer))
    {
	return false;
    }
    return true;
}

#ifdef PNG_ENABLED
#include "png.h"

class png_writer : public image_writer 
{
public:
    png_writer(FILE *fp, IImage *image) : image_writer(fp,image) {
	ok = false;
	png_ptr = png_create_write_struct(
	    PNG_LIBPNG_VER_STRING,
	    NULL, NULL, NULL); // FIXME do more error handling

	if(NULL == png_ptr)
	{
	    return;
	}

	info_ptr = png_create_info_struct(png_ptr);
	if(NULL == info_ptr)
	{
	    png_destroy_write_struct(&png_ptr, png_infopp_NULL);
	    return;
	}

	if (setjmp(png_jmpbuf(png_ptr)))
	{
	    /* If we get here, we had a problem writing the file */
	    png_destroy_write_struct(&png_ptr, &info_ptr);
	    return;
	}

	png_init_io(png_ptr, fp);

	ok = true;
    };
    ~png_writer() {
	if(ok)
	{
	    png_destroy_write_struct(&png_ptr, &info_ptr);
	}
    }

    bool save_header();
    bool save_tile();
    bool save_footer();

private:
    bool ok;
    png_structp png_ptr;
    png_infop info_ptr;
};

bool
png_writer::save_header()
{
    png_set_IHDR(
	png_ptr, info_ptr, 
	im->totalXres(), im->totalYres(), // width, height
	8, PNG_COLOR_TYPE_RGB, // bit depth, color type
	PNG_INTERLACE_NONE, 
	PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
    
    png_write_info(png_ptr, info_ptr);

    return true;
}

bool 
png_writer::save_tile()
{
    for (int y = 0; y < im->Yres(); y++)
    {
	png_bytep row = (png_bytep)(im->getBuffer() + im->row_length() * y); 
	png_write_rows(png_ptr, &row, 1);
    }
    printf("Wrote %d rows\n", im->Yres());
    return true;
}

bool
png_writer::save_footer()
{
   png_write_end(png_ptr, info_ptr);
   return true;
}

#endif

ImageWriter *
ImageWriter::create(image_file_t file_type, FILE *fp, IImage *image)
{
    switch(file_type)
    {
    case FILE_TYPE_TGA:
	return new tga_writer(fp, image);
#ifdef PNG_ENABLED
    case FILE_TYPE_PNG:
	return new png_writer(fp, image);
#endif
#ifdef JPG_ENABLED
    case FILE_TYPE_JPG:
	return new jpg_writer(fp, image);
#endif	
    }
    return NULL; // unknown file type
}
