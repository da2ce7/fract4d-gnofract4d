#ifndef _IMAGE_H_
#define _IMAGE_H_

struct image
{
	int Xres;
	int Yres;
	char *buffer;

	image();
	~image();
	image(const image& im);
	bool set_resolution(int x, int y);
	double ratio();
};

#endif /* _IMAGE_H_ */
