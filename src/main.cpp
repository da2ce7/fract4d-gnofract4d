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

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include <gnome.h>

#include "model.h"
#include "callbacks.h"
#include "interface.h"
#include "gf4d_fractal.h"

static char *g_param_file = NULL;
static char *g_param_x = NULL;
static int g_param_quit=0;
static char *g_param_save=NULL;

struct poptOption options[] = {
    {
        "params",
        'p',
        POPT_ARG_STRING,
        &g_param_file,
        0,
        N_("Load a parameter file at startup"),
        N_("PARAM.FCT")
    },
    {
        "x",
        'x',
        POPT_ARG_STRING,
        &g_param_x,
        0,
        N_("X Coordinate"),
        N_("2.5768939")
    },
    {
        "save",
        's',
        POPT_ARG_STRING,
        &g_param_save,
        0,
        N_("Save image to this file"),
        N_("IMAGE.PNG")
    },
    {
        "quit",
        'q',
        POPT_ARG_NONE,
        &g_param_quit,
        0,
        N_("Exit after calculating the fractal"),
        NULL
    },
    { NULL, '\0', 0, NULL, 0 , NULL, NULL }
};

int
main (int argc, char *argv[])
{
    GtkWidget *app;
    GnomeClient *client;
    model_t *m;

    g_thread_init(NULL);
    
    bindtextdomain (PACKAGE, PACKAGE_LOCALE_DIR);
    textdomain (PACKAGE);
    
    gnome_init_with_popt_table (PACKAGE, VERSION, argc, argv, options, 0, NULL);

    m = model_new();

    Gf4dFractal *f = model_get_fract(m);
    if(g_param_file) 
    { 
        model_cmd_load(m,g_param_file);        
    }
    if(g_param_x)
    {
        gf4d_fractal_set_param(f, XCENTER, g_param_x);
    }
    if(g_param_save)
    {
        model_set_save_file(m,g_param_save);
    }
    if(g_param_quit)
    {
        model_set_quit(m,true);
    }
    client = gnome_master_client();
    gtk_signal_connect(GTK_OBJECT (client), "save_yourself",
                       GTK_SIGNAL_FUNC( save_session_cb ), m);
    gtk_signal_connect(GTK_OBJECT (client), "die",
                       GTK_SIGNAL_FUNC( quit_session_cb ), m);

    gdk_threads_enter();
    app = create_app (m);
    gtk_widget_show (app);

    gtk_main ();
    gdk_threads_leave();

    return 0;
}

