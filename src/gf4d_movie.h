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

/* an object to hold a movie in the process of being rendered. As with
 * gf4d_fractal, this is an object rather than a widget. 
 */

#ifndef _GF4D_MOVIE_H_
#define _GF4D_MOVIE_H_

#include <stdio.h>
#include <gtk/gtkobject.h>
#include <pthread.h>

#include "gf4d_fractal.h"

#ifdef __cplusplus
extern "C" {
#endif

#define GF4D_TYPE_MOVIE                 (gf4d_movie_get_type())
#define GF4D_MOVIE(obj)                 GTK_CHECK_CAST (obj, GF4D_TYPE_MOVIE, Gf4dMovie)
#define GF4D_MOVIE_CLASS(klass)         GTK_CHECK_CLASS_CAST (klass, GF4D_TYPE_MOVIE, Gf4dMovieClass)
#define GF4D_IS_MOVIE(obj)              GTK_CHECK_TYPE (obj, GF4D_TYPE_MOVIE)
#define GF4D_IS_MOVIE_CLASS(klass)      GTK_CHECK_CLASS_TYPE((klass), GF4D_TYPE_MOVIE)

typedef struct _Gf4dMovie Gf4dMovie;
typedef struct _Gf4dMovieClass Gf4dMovieClass;
typedef struct _Gf4dMovieFrame Gf4dMovieFrame;

enum {
    GF4D_MOVIE_CALCULATING,
    GF4D_MOVIE_DONE
};

struct _Gf4dMovie
{
    GtkObject object;	

    GList *keyframes;

    pthread_t tid;
    pthread_mutex_t lock;

    // is the calculation thread running?
    pthread_mutex_t cond_lock;
    pthread_cond_t running_cond;

    // are any workers going?
    int workers_running;
    int status;

    Gf4dFractal *output;
};

struct _Gf4dMovieClass
{
    GtkObjectClass parent_class;
    void (* list_changed)       (Gf4dMovie *movie);
    void (* progress_changed)   (Gf4dMovie *movie);
    void (* image_complete)     (Gf4dMovie *movie, int frame);
    void (* status_changed)     (Gf4dMovie *movie); // equiv to message
};

struct _Gf4dMovieFrame
{
    Gf4dFractal *f;
    int nFrames;
};

// basic functions
GtkObject*    gf4d_movie_new(void);
GtkType       gf4d_movie_get_type(void);

#ifdef __cplusplus
}
#endif

void gf4d_movie_set_output(Gf4dMovie *mov, Gf4dFractal *f);

void gf4d_movie_calc(Gf4dMovie *mov, int nThreads);

gboolean gf4d_movie_write_params(Gf4dMovie *mov, const gchar *filename);
gboolean gf4d_movie_load_params(Gf4dMovie *mov, const gchar *filename);

/* are we currently calculating? */
gboolean gf4d_movie_is_calculating(Gf4dMovie *mov);

/* stop calculating now! */
void gf4d_movie_interrupt(Gf4dMovie *mov);

/* add f to the list after "f_after", or at the end if f_after is NULL */
void gf4d_movie_add(Gf4dMovie *mov, 
    Gf4dMovieFrame *fr, 
    Gf4dMovieFrame *fr_after);

/* remove "f" */
void gf4d_movie_remove(Gf4dMovie *mov, Gf4dMovieFrame *fr);

/* default number of tweened frames between keyframes */
#define DEFAULT_FRAMES 10 

Gf4dMovieFrame *gf4d_movie_frame_new(Gf4dFractal *f, int nFrames);
void gf4d_movie_frame_set_frames(Gf4dMovieFrame *fr, int nFrames);

#endif /* _GF4D_MOVIE_H_ */
