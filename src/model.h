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

typedef void callback_func_t(model_t *, void *) ;
typedef void undo_callback_func_t(model_t *m, int status, void *);

#ifdef __cplusplus
extern "C" {
#endif

        /* ctor */
	model_t *model_new(void);	
	

	/* dtor */
	void model_delete(model_t **pm);

	/* apply changes */	
	//void model_update(model_t *m);

	/* commands */
	Gf4dFractal *model_cmd_start(model_t *m);
	void model_cmd_finish(model_t *m);
	void model_undo(model_t *m);
	void model_redo(model_t *m);
	int model_can_undo(model_t *m);
	int model_can_redo(model_t *m);

	int model_cmd_reset(model_t *m);
	int model_cmd_save_image(model_t *m, char *filename);

	int model_cmd_save(model_t *m, char *filename);
	int model_cmd_load(model_t *m, char *filename);
	int model_save(model_t *m);

	/* retrieve things */
	Gf4dFractal *model_get_fract(model_t *m);

	void model_set_undo_status_callback(model_t *m,
					    undo_callback_func_t *f,
					    void *user_data);

	void model_set_redo_status_callback(model_t *m,
					    undo_callback_func_t *f,
					    void *user_data);

	void model_interrupt(model_t *m);
	void model_clear_interrupt(model_t *m);
	int model_is_interrupted(model_t *m);

	void model_undo_status(model_t *m, int status);
	void model_redo_status(model_t *m, int status);

#ifdef __cplusplus
}
#endif

#endif /* _MODEL_H_ */
