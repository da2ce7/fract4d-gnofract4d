/* an object to hold the fractal data. This is an *object*, not a
 * widget - it doesn't display anything. It just holds the fractal's
 * state and provides "changed" signal notifications to keep the UI in
 * sync */

#ifndef _GF4D_FRACTAL_H_
#define _GF4D_FRACTAL_H_

#include <stdio.h>
#include <gtk/gtkobject.h>
#include <pthread.h>

#ifdef __cplusplus
extern "C" {
#else if 0
} // just to keep emacs indenter happy!
#endif

#define GF4D_TYPE_FRACTAL                 (gf4d_fractal_get_type())
#define GF4D_FRACTAL(obj)                 GTK_CHECK_CAST (obj, GF4D_TYPE_FRACTAL, Gf4dFractal)
#define GF4D_FRACTAL_CLASS(klass)         GTK_CHECK_CLASS_CAST (klass, GF4D_TYPE_FRACTAL, Gf4dFractalClass)
#define GF4D_IS_FRACTAL(obj)              GTK_CHECK_TYPE (obj, GF4D_TYPE_FRACTAL)
#define GF4D_IS_FRACTAL_CLASS(klass)      GTK_CHECK_CLASS_TYPE((klass), GF4D_TYPE_FRACTAL)

typedef struct _Gf4dFractal Gf4dFractal;
typedef struct _Gf4dFractalClass Gf4dFractalClass;

#include "fract_public.h"
#include "colorizer_public.h"
#include "pointFunc_public.h"

struct _Gf4dFractal
{
    GtkObject object;	
    fractal_t *f;
    image_t *im;
    pthread_t tid;
    pthread_mutex_t lock;
    pthread_mutex_t cond_lock;
    pthread_cond_t running_cond;
    // are any workers going?
    int workers_running;
    // how many workers in total? (no, these can't be the same var!)
    int nWorkers;
};

struct _Gf4dFractalClass
{
    GtkObjectClass parent_class;
    // args should change here
    void (* parameters_changed) (Gf4dFractal *fract);
    void (* image_changed)      (Gf4dFractal *fract);
    void (* progress_changed)   (Gf4dFractal *fract);
    void (* status_changed)     (Gf4dFractal *fract); // equiv to message
};

// basic functions
GtkObject*    gf4d_fractal_new(void);
GtkType       gf4d_fractal_get_type(void);

#ifdef __cplusplus
}
#endif

class iterFunc;

void gf4d_fractal_relocate(Gf4dFractal *f, int x, int y, double zoom);
void gf4d_fractal_flip2julia(Gf4dFractal *f, int x, int y);
void gf4d_fractal_move(Gf4dFractal *f, param_t i, int direction);

void gf4d_fractal_calc(Gf4dFractal *f, int nThreads);

void gf4d_fractal_reset(Gf4dFractal *f);
gboolean gf4d_fractal_write_params(Gf4dFractal *f, const gchar *filename);
gboolean gf4d_fractal_load_params(Gf4dFractal *f, const gchar *filename);

/* accessor functions */
int gf4d_fractal_get_max_iterations(Gf4dFractal *f);
e_antialias gf4d_fractal_get_aa(Gf4dFractal *f);
gboolean gf4d_fractal_get_auto(Gf4dFractal *f);
char *gf4d_fractal_get_param(Gf4dFractal *f, param_t i);

/* stop calculating now! */
void gf4d_fractal_interrupt(Gf4dFractal *f);

/* update functions */
void gf4d_fractal_set_max_iterations(Gf4dFractal *f, int val);
void gf4d_fractal_set_param(Gf4dFractal *f, param_t i, char *val);
void gf4d_fractal_set_aa(Gf4dFractal *f, e_antialias val);
void gf4d_fractal_set_auto(Gf4dFractal *f, gboolean val);
int gf4d_fractal_set_precision(Gf4dFractal *f, int digits);

/* iteration functions */
iterFunc *gf4d_fractal_get_func(Gf4dFractal *f);
void gf4d_fractal_set_func(Gf4dFractal *f, int type);

/* color functions */
e_colorizer gf4d_fractal_get_color_type(Gf4dFractal *f);
void gf4d_fractal_set_color_type(Gf4dFractal *f, e_colorizer type);

/* color functions : only for COLORIZER_CMAP */
void gf4d_fractal_set_cmap_file(Gf4dFractal *f, const char *filename);
gchar *gf4d_fractal_get_cmap_file(Gf4dFractal *f);

/* color functions : only for COLORIZER_RGB */
double gf4d_fractal_get_r(Gf4dFractal *f);
double gf4d_fractal_get_g(Gf4dFractal *f);
double gf4d_fractal_get_b(Gf4dFractal *f);
void gf4d_fractal_set_color(Gf4dFractal *f, double r, double g, double b);

gboolean gf4d_fractal_get_potential(Gf4dFractal *f);
void gf4d_fractal_set_potential(Gf4dFractal *f, gboolean potential);

    /* bailout type */
e_bailFunc gf4d_fractal_get_bailout_type(Gf4dFractal *f);
void gf4d_fractal_set_bailout_type(Gf4dFractal *f, e_bailFunc);

/* image-related functions: to be removed */
int gf4d_fractal_get_xres(Gf4dFractal *f);
int gf4d_fractal_get_yres(Gf4dFractal *f);
guchar *gf4d_fractal_get_image(Gf4dFractal *f);
double gf4d_fractal_get_ratio(Gf4dFractal *f);
int  gf4d_fractal_set_resolution(Gf4dFractal *f, int xres, int yres);

/* sneaky functions */
Gf4dFractal *gf4d_fractal_copy(Gf4dFractal *f);

// is f2 the same as f?
gboolean gf4d_fractal_is_equal(Gf4dFractal *f, Gf4dFractal *f2);

fractal_t *gf4d_fractal_copy_fract(Gf4dFractal *f);
void gf4d_fractal_set_fract(Gf4dFractal *gf, fractal_t * f);
void gf4d_fractal_update_fract(Gf4dFractal *gf, Gf4dFractal *gf2);

void gf4d_fractal_set_inexact(Gf4dFractal *gf_dst, Gf4dFractal *gf_src, double weirdness);

#include "fract_callbacks.h"

#endif /* _GF4D_FRACTAL_H_ */
