#include <stdlib.h>

#include "image.h"

image::~image()
{
	delete[] buffer;
	delete[] iter_buf;
}

image::image()
{
	Xres = Yres = 0;
	buffer = NULL;
	iter_buf = NULL;
}

image::image(const image& im)
{
	Xres = im.Xres;
	Yres = im.Yres;
	buffer = new char[3 * Xres * Yres];
	iter_buf = new int[Xres * Yres];
}

bool image::set_resolution(int x, int y)
{
	if(buffer && Xres == x && Yres == y) return 0;
	Xres = x;
	Yres = y;
	delete[] buffer;
	delete[] iter_buf;
	buffer = new char[3 * Xres * Yres];
	iter_buf = new int[Xres * Yres];
	return 1;
}

double image::ratio()
{
	return ((double)Yres / Xres);
}
