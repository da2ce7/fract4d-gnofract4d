/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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

#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <stdlib.h>

#include <gnome.h>

#include "model.h"
#include "gf4d_fractal.h"
#include "gundo.h"
#include "gundo_ui.h"
#include "fract.h"

#include <iosfwd>
#include <fstream>

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
    GSList *explore_only_widgets;
    GSList *explore_sensitive_widgets;
    GtkWidget *topWidget;
    GtkWidget *app;
    fractal *old_fract;

    bool explore_mode;
    double weirdness;

    bool commandInProgress;

    char *saveFileName;
    bool quitWhenDone;

    int nCalcThreads;

    // image dimensions
    int width;
    int height;

    Gf4dMovie *movie;
};

void model_get_dimensions(model_t *m, int *pWidth, int *pHeight)
{
    g_assert(m && pWidth && pHeight);
    *pWidth = m->width;
    *pHeight = m->height;
}

static void model_resize_widget(model_t *m)
{
    g_assert(m);
    
    // resize widget if it exists (we won't have one if
    // we're being called by the arg-parsing stuff)
    if(m->topWidget)
    {        
        // +2 to account for padding in table
        gtk_widget_set_usize(m->topWidget,m->width+2,m->height+2);
    }
}

void model_set_dimensions(model_t *m, int width, int height)
{
    if(m->width == width && m->height == height) return;
    m->width = width;
    m->height = height;
    model_resize_widget(m);
}

void model_set_width(model_t *m, int width)
{
    if(width == m->width) return;

    m->width = width;
    model_resize_widget(m);
}

void model_set_height(model_t *m, int height)
{
    if(height == m->height) return;

    m->height = height;
    model_resize_widget(m);
}

void model_set_top_widget(model_t *m, GtkWidget *widget, GtkWidget *app)
{
    m->topWidget = widget;
    m->app = app;

    model_resize_widget(m);
}

GtkWidget *model_get_app(model_t *m)
{
    return m->app;
}

void model_status_callback(Gf4dFractal *f, gint val, model_t *m)
{
    /* we're only interesting in DONE events at the moment */
    switch(val)
    {
    case GF4D_FRACTAL_DONE: 
        if(m->saveFileName) {
            model_cmd_save_image(m, m->saveFileName);
        }
        if(m->quitWhenDone) {
            exit(0);
        }
        break;
    default:
        // do nothing
        ;
    }

}

void model_set_quit(model_t *m, int quit)
{
    m->quitWhenDone = (bool)quit;
}

void model_set_save_file(model_t *m, char *filename)
{
    m->saveFileName = g_strdup(filename);
}

static void 
model_restore_old_fractal(gpointer undo_data)
{
    undo_action_data *p = (undo_action_data *)undo_data;
    model_set_cmd_in_progress(p->m,true);
    gf4d_fractal_set_fract(p->m->fract, p->old);
    gf4d_fractal_parameters_changed(p->m->fract);
    model_update_subfracts(p->m);	
    model_set_cmd_in_progress(p->m,false);
}

void model_set_cmd_in_progress(model_t *m, int val)
{
    m->commandInProgress = (bool)val;
}

static void
model_restore_new_fractal(gpointer undo_data)
{
    undo_action_data *p = (undo_action_data *)undo_data;
    model_set_cmd_in_progress(p->m,true);
    gf4d_fractal_set_fract(p->m->fract, p->new_);
    gf4d_fractal_parameters_changed(p->m->fract);
    model_update_subfracts(p->m);
    model_set_cmd_in_progress(p->m,false);
}

static void
model_free_undo_data(gpointer undo_data)
{
    undo_action_data *p = (undo_action_data *)undo_data;
    //g_print("deleting %x on %x\n",p,pthread_self());
    fract_delete(&(p->old));
    fract_delete(&(p->new_));
    delete p;
    //g_print("done deleting %x\n",p);
}

/* attempt to peek at /proc/cpuinfo, which might conceivably work on Linux, 
   but not on anything else. If it doesn't work, just assume 1 processor */

// FIXME: user should be able to set this value 

static int
model_guess_calc_threads()
{
    std::ifstream cpuinfo("/proc/cpuinfo");
    if(!cpuinfo) return 1;

    int nCPUs = 0;    
    std::string line;

    while(getline(cpuinfo,line))
    {
        if(strncmp(line.c_str(), "processor\t: ", strlen("processor\t: "))==0)
        {
            // we found a processor line
            nCPUs++; 
        }
    }

    // convert 0 to 1 if no CPUs found (maybe some fscker changed /proc)
    return (nCPUs ? nCPUs : 1); 
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
    m->explore_only_widgets = NULL;
    m->explore_sensitive_widgets = NULL;
    model_update_subfracts(m);
    m->undo_seq = gundo_sequence_new();
    m->commandInProgress = false;
    m->saveFileName = NULL;
    m->quitWhenDone = false;

    m->undo_action.undo = model_restore_old_fractal;
    m->undo_action.redo = model_restore_new_fractal;
    m->undo_action.free = model_free_undo_data;

    m->nCalcThreads = model_guess_calc_threads();
    gf4d_fractal_parameters_changed(m->fract);

    m->topWidget=NULL;
    m->width = 640;
    m->height = 480;

    m->movie = GF4D_MOVIE(gf4d_movie_new());
    gf4d_movie_set_output(m->movie, m->fract);
    return m;
}

void
model_delete(model_t **pm)
{
    model_t *m = *pm;
    gtk_object_destroy(GTK_OBJECT(&m->fract));

    free(m->saveFileName);
    delete m;

    *pm = NULL;
}

static gchar *autosave_filename()
{
    return g_concat_dir_and_file(g_get_home_dir(), ".gnome/" PACKAGE "-autosave.fct");
}

int model_write_autosave_file(model_t *m)
{
    gchar *filename = autosave_filename();
    int ret = model_cmd_save(m,filename);
    g_free(filename);

    return ret;
}

int model_load_autosave_file(model_t *m)
{
    gchar *filename = autosave_filename();
    int ret = model_nocmd_load(m,filename);
    g_free(filename);

    return ret;
}

void
model_add_fract_to_movie(model_t *m, Gf4dFractal *f_after)
{
    gf4d_movie_add(m->movie, m->fract, f_after);
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
    if(model_cmd_start(m,"load"))
    {
        ret = model_nocmd_load(m,filename);
        model_cmd_finish(m, "load");
    }
    return ret;
}

int
model_nocmd_load(model_t *m, char *filename)
{
    return gf4d_fractal_load_params(m->fract,filename);
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
    }
}


bool
model_cmd_start(model_t *m, char *msg)
{
    if(m->commandInProgress) return false;

    //g_print("%d> %s\n",pthread_self(), msg);
    model_set_cmd_in_progress(m,true);
    // invoke copy constructor to get original fractal before update
    m->old_fract = gf4d_fractal_copy_fract(m->fract);
    return true;
}

Gf4dFractal *
model_get_fract(model_t *m)
{
    return m->fract;
}

Gf4dMovie   *
model_get_movie(model_t *m)
{
    return m->movie;
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
    if(model_cmd_start(m,"sub"))
    {
        gf4d_fractal_set_fract(m->fract,gf4d_fractal_copy_fract(m->subfracts[num]));
        model_cmd_finish(m, "sub");
    }
}

int
model_get_calcthreads(model_t *m)
{
    return m->nCalcThreads;
}

void
model_set_calcthreads(model_t *m, int n)
{
    m->nCalcThreads = n;
}

void
model_cmd_finish(model_t *m, char *msg)
{
    g_assert(m->commandInProgress);

    undo_action_data *p = new undo_action_data;
    p->m = m;
    p->old = m->old_fract;
    p->new_ = gf4d_fractal_copy_fract(m->fract);

    gundo_sequence_add_action(m->undo_seq, &m->undo_action, p);

    gf4d_fractal_parameters_changed(m->fract);
    model_update_subfracts(m);

    //g_print("%d< %s\n",pthread_self(),msg);
    model_set_cmd_in_progress(m,false);
}

void
model_add_subfract_widget(model_t *m, GtkWidget *widget)
{
    // all we need to do is add it to the list of widgets 
    // which are shown in explore mode
    model_make_explore_visible(m,widget);
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
    m->explore_mode = !m->explore_mode;

    // update explore-only widgets
    GSList *pWidget = m->explore_only_widgets;

    while(pWidget)
    {
        if(m->explore_mode)
        {
            gtk_widget_show_all(GTK_WIDGET(pWidget->data));
        }
        else
        {
            gtk_widget_hide_all(GTK_WIDGET(pWidget->data));
        }
        pWidget = pWidget->next;
    }
    model_update_subfracts(m);

    // update explore-only widgets
    pWidget = m->explore_sensitive_widgets;

    while(pWidget)
    {
        gtk_widget_set_sensitive(GTK_WIDGET(pWidget->data), m->explore_mode);
        pWidget = pWidget->next;
    }
    model_update_subfracts(m);

}

void
model_make_explore_visible(model_t *m, GtkWidget *widget)
{
    m->explore_only_widgets = g_slist_prepend(m->explore_only_widgets, widget);
}

void
model_make_explore_sensitive(model_t *m, GtkWidget *widget)
{
    m->explore_sensitive_widgets = g_slist_prepend(m->explore_sensitive_widgets, widget);
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
    model_update_subfracts(m);
}
