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

#ifndef _MODEL_H_
#define _MODEL_H_
/* Holds the application state (the model, in Model/View/Controller parlance */

/* opaque definition */
typedef struct _model model_t;

#include <gnome.h>

#include "gf4d_fractal.h"
#include "gf4d_movie.h"

#ifdef __cplusplus
extern "C" {
#endif

    /* ctor */
    model_t *model_new(void);	
	
    /* dtor */
    void model_delete(model_t **pm);

    /* flags */

    // quit after drawing current image
    void model_set_quit(model_t *m, int quit);
    // save image to this file when it's finished
    void model_set_save_file(model_t *m, char *filename);

    /* commands */
    bool model_cmd_start(model_t *m, char *msg);
    void model_cmd_finish(model_t *m, char *msg);
    void model_undo(model_t *m);
    void model_redo(model_t *m);

    int model_cmd_reset(model_t *m);
    int model_cmd_save_image(model_t *m, char *filename);

    int model_cmd_save(model_t *m, char *filename);
    int model_cmd_load(model_t *m, char *filename);

    // load without updating undo history - used by cmd-line parameters
    int model_nocmd_load(model_t *m, char *filename);

    int model_write_autosave_file(model_t *m);
    int model_load_autosave_file(model_t *m);

    // used to avoid otherwise recursive commands
    void model_set_cmd_in_progress(model_t *m, int val);

    /* called by the fractal to tell us what it's up to */
    void model_status_callback(Gf4dFractal *f, gint val, model_t *m);

    /* retrieve things */
    Gf4dFractal *model_get_fract(model_t *m);
    Gf4dMovie   *model_get_movie(model_t *m);
    Gf4dFractal *model_get_subfract(model_t *m, int num);

    /* copy subfract n onto main fract */
    void model_set_subfract(model_t *m, int num);

    /* make subfracts weird versions of main one */
    void model_update_subfracts(model_t *m);
    void model_toggle_explore_mode(model_t *m);

    // number of threads to use to calculate a fractal
    // only worth making this > 1 on an SMP computer
    int model_get_calcthreads(model_t *m);
    void model_set_calcthreads(model_t *m, int n);

    void model_add_subfract_widget(model_t *m, GtkWidget *widget);
    void model_set_top_widget(model_t *m, GtkWidget *widget, GtkWidget *app);
    GtkWidget *model_get_app(model_t *m);

    // delegates to gundo
    void model_make_undo_sensitive(model_t *m, GtkWidget *widget);
    void model_make_redo_sensitive(model_t *m, GtkWidget *widget);

    // explorer stuff
    void model_set_weirdness_factor(model_t *m, gfloat weirdness);

    // designate a widget as visible only in explorer mode
    void model_make_explore_visible(model_t *m, GtkWidget *widget);
    void model_make_explore_sensitive(model_t *m, GtkWidget *widget);

    // image dimensions
    void model_get_dimensions(model_t *m, int *pWidth, int *pHeight);
    void model_set_dimensions(model_t *m, int width, int height);
    void model_set_width(model_t *m, int width);
    void model_set_height(model_t *m, int height);
     
    // compiler properties
    void model_set_compiler_location(model_t *m, char *location);
    const char *model_get_compiler_location(model_t *m);

    void model_set_compiler_flags(model_t *m, char *location);
    const char *model_get_compiler_flags(model_t *m);

    // report an error
    void model_on_error(model_t *m, const char *message);

#ifdef __cplusplus
}
#endif

#endif /* _MODEL_H_ */
