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

#include <stdlib.h>
#include <stdio.h>

#include <gnome.h>
#include "model.h"
#include "gf4d_fractal.h"

#ifndef NDEBUG
#define MODEL_HISTORY_DEBUG(_x) model_history_debug(_x)
#else
#define MODEL_HISTORY_DEBUG(_x)
#endif

double zoom=2;

/* real definition */
struct _model {
	GList *history;

	Gf4dFractal *fract;

	undo_callback_func_t *undo_status_cb, *redo_status_cb;

	void *undo_status_user_data;
	void *redo_status_user_data;

	int interrupted;
};

model_t *
model_new(void)
{
	model_t *m = calloc(sizeof(model_t),1);

	m->fract = GF4D_FRACTAL(gf4d_fractal_new());
	m->history = g_list_prepend(m->history,m->fract);
	return m;
}

void
model_delete(model_t **pm)
{
	model_t *m = *pm;
	gtk_object_destroy(GTK_OBJECT(&m->fract));
	free(m);
	*pm = NULL;
}

int
model_save(model_t *m)
{
	return 1;
}

int
model_cmd_save_image(model_t *m, char *filename)
{
	GdkImlibImage *image;
	image = gdk_imlib_create_image_from_data(gf4d_fractal_get_image(m->fract),
						 NULL,
						 gf4d_fractal_get_xres(m->fract),
						 gf4d_fractal_get_yres(m->fract));
	gdk_imlib_save_image(image,filename, NULL);
	gdk_imlib_destroy_image(image);

	return 1;
}


int 
model_cmd_save(model_t *m, char *filename)
{
	FILE *fp;
	if ((fp = fopen(filename, "wb")) == 0) {
		return 0;
	}

	gf4d_fractal_write_params(m->fract,fp);

	fclose(fp);
	return 1;
}
	
int 
model_cmd_load(model_t *m, char *filename)
{
	FILE *fp;
	if ((fp = fopen(filename, "rb")) == 0) return 0;

	model_cmd_start(m);
	gf4d_fractal_load_params(m->fract,fp);

	fclose(fp);

	model_cmd_finish(m);
	return 1;
}


#ifndef NDEBUG
void model_history_debug(model_t *m);

void
model_history_debug(model_t *m)
{
	GList *list = g_list_first(m->history);
	while(list)
	{
		char *x = gf4d_fractal_get_param((Gf4dFractal *)(list->data),XCENTER);
		char *y = gf4d_fractal_get_param((Gf4dFractal *)(list->data),YCENTER);
		if(list->data == m->fract) {
			g_print("<%s %s> ",x,y);
		} else {
			g_print("(%s %s) ",x,y);
		}
		list = list->next;
	}
	g_print("\n");
}
#endif

int
model_can_undo(model_t *m)
{
	if(m->history->next) return 1;
	return 0;
}

int 
model_can_redo(model_t *m)
{
	if(m->history->prev) return 1;
	return 0;
}

void 
model_undo(model_t *m)
{
	g_print("pre undo: ");
	model_history_debug(m);
	if(m->history->next)
	{
		Gf4dFractal *top_fract = m->history->next->data;
		gf4d_fractal_set_resolution(top_fract,
				     gf4d_fractal_get_xres(m->fract),
				     gf4d_fractal_get_yres(m->fract));
		m->fract = top_fract;
		m->history = m->history->next;
	}
	model_undo_status(m,model_can_undo(m));
	model_redo_status(m,model_can_redo(m));
	g_print("post undo: ");
	model_history_debug(m);
}

void
model_redo(model_t *m)
{
	g_print("pre redo: ");
	model_history_debug(m);
	if(m->history->prev)
	{
		Gf4dFractal *top_fract = m->history->prev->data;
		gf4d_fractal_set_resolution(top_fract,
				     gf4d_fractal_get_xres(m->fract),
				     gf4d_fractal_get_yres(m->fract));
		m->fract = top_fract;
		m->history = m->history->prev;
	}
	model_undo_status(m,model_can_undo(m));
	model_redo_status(m,model_can_redo(m));
	g_print("post redo: ");
	model_history_debug(m);
}


Gf4dFractal *
model_cmd_start(model_t *m)
{
	return m->fract;
}

Gf4dFractal *
model_get_fract(model_t *m)
{
	return m->fract;
}

void
model_cmd_finish(model_t *m)
{
	g_print("post do: ");
	gf4d_fractal_parameters_changed(m->fract);
}

void
model_interrupt(model_t *m)
{
	m->interrupted=1;
}

void
model_clear_interrupt(model_t *m)
{
	m->interrupted=0;
}

int
model_is_interrupted(model_t *m)
{
	return m->interrupted;
}

void
model_undo_status(model_t *m, int status)
{
	if(m->undo_status_cb) m->undo_status_cb(m,status,m->undo_status_user_data);
}

void
model_redo_status(model_t *m, int status)
{
	if(m->redo_status_cb) m->redo_status_cb(m,status,m->redo_status_user_data);
}

void
model_set_undo_status_callback(model_t *m, undo_callback_func_t *f, void *user_data)
{
	m->undo_status_cb = f;
	m->undo_status_user_data = user_data;
}

void
model_set_redo_status_callback(model_t *m, undo_callback_func_t *f, void *user_data)
{
	m->redo_status_cb = f;
	m->redo_status_user_data = user_data;
}


