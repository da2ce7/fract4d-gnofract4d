
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
} list_item_t;

class ColorMap
{
public:
    ColorMap();
    virtual ~ColorMap();

    virtual bool init(int n_colors) = 0;
    virtual void set_solid(int which, int r, int g, int b, int a);
    virtual void set_transfer(int which, e_transferType type);
 
    virtual rgba_t get_solid(int which) const;
    virtual rgba_t lookup(double index) const = 0;
    virtual rgba_t lookup_with_transfer(
	int fate, double index, int solid) const;
 protected:
    int ncolors;
    rgba_t solids[2];
    e_transferType transfers[2];
};

class ListColorMap: public ColorMap
{
 public:
    ListColorMap();
    ~ListColorMap();

    bool init(int n_colors);
    void set(int i, double d, int r, int g, int b, int a);
    rgba_t lookup(double index) const; 
 private:
    list_item_t *items;
};

class GradientColorMap: public ColorMap
{
 public:
    GradientColorMap();
    ~GradientColorMap();

    //bool init(int n_colors);
};

extern void cmap_delete(ColorMap *cmap);
#endif /* CMAP_H_ */
