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

#include "preview.h"
#include "callbacks.h"
#include "drawingareas.h"

#include <gnome.h>
#include "gf4d_fractal.h"

gint 
popup_expose_event (GtkWidget *widget, GdkEventExpose *event, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);
    redraw_image_rect(widget, gf4d_fractal_get_image(f),
                      event->area.x, event->area.y,
                      event->area.width, event->area.height,
                      gf4d_fractal_get_xres(f));
    return FALSE;
}

static void
preview_status_callback(Gf4dFractal *f, gint val, void *user_data)
{
    if(val != GF4D_FRACTAL_DONE) return;

    GtkWidget *drawing_area = GTK_WIDGET(user_data);
    redraw_image_rect(drawing_area, gf4d_fractal_get_image(f),
                      0, 0,
                      PREVIEW_SIZE, PREVIEW_SIZE,
                      gf4d_fractal_get_xres(f));
    return;
}

Gf4dFractal *
preview_get_shadow(GtkWidget *preview)
{
    return GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(preview), "shadow"));
}

void 
preview_disconnect(GtkWidget *preview, Gf4dFractal *f)
{
    g_print("disconnecting from fractal prior to deletion\n");
    gtk_signal_disconnect_by_data(GTK_OBJECT(f), preview);
}

GtkWidget*
create_preview_drawing_area(Gf4dFractal *f)
{
    GtkWidget *drawing_area=NULL;
    gtk_widget_push_visual (gdk_rgb_get_visual ());
    gtk_widget_push_colormap (gdk_rgb_get_cmap ());
    
    drawing_area = gtk_drawing_area_new();
    gtk_widget_pop_colormap ();
    gtk_widget_pop_visual ();

    gtk_widget_set_events (drawing_area, GDK_EXPOSURE_MASK);

    gtk_drawing_area_size (
        GTK_DRAWING_AREA(drawing_area), 
        PREVIEW_SIZE,
        PREVIEW_SIZE);

    /* connect widget signals */
    gtk_signal_connect (GTK_OBJECT(drawing_area), "expose_event", 
                        (GtkSignalFunc) popup_expose_event, f);

    /* connect fractal object signals */
    gtk_signal_connect(GTK_OBJECT(f), "status_changed",
                       GTK_SIGNAL_FUNC (preview_status_callback), 
                       drawing_area);

    /* register disconnection - could use _while_alive stuff instead */
    gtk_signal_connect(GTK_OBJECT(drawing_area), "destroy",
                       GTK_SIGNAL_FUNC (preview_disconnect), f);

    gtk_object_set_data (GTK_OBJECT (drawing_area), "shadow", f);

    gf4d_fractal_set_aa(f, (e_antialias)0);
    gf4d_fractal_calc(f,1 );

    return drawing_area;
}

void
preview_refresh_callback(Gf4dFractal *f, Gf4dFractal *shadow)
{
    gf4d_fractal_update_fract(shadow,f);
    gf4d_fractal_set_aa(shadow, (e_antialias)0);
    gf4d_fractal_calc(shadow, 1);
}

GtkWidget *
create_preview (Gf4dFractal *f)
{
    gf4d_fractal_set_resolution(f,PREVIEW_SIZE, PREVIEW_SIZE);

    GtkWidget *preview = create_preview_drawing_area(f);

    gtk_widget_show_all(preview);

    return preview;
}


