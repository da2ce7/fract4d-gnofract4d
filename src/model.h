/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
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

#include "gf4d_fractal.h"


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
    bool model_cmd_start(model_t *m);
    void model_cmd_finish(model_t *m);
    void model_undo(model_t *m);
    void model_redo(model_t *m);

    int model_cmd_reset(model_t *m);
    int model_cmd_save_image(model_t *m, char *filename);

    int model_cmd_save(model_t *m, char *filename);
    int model_cmd_load(model_t *m, char *filename);

    // used to avoid otherwise recursive commands
    void model_set_cmd_in_progress(model_t *m, int val);

    /* called by the fractal to tell us what it's up to */
    void model_status_callback(Gf4dFractal *f, gint val, model_t *m);

    /* retrieve things */
    Gf4dFractal *model_get_fract(model_t *m);
    Gf4dFractal *model_get_subfract(model_t *m, int num);

    /* copy subfract n onto main fract */
    void model_set_subfract(model_t *m, int num);

    /* make subfracts weird versions of main one */
    void model_update_subfracts(model_t *m);
    void model_toggle_explore_mode(model_t *m);

    // this is crap - lose it
    void model_set_subfract_widget(model_t *m, GtkWidget *widget, int num);

    // delegates to gundo
    void model_make_undo_sensitive(model_t *m, GtkWidget *widget);
    void model_make_redo_sensitive(model_t *m, GtkWidget *widget);

    // explorer stuff
    void model_set_weirdness_factor(model_t *m, gfloat weirdness);

#ifdef __cplusplus
}
#endif

#endif /* _MODEL_H_ */
