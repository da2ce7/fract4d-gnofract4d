#include <stdlib.h>

#include "image.h"

image::~image()
{
	delete[] buffer;
}

image::image()
{
	Xres = Yres = 0;
	buffer = NULL;
}

image::image(const image& im)
{
	Xres = im.Xres;
	Yres = im.Yres;
	buffer = new char[3 * Xres * Yres];
}

bool image::set_resolution(int x, int y)
{
	if(buffer && Xres == x && Yres == y) return 0;
	Xres = x;
	Yres = y;
	delete[] buffer;
	buffer = new char[3 * Xres * Yres];
	return 1;
}

double image::ratio()
{
	return ((double)Yres / Xres);
}
