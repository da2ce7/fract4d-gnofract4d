/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

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
    IFractal *f;
    image_t *im;
    pthread_t tid;
    pthread_mutex_t lock;
    pthread_mutex_t cond_lock;
    pthread_mutex_t pause_lock;
    pthread_cond_t running_cond;
    // are any workers going?
    volatile int workers_running;
    // how many workers in total? (no, these can't be the same var!)
    int nWorkers;
    // what's our current status? (only used to restore it after a pause)
    int status; 
    gboolean paused;
    gboolean fOnGTKThread;
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
void gf4d_fractal_move(Gf4dFractal *f, param_t i, double direction);

/* if the fractal is on the main GTK thread, it needs to yield the gdk
 * mutex before waiting for other threads, to avoid deadlock.  By
 * default this is assumed to be the case. If calling methods from
 * another thread (as in the movie code), set this to false
 * first. This property is NOT copied with the rest of the fractal by
 * gf4d_fractal_copy et al
 * 
 * Apologies for this horrendous mess!  */
void gf4d_fractal_set_on_gui_thread(Gf4dFractal *f, gboolean fOnThread);
gboolean gf4d_fractal_is_on_gui_thread(Gf4dFractal *f);


void gf4d_fractal_calc(Gf4dFractal *f, 
    int nThreads, e_antialias effective_aa=AA_DEFAULT);

// temporary method: not threaded, just works out new colors
void gf4d_fractal_recolor(Gf4dFractal *f); 

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

/* stop calculation until told to continue */
gboolean gf4d_fractal_pause(Gf4dFractal *f, gboolean pause);

/* update functions */
void gf4d_fractal_set_max_iterations(Gf4dFractal *f, int val);
void gf4d_fractal_set_param(Gf4dFractal *f, param_t i, char *val);
void gf4d_fractal_set_aa(Gf4dFractal *f, e_antialias val);
void gf4d_fractal_set_auto(Gf4dFractal *f, gboolean val);
int gf4d_fractal_set_precision(Gf4dFractal *f, int digits);

/* iteration functions */
iterFunc *gf4d_fractal_get_func(Gf4dFractal *f);
void gf4d_fractal_set_func(Gf4dFractal *f, const char *type);

/* color functions */
colorizer_t *gf4d_fractal_get_colorizer(Gf4dFractal *f);
void gf4d_fractal_set_colorizer(Gf4dFractal *f, colorizer_t *cizer);

// type = 0 for outer, 1 for inner
e_colorFunc gf4d_fractal_get_colorFunc(Gf4dFractal *f, int type);
void gf4d_fractal_set_colorFunc(Gf4dFractal *f, e_colorFunc, int type); 

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

IFractal *gf4d_fractal_copy_fract(Gf4dFractal *f);
void gf4d_fractal_set_fract(Gf4dFractal *gf, IFractal * f);
void gf4d_fractal_update_fract(Gf4dFractal *gf, Gf4dFractal *gf2);

void gf4d_fractal_set_inexact(Gf4dFractal *gf_dst, Gf4dFractal *gf_src, double weirdness);
void gf4d_fractal_set_mixed(Gf4dFractal *f_dst, Gf4dFractal *f_src1, Gf4dFractal *f_src2, 
    double lambda);

void gf4d_fractal_set_keep_data(Gf4dFractal *f, gboolean keep_data); 


void gf4d_fractal_parameters_changed(Gf4dFractal *f);
void gf4d_fractal_image_changed(Gf4dFractal *f, int x1, int x2, int y1, int y2);
void gf4d_fractal_progress_changed(Gf4dFractal *f, float progress);
void gf4d_fractal_status_changed(Gf4dFractal *f, int status_val);

// returns true if we've been interrupted and are supposed to stop
bool gf4d_fractal_try_finished_cond(Gf4dFractal *f);

#endif /* _GF4D_FRACTAL_H_ */
