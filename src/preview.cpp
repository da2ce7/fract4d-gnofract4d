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
    return GF4D_FRACTAL(g_object_get_data(G_OBJECT(preview), "shadow"));
}

void 
preview_disconnect(GtkWidget *preview, Gf4dFractal *f)
{
    g_signal_handlers_disconnect_matched(
	G_OBJECT(f), 
	G_SIGNAL_MATCH_DATA,
	0, 0, NULL, NULL, (gpointer)preview);
}

GtkWidget*
create_preview_drawing_area(Gf4dFractal *f)
{
    GtkWidget *drawing_area=NULL;
    gtk_widget_push_colormap (gdk_rgb_get_cmap ());
    
    drawing_area = gtk_drawing_area_new();
    gtk_widget_pop_colormap ();

    gtk_widget_set_events (drawing_area, GDK_EXPOSURE_MASK);

    gtk_widget_set_size_request(
        GTK_WIDGET(drawing_area), 
        PREVIEW_SIZE,
        PREVIEW_SIZE);

    /* connect widget signals */
    g_signal_connect (GTK_OBJECT(drawing_area), "expose_event", 
                        (GtkSignalFunc) popup_expose_event, f);

    /* connect fractal object signals */
    g_signal_connect(GTK_OBJECT(f), "status_changed",
                       GTK_SIGNAL_FUNC (preview_status_callback), 
                       drawing_area);

    /* register disconnection - could use _while_alive stuff instead */
    g_signal_connect(GTK_OBJECT(drawing_area), "destroy",
                       GTK_SIGNAL_FUNC (preview_disconnect), f);

    g_object_set_data (G_OBJECT (drawing_area), "shadow", f);

    gf4d_fractal_calc(f,1,AA_NONE);

    return drawing_area;
}

void
preview_refresh_callback(Gf4dFractal *f, Gf4dFractal *shadow)
{
    gf4d_fractal_update_fract(shadow,f);
    gf4d_fractal_calc(shadow,1,AA_NONE);
}

GtkWidget *
create_preview (Gf4dFractal *f)
{
    gf4d_fractal_set_resolution(f,PREVIEW_SIZE, PREVIEW_SIZE);

    GtkWidget *preview = create_preview_drawing_area(f);

    gtk_widget_show_all(preview);

    return preview;
}


