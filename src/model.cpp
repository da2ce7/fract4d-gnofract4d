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
#include "gundo.h"
#include "gundo_ui.h"
#include "fract.h"

#ifndef NDEBUG
#define MODEL_HISTORY_DEBUG(_x) model_history_debug(_x)
#else
#define MODEL_HISTORY_DEBUG(_x)
#endif

double zoom=2;

typedef struct {
	model_t *m;
	fractal *old;
	fractal *new_;
} undo_action_data ;

/* real definition */
struct _model {
	GundoSequence *undo_seq;
	GundoActionType undo_action;
	Gf4dFractal *fract;
	Gf4dFractal *subfracts[8];
	GtkWidget *sub_drawing_areas[8];
	fractal *old_fract;

	int interrupted;
	bool explore_mode;
	double weirdness;
};

static void 
model_restore_old_fractal(gpointer undo_data)
{
	undo_action_data *p = (undo_action_data *)undo_data;
	gf4d_fractal_set_fract(p->m->fract, p->old);
	gf4d_fractal_parameters_changed(p->m->fract);
}

static void
model_restore_new_fractal(gpointer undo_data)
{
	undo_action_data *p = (undo_action_data *)undo_data;
	gf4d_fractal_set_fract(p->m->fract, p->new_);
	gf4d_fractal_parameters_changed(p->m->fract);
}

static void
model_free_undo_data(gpointer undo_data)
{
	undo_action_data *p = (undo_action_data *)undo_data;
	fract_delete(&(p->old));
	fract_delete(&(p->new_));
	delete p;
}

model_t *
model_new(void)
{
	model_t *m = new model_t;

	m->fract = GF4D_FRACTAL(gf4d_fractal_new());
	for(int i = 0; i < 8; i++)
	{
		m->subfracts[i] = GF4D_FRACTAL(gf4d_fractal_new());
	}
	m->explore_mode = true;
	m->weirdness = 0.5;
	model_update_subfracts(m);
	m->undo_seq = gundo_sequence_new();

	m->undo_action.undo = model_restore_old_fractal;
	m->undo_action.redo = model_restore_new_fractal;
	m->undo_action.free = model_free_undo_data;

	gf4d_fractal_parameters_changed(m->fract);
	return m;
}

void
model_delete(model_t **pm)
{
	model_t *m = *pm;
	gtk_object_destroy(GTK_OBJECT(&m->fract));
	delete m;
	*pm = NULL;
}

int
model_cmd_save_image(model_t *m, char *filename)
{
	GdkImlibImage *image;
	image = gdk_imlib_create_image_from_data(
		(unsigned char *)gf4d_fractal_get_image(m->fract),
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
	return gf4d_fractal_write_params(m->fract,filename);
}
	
int 
model_cmd_load(model_t *m, char *filename)
{
	int ret;
	model_cmd_start(m);
	ret = gf4d_fractal_load_params(m->fract,filename);
	model_cmd_finish(m);
	return ret;
}

void 
model_undo(model_t *m)
{
	if(gundo_sequence_can_undo(m->undo_seq))
	{
		gundo_sequence_undo(m->undo_seq);
	}
}

void
model_redo(model_t *m)
{
	if(gundo_sequence_can_redo(m->undo_seq))
	{
		gundo_sequence_redo(m->undo_seq);
		gf4d_fractal_parameters_changed(m->fract);
	}
}


void
model_cmd_start(model_t *m)
{
	// invoke copy constructor to get original fractal before update
	m->old_fract = gf4d_fractal_copy_fract(m->fract);
}

Gf4dFractal *
model_get_fract(model_t *m)
{
	return m->fract;
}

Gf4dFractal *
model_get_subfract(model_t *m, int num)
{
	g_assert(num > -1 && num < 8);
	return m->subfracts[num];
}

void
model_set_subfract(model_t *m, int num)
{
	model_cmd_start(m);
	gf4d_fractal_set_fract(m->fract,gf4d_fractal_copy_fract(m->subfracts[num]));
	model_cmd_finish(m);
}

void
model_cmd_finish(model_t *m)
{
	undo_action_data *p = new undo_action_data;

	p->m = m;
	p->old = m->old_fract;
	p->new_ = gf4d_fractal_copy_fract(m->fract);

	gundo_sequence_add_action(m->undo_seq, &m->undo_action, p);

	gf4d_fractal_parameters_changed(m->fract);
	model_update_subfracts(m);
}

void
model_set_subfract_widget(model_t *m, GtkWidget *widget, int num)
{
	m->sub_drawing_areas[num] = widget;
}

void
model_update_subfracts(model_t *m)
{
	if(!m->explore_mode) return;

	for(int i = 0; i < 8; i++)
	{
		gf4d_fractal_set_inexact(m->subfracts[i],m->fract,m->weirdness);
		gf4d_fractal_parameters_changed(m->subfracts[i]);
	}
}

void 
model_toggle_explore_mode(model_t *m)
{
	if(m->explore_mode)
	{
		for(int i = 0; i < 8; i++)
		{
			gtk_widget_hide(m->sub_drawing_areas[i]);
		}
	}
	else
	{
		for(int i = 0; i < 8; i++)
		{
			gtk_widget_show(m->sub_drawing_areas[i]);
		}
	}
	m->explore_mode = !m->explore_mode;
	model_update_subfracts(m);
}

void
model_make_undo_sensitive(model_t *m, GtkWidget *widget)
{
	gundo_make_undo_sensitive(widget,m->undo_seq);
}

void
model_make_redo_sensitive(model_t *m, GtkWidget *widget)
{
	gundo_make_redo_sensitive(widget,m->undo_seq);
}


void
model_set_weirdness_factor(model_t *m, gfloat weirdness)
{
	m->weirdness = weirdness;
}
