
#ifndef CMAP_H_
#define CMAP_H_

#include "color.h"

struct s_cmap;

typedef struct s_cmap cmap_t;

typedef enum
{
    TRANSFER_NONE,
    TRANSFER_LINEAR,
    TRANSFER_SIZE
} e_transferType;


extern cmap_t *cmap_new(int ncolors);
extern void cmap_set(cmap_t *cmap, int i, double d, int r, int g, int b, int a); 
extern void cmap_set_solid(cmap_t *cmap, int which, int r, int g, int b, int a);
extern void cmap_set_transfer(cmap_t *cmap, int which, e_transferType type);
extern rgba_t cmap_get_solid(cmap_t *cmap, int which);
extern rgba_t cmap_lookup(cmap_t *cmap, double index);
extern rgba_t cmap_lookup_with_transfer(
    cmap_t *cmap, int fate, double index, int solid);
extern void cmap_delete(cmap_t *cmap);

#endif /* CMAP_H_ */
