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

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include <gnome.h>
#include <bonobo.h>

#include "model.h"
#include "callbacks.h"
#include "interface.h"
#include "menus.h"
#include "toolbars.h"
#include "drawingareas.h"
#include "gf4d_fractal.h"


gint
key_event(GtkWidget *widget, GdkEventKey *event, gpointer user_data)
{
    model_t *m = (model_t *)user_data;

    param_t axis;
    double dir;
    switch(event->keyval)
    {
    case GDK_Up:
	axis = YCENTER; dir = -0.025;
	break;
    case GDK_Down:
	axis = YCENTER; dir = 0.025;
	break;
    case GDK_Left:
	axis = XCENTER; dir = -0.025;
	break;
    case GDK_Right:
	axis = XCENTER; dir = 0.025;
	break;
    default:
	return 0;
    }

    if(event->state & GDK_CONTROL_MASK)
    { 
	dir *= 10.0;
    }
    if(event->state & GDK_MOD1_MASK)
    {
	if(axis == XCENTER) axis = ZCENTER;
	else axis = WCENTER;
    }

    if(model_cmd_start(m,"key_setpos"))
    {
	Gf4dFractal *f = model_get_fract(m);
	gf4d_fractal_move(f,axis,dir);
	model_cmd_finish(m,"key_setpos");
    }
    
    return 0;
}

void 
hide_dialog_cb(GtkDialog *dialog, gint, gpointer)
{
    gtk_widget_hide(GTK_WIDGET(dialog));
}

GtkWidget *main_app_window = NULL;

GtkWidget *
create_app (model_t *m)
{
    GtkWidget *table;
    GtkWidget *drawing_area;
    GtkWidget *fixed;

    if(main_app_window != NULL)
    {
	return main_app_window;
    }

    GtkWidget *app = gnome_app_new ("Gnofract4D", _("Gnofract4D"));

    gtk_widget_realize(app);

    gnome_app_create_menus_with_data (GNOME_APP (app), menubar1_uiinfo, m);
    //gtk_window_set_policy(GTK_WINDOW(app),true,true,false);
    
    GtkWidget *appbar = gnome_appbar_new(TRUE,TRUE,GNOME_PREFERENCES_NEVER); 
    gtk_widget_show (appbar);
    gnome_app_set_statusbar (GNOME_APP (app), appbar);
    
    GtkWidget *toolbar_move = create_move_toolbar(m, appbar);
    
    gnome_app_add_toolbar(
        GNOME_APP (app), 
        GTK_TOOLBAR(toolbar_move),
        "move",
        BONOBO_DOCK_ITEM_BEH_NORMAL,
        BONOBO_DOCK_TOP,
        1,0,0);
    
    GtkWidget *scrolled_window = NULL;
    scrolled_window = gtk_scrolled_window_new(NULL,NULL);
    gtk_scrolled_window_set_policy(
        GTK_SCROLLED_WINDOW(scrolled_window),
        GTK_POLICY_AUTOMATIC,
        GTK_POLICY_AUTOMATIC);
    gtk_widget_show(scrolled_window);

    // terrible hack to get initial window size roughly right
    gtk_widget_set_size_request(scrolled_window,640+8,480+8);

    table = gtk_table_new (4,4,false);
    
    gtk_widget_show (table);
    
    fixed = gtk_fixed_new();
    gtk_widget_show(fixed);

    gtk_fixed_put(GTK_FIXED(fixed),table,0,0);

    gtk_scrolled_window_add_with_viewport(
        GTK_SCROLLED_WINDOW(scrolled_window), fixed);

    gnome_app_set_contents (GNOME_APP (app), scrolled_window);
    
    model_set_top_widget(m, table, app);
    
    drawing_area = create_drawing_area(m,appbar);
    
    gtk_widget_show_all (drawing_area);

    gtk_table_attach(GTK_TABLE(table),drawing_area,1,3,1,3, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL),
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL),
                     1,1);

    create_sub_drawing_area(m,table,0,0,0);
    create_sub_drawing_area(m,table,1,1,0);
    create_sub_drawing_area(m,table,2,2,0);
    create_sub_drawing_area(m,table,3,3,0);

    create_sub_drawing_area(m,table,4,0,1);
    create_sub_drawing_area(m,table,5,3,1);
    create_sub_drawing_area(m,table,6,0,2);
    create_sub_drawing_area(m,table,7,3,2);

    create_sub_drawing_area(m,table,8,0,3);
    create_sub_drawing_area(m,table,9,1,3);
    create_sub_drawing_area(m,table,10,2,3);
    create_sub_drawing_area(m,table,11,3,3);

    // turn explore mode *off*
    model_toggle_explore_mode(m);
    
    g_signal_connect (
        GTK_OBJECT (app), "delete_event",
        GTK_SIGNAL_FUNC (quit_cb),
        m);
    
    g_signal_connect (
        GTK_OBJECT (app), "destroy_event",
        GTK_SIGNAL_FUNC (quit_cb),
        m);

    g_signal_connect (GTK_OBJECT(app), "key_press_event",
			(GtkSignalFunc) key_event, m);

    main_app_window= app;
    return app;
}


