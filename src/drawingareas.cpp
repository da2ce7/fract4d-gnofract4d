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
#include "drawingareas.h"
#include "properties.h"

typedef struct {
    model_t *m;
    int num;
} subfract_cb_data;

/* copy a section of the fractal's image to the screen */
void 
redraw_image_rect(GtkWidget *widget, guchar *img, int x, int y, int width, int height, int image_width)
{
    /* widget may be hidden */
    if(widget->window)
    {
        gdk_draw_rgb_image(
            widget->window,
            widget->style->white_gc,
            x, y, width, height,
            GDK_RGB_DITHER_NONE,
            img + 3*(x + y * image_width) ,
            3*image_width);
    }
}

/* handle a click on a subfractal in explorer mode */
void sub_mouse_event(GtkWidget *widget, GdkEvent *event, gpointer data)
{
    subfract_cb_data *pdata = (subfract_cb_data *)data;
    model_set_subfract(pdata->m, pdata->num);
}

/* handle a click (or other mouse fiddling) on the main fractal */
void mouse_event(GtkWidget *widget, GdkEvent * event, gpointer data)
{	
    model_t *m = (model_t *)data;
    Gf4dFractal *f=model_get_fract(m);

    static int x, y;
    static int new_x,new_y;
    int dy;
    double zoom=2.0;

    switch (event->type) {
	
    case GDK_BUTTON_PRESS:
        if (event->button.button == 1) {
            x = (int)event->button.x;
            y = (int)event->button.y;
            new_x = x ; new_y = y;
        }else if (event->button.button == 2) {
            if(model_cmd_start(m,"button2"))
            {
                gf4d_fractal_flip2julia(
                    f, 
                    (int)event->button.x,
                    (int)event->button.y);
                model_cmd_finish(m,"button2");
            }
        }else if (event->button.button == 3) {
            if(model_cmd_start(m,"button3"))
            {
                gf4d_fractal_relocate(
                    f,
                    (int)event->button.x,
                    (int)event->button.y,
                    (1.0/zoom) );
                model_cmd_finish(m,"button3");
            }
        }
        break;

    case GDK_MOTION_NOTIFY:
        /* inefficiently erase old rectangle by redrawing entire image */
        redraw_image_rect(
            widget,gf4d_fractal_get_image(f),
            0,0,
            gf4d_fractal_get_xres(f), 
            gf4d_fractal_get_yres(f),
            gf4d_fractal_get_xres(f));

        /* draw new one */
        gdk_window_get_pointer(widget->window,
                               &new_x, &new_y,NULL);

        /* correct rectangle to window aspect ratio */
        dy = (int)(abs(new_x - x) * gf4d_fractal_get_ratio(f));
        if(new_y < y) dy = -dy;
        new_y = y + dy;

        gdk_draw_rectangle(widget->window,
                           widget->style->white_gc,
                           0,
                           MIN(x,new_x),MIN(y,new_y),
                           abs(new_x-x), abs(new_y-y));
        break;
    case GDK_BUTTON_RELEASE:
        if(event->button.button==1) {
            double this_zoom;
            /* inefficiently erase old rectangle */
            redraw_image_rect(
                widget,gf4d_fractal_get_image(f),
                0,0,
                gf4d_fractal_get_xres(f),
                gf4d_fractal_get_yres(f),
                gf4d_fractal_get_xres(f));

            /* zoom factor */
            if(x == new_x || y == new_y)
            {
                // user just clicked without dragging mouse - default zoom
                this_zoom=zoom;
            } else {
                // zoom so selected rectangle fills screen
                this_zoom=(double)gf4d_fractal_get_xres(f)/abs(x - new_x);
            }

            /* coords of rectangle midpoint */
            x = (x + new_x)/2;
            y = (y + new_y)/2;

            if(model_cmd_start(m,"button"))
            {
                gf4d_fractal_relocate(f, x, y, this_zoom);
                model_cmd_finish(m,"button");
            }
        }
    default:
        break;

    }
}

gint 
expose_event (GtkWidget *widget, GdkEventExpose *event, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);
    redraw_image_rect(widget, gf4d_fractal_get_image(f),
                      event->area.x, event->area.y,
                      event->area.width, event->area.height,
                      gf4d_fractal_get_xres(f));
    return FALSE;
}

gint 
configure_event(GtkWidget *widget, GdkEventConfigure *event, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);

    gf4d_fractal_set_resolution(f,
                                widget->allocation.width, 
                                widget->allocation.height);
    gf4d_fractal_parameters_changed(f);
    
    return TRUE;
}

void 
update_callback(Gf4dFractal *f, GdkEventExpose *ev, void *user_data)
{
    GtkWidget *drawing_area = GTK_WIDGET(user_data);
    gtk_widget_draw(drawing_area,&(ev->area));
}

void redraw_callback(Gf4dFractal *f, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    propertybox_refresh(m);
    
    int nThreads = model_get_calcthreads(m);
    g_print("drawing with %d threads\n",nThreads);
    gf4d_fractal_calc(f,nThreads);
}

void 
message_callback(Gf4dFractal *f, gint val, void *user_data)
{
    gchar *msg;
    switch(val)
    {
    case GF4D_FRACTAL_DONE: msg = _("finished"); break;
    case GF4D_FRACTAL_DEEPENING: 
        msg = g_strdup_printf(_("deepening(%d iterations)..."), 
                              gf4d_fractal_get_max_iterations(f)); break;
    case GF4D_FRACTAL_ANTIALIASING: msg = _("antialiasing..."); break;
    case GF4D_FRACTAL_CALCULATING: msg = _("calculating..."); break;
    case GF4D_FRACTAL_PAUSED: msg = _("paused"); break;
    default: msg = _("error"); break;
    };
    gnome_appbar_push(GNOME_APPBAR(user_data), msg);
    if(val == GF4D_FRACTAL_DEEPENING)
    {
        g_free(msg);
    }
}

void 
progress_callback(Gf4dFractal *f,gfloat percentage, void *user_data)
{
    gnome_appbar_set_progress(GNOME_APPBAR(user_data),percentage);
}

GtkWidget*
create_drawing_area(model_t *m, GtkWidget *appbar)
{
    GtkWidget *drawing_area=NULL;
    gtk_widget_push_visual (gdk_rgb_get_visual ());
    gtk_widget_push_colormap (gdk_rgb_get_cmap ());
    
    drawing_area = gtk_drawing_area_new();
    gtk_widget_pop_colormap ();
    gtk_widget_pop_visual ();

    gtk_widget_set_events (drawing_area, 
                           GDK_EXPOSURE_MASK |
                           GDK_BUTTON_PRESS_MASK | 
                           GDK_BUTTON_RELEASE_MASK |
                           GDK_BUTTON1_MOTION_MASK |
                           GDK_POINTER_MOTION_HINT_MASK);

    /* connect widget signals */
    gtk_signal_connect (GTK_OBJECT(drawing_area), "expose_event", 
                        (GtkSignalFunc) expose_event, model_get_fract(m));

    gtk_signal_connect (GTK_OBJECT(drawing_area), "configure_event",
                        (GtkSignalFunc) configure_event, model_get_fract(m));

    gtk_signal_connect (GTK_OBJECT(drawing_area), "button_press_event",
                        (GtkSignalFunc) mouse_event, m);

    gtk_signal_connect (GTK_OBJECT(drawing_area), "motion_notify_event",
                        (GtkSignalFunc) mouse_event, m);

    gtk_signal_connect (GTK_OBJECT(drawing_area), "button_release_event",
                        (GtkSignalFunc) mouse_event, m);

    /* connect fractal object signals */
    gtk_signal_connect(GTK_OBJECT(model_get_fract(m)), "image_changed",
                       GTK_SIGNAL_FUNC (update_callback), 
                       drawing_area);

    gtk_signal_connect(
        GTK_OBJECT(model_get_fract(m)), "parameters_changed",
        GTK_SIGNAL_FUNC(redraw_callback),
        m);
    
    gtk_signal_connect(
        GTK_OBJECT(model_get_fract(m)),"progress_changed",
        GTK_SIGNAL_FUNC(progress_callback),
        appbar);
    
    gtk_signal_connect(
        GTK_OBJECT(model_get_fract(m)),"status_changed",
        GTK_SIGNAL_FUNC(message_callback),
        appbar);

    gtk_signal_connect(
        GTK_OBJECT(model_get_fract(m)),"status_changed",
        GTK_SIGNAL_FUNC(model_status_callback),
        m);

    return drawing_area;
}

/* other areas around the edge of the screen in the Explorer */
GtkWidget *
create_sub_drawing_area(model_t *m, GtkWidget *table, int num, int x, int y)
{
    GtkWidget *drawing_area=NULL;
    gtk_widget_push_visual (gdk_rgb_get_visual ());
    gtk_widget_push_colormap (gdk_rgb_get_cmap ());
	
    drawing_area = gtk_drawing_area_new();
    gtk_widget_pop_colormap ();
    gtk_widget_pop_visual ();

    gtk_widget_set_events (drawing_area, 
                           GDK_EXPOSURE_MASK |
                           GDK_BUTTON_PRESS_MASK | 
                           GDK_BUTTON_RELEASE_MASK |
                           GDK_BUTTON1_MOTION_MASK |
                           GDK_POINTER_MOTION_HINT_MASK);

    subfract_cb_data *pdata = new subfract_cb_data;

    pdata->m = m;
    pdata->num = num;

    model_add_subfract_widget(m,drawing_area);

    Gf4dFractal *f = model_get_subfract(m,num);
    /* connect widget signals */
    gtk_signal_connect (GTK_OBJECT(drawing_area), "expose_event", 
                        (GtkSignalFunc) expose_event, 
                        f);
	
    gtk_signal_connect (GTK_OBJECT(drawing_area), "configure_event",
                        (GtkSignalFunc) configure_event, 
                        f);
	
    gtk_signal_connect (GTK_OBJECT(drawing_area), "button_press_event",
                        (GtkSignalFunc) sub_mouse_event, pdata);

    /* connect fractal object signals */
    gtk_signal_connect(GTK_OBJECT(f),
                       "image_changed",
                       GTK_SIGNAL_FUNC (update_callback), 
                       drawing_area);
	
    gtk_signal_connect(GTK_OBJECT(f),
                       "parameters_changed",
                       GTK_SIGNAL_FUNC(redraw_callback),
                       m);

    gtk_widget_show (drawing_area);
    gtk_table_attach(GTK_TABLE(table),drawing_area,x,x+1,y,y+1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL),
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL),
                     1,1);

    return drawing_area;
}
