
#ifndef CMAP_H_
#define CMAP_H_

#include "color.h"

struct s_cmap;

typedef struct s_cmap cmap_t;

#ifdef __cplusplus
extern "C" {
#endif

extern cmap_t *cmap_new(int ncolors);
extern void cmap_set(cmap_t *cmap, int i, double d, int r, int g, int b, int a); 
extern rgba_t cmap_lookup(cmap_t *cmap, double index);
extern void cmap_delete(cmap_t *cmap);

#ifdef __cplusplus
}
#endif

#endif /* CMAP_H_ */
