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
#  include <config.h>
#endif

#include <gnome.h>

#include <iostream>
#include <fstream>
#include <string>

#include "model.h"
#include "callbacks.h"
#include "interface.h"
#include "gf4d_fractal.h"
#include "movie_editor.h"
#include "tls.h"

static int guess_calc_threads(void);

static char *g_param_file = NULL;
static char *g_params[N_PARAMS] = { NULL };
static int g_param_quit=0;
static char *g_param_save=NULL;
static int g_param_r=0;
static int g_param_g=0;
static int g_param_b=0;
static char *g_param_cmap=NULL;
static int g_param_width=0;
static int g_param_height=0;
static int g_param_nThreads= guess_calc_threads();

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
        g_params + XCENTER,
        0,
        N_("X Coordinate"),
        N_("2.5768939")
    },
    {
        "y",
        'y',
        POPT_ARG_STRING,
        g_params + YCENTER,
        0,
        N_("Y Coordinate"),
        N_("1.0020343")
    },
    {
        "z",
        'z',
        POPT_ARG_STRING,
        g_params + ZCENTER,
        0,
        N_("Z Coordinate"),
        N_("0.0002303")
    },
    {
        "w",
        'w',
        POPT_ARG_STRING,
        g_params + WCENTER,
        0,
        N_("W Coordinate"),
        N_("0.1341453")
    },
    {
        "xy",
        'a',
        POPT_ARG_STRING,
        g_params + XYANGLE,
        0,
        N_("XY Angle"),
        N_("4.4265632")
    },
    {
        "xz",
        'b',
        POPT_ARG_STRING,
        g_params + XZANGLE,
        0,
        N_("XZ Angle"),
        N_("1.9782122")
    },
    {
        "xw",
        'c',
        POPT_ARG_STRING,
        g_params + XWANGLE,
        0,
        N_("XW Angle"),
        N_("2.7818281")
    },
    {
        "yz",
        'd',
        POPT_ARG_STRING,
        g_params + YZANGLE,
        0,
        N_("YZ Angle"),
        N_("3.1415926")
    },
    {
        "yw",
        'e',
        POPT_ARG_STRING,
        g_params + YWANGLE,
        0,
        N_("YW Angle"),
        N_("2.4987611")
    },
    {
        "zw",
        'f',
        POPT_ARG_STRING,
        g_params + ZWANGLE,
        0,
        N_("ZW Angle"),
        N_("2.4673331")
    },
    {
        "size",
        'S',
        POPT_ARG_STRING,
        g_params + MAGNITUDE,
        0,
        N_("Size"),
        N_("8.0033211")
    },
    {
        "red",
        'r',
        POPT_ARG_INT,
        &g_param_r,
        0,
        N_("Red component of base color (0-255)"),
        N_("89")
    },
    {
        "green",
        'g',
        POPT_ARG_INT,
        &g_param_g,
        0,
        N_("Green component of base color (0-255)"),
        N_("78")
    },
    {
        "blue",
        'B',
        POPT_ARG_INT,
        &g_param_b,
        0,
        N_("Blue component of base color (0-255)"),
        N_("255")
    },
    {
        "colormap",
        'm',
        POPT_ARG_STRING,
        &g_param_cmap,
        0,
        N_("Filename of colormap file to use"),
        N_("FOO.MAP")
    },
    {
        "width",
        'i',
        POPT_ARG_INT,
        &g_param_width,
        0,
        N_("Image Width"),
        N_("1024")
    },
    {
        "height",
        'j',
        POPT_ARG_INT,
        &g_param_height,
        0,
        N_("Image height"),
        N_("768")
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
    {
        "nthreads",
        'n',
        POPT_ARG_INT,
        &g_param_nThreads,
        0,
        N_("Number of calculation threads to use"),
        N_("1")
    },
    { NULL, '\0', 0, NULL, 0 , NULL, NULL }
};

/* attempt to peek at /proc/cpuinfo, which might conceivably work on Linux, 
   but not on anything else. If it doesn't work, just assume 1 processor */

static int
guess_calc_threads()
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


// execute any command-line arguments
void
apply_arguments(model_t *m)
{
    Gf4dFractal *f = model_get_fract(m);
    if(g_param_file) 
    { 
        model_nocmd_load(m,g_param_file);        
    }
    for(int i = 0; i < N_PARAMS; ++i)
    {
        if(g_params[i])
        {
            gf4d_fractal_set_param(f, (param_t)i, g_params[i]);
        }
    }
    if(g_param_width)
    {
        model_set_width(m,g_param_width);
    }
    if(g_param_height)
    {
        model_set_height(m,g_param_height);
    }
    if(g_param_save)
    {
        model_set_save_file(m,g_param_save);
    }
    if(g_param_quit)
    {
        model_set_quit(m,true);
    }
    model_set_calcthreads(m,g_param_nThreads);
}

int
main (int argc, char *argv[])
{
    GtkWidget *app;
    GnomeClient *client;
    model_t *m;

    g_thread_init(NULL);
    tls_init();

    bindtextdomain (PACKAGE, PACKAGE_LOCALE_DIR);
    textdomain (PACKAGE);
    
    gnome_init_with_popt_table (PACKAGE, VERSION, argc, argv, options, 0, NULL);

    m = model_new();

    apply_arguments(m);

    if(!g_param_file)
    {
        // no filename specified - try to open autosave file
        model_load_autosave_file(m);
    }
    client = gnome_master_client();
    gtk_signal_connect(GTK_OBJECT (client), "save_yourself",
                       GTK_SIGNAL_FUNC( save_session_cb ), m);
    gtk_signal_connect(GTK_OBJECT (client), "die",
                       GTK_SIGNAL_FUNC( quit_session_cb ), m);

    gdk_threads_enter();
    app = create_app (m);
    gtk_widget_show (app);

    //create_movie_editor(NULL,m);

    gtk_main ();
    gdk_threads_leave();

    return 0;
}

