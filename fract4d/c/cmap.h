
#ifndef CMAP_H_
#define CMAP_H_

#include "color.h"

typedef enum
{
    TRANSFER_NONE,
    TRANSFER_LINEAR,
    TRANSFER_SIZE
} e_transferType;

typedef struct 
{
    double index;
    rgba_t color;
} item_t;

class ColorMap
{
public:
    ColorMap();
    ~ColorMap();

    bool init(int n_colors);
    void set(int i, double d, int r, int g, int b, int a); 
    void set_solid(int which, int r, int g, int b, int a);
    void set_transfer(int which, e_transferType type);
 
    rgba_t get_solid(int which) const;
    rgba_t lookup(double index) const;
    rgba_t lookup_with_transfer(
	int fate, double index, int solid) const;
 private:
    int ncolors;
    item_t *items;
    rgba_t solids[2];
    e_transferType transfers[2];

};

extern void cmap_delete(ColorMap *cmap);
#endif /* CMAP_H_ */
