
#ifndef CMAP_H_
#define CMAP_H_

#include "color.h"

struct s_cmap;

typedef struct s_cmap cmap_t;


extern cmap_t *cmap_new(int ncolors);
extern void cmap_set(cmap_t *cmap, int i, double d, int r, int g, int b, int a); 
extern rgba_t cmap_lookup(cmap_t *cmap, double index);
extern void cmap_delete(cmap_t *cmap);

#endif /* CMAP_H_ */
