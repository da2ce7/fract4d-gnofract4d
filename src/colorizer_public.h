#ifndef _COLORIZER_PUBLIC_H_
#define _COLORIZER_PUBLIC_H_

typedef struct colorizer colorizer_t;

#ifdef __cplusplus
extern "C" {
#endif

typedef struct rgb rgb_t;

struct rgb
{
	unsigned char r;
	unsigned char g;
	unsigned char b;
};

typedef enum {
	COLORIZER_RGB,
	COLORIZER_CMAP
} e_colorizer;

colorizer_t *colorizer_new(e_colorizer);
void colorizer_delete(colorizer_t **);

#ifdef __cplusplus
}
#endif

#endif /* _COLORIZER_PUBLIC_H_ */
