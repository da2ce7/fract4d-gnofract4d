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
#include  <config.h>
#endif

#include "toolbars.h"
#include "callbacks.h"
#include "angles.h"
#include "preview.h"
#include "gf4d_fourway.h"
#include "gf4d_fractal.h"

void 
position_set_cb (GtkWidget *button, gpointer user_data)
{
    set_cb_data *pdata = (set_cb_data *)user_data;

    if(model_cmd_start(pdata->m,"setpos"))
    {
        Gf4dFractal *f = model_get_fract(pdata->m);
        gf4d_fractal_move(f,pdata->pnum,pdata->dir);
        model_cmd_finish(pdata->m,"setpos");
    }
}


void 
explore_cb(GtkWidget *widget, gpointer user_data)
{
    model_t *m = (model_t *)user_data;	
    model_toggle_explore_mode(m);
}

void 
explore_refresh_cb(GtkWidget *widget, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    model_update_subfracts(m);
}

void 
weirdness_cb(GtkAdjustment *adj, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    model_set_weirdness_factor(m,adj->value);
}

void fourway_set_cb (
    Gf4dFourway *fourway, 
    gint deltax, 
    gint deltay, 
    gpointer user_data)
{
    fourway_cb_data *pdata = (fourway_cb_data *)user_data;

    if(model_cmd_start(pdata->m, "angle"))
    {
        Gf4dFractal *f = model_get_fract(pdata->m);
        gf4d_fractal_move(f,pdata->pnum1, deltax / 100.0);
        gf4d_fractal_move(f,pdata->pnum2, deltay / 100.0);

        model_cmd_finish(pdata->m, "angle");
    }
}

void fourway_set_preview_cb (
    Gf4dFourway *fourway, 
    gint deltax, 
    gint deltay, 
    gpointer user_data)
{
    fourway_cb_data *pdata = (fourway_cb_data *)user_data;

    gf4d_fractal_move(pdata->shadow,pdata->pnum1, deltax / 100.0);    
    gf4d_fractal_move(pdata->shadow,pdata->pnum2, deltay / 100.0);
    
    gf4d_fractal_calc(pdata->shadow,1);
}

GtkWidget*
create_param_button(
    char *label_text, 
    param_t x_data, 
    param_t y_data,
    model_t *m, 
    Gf4dFractal *preview)
{
    GtkWidget *fourway = gf4d_fourway_new(label_text);

    fourway_cb_data *pdata = g_new0(fourway_cb_data,1);
    pdata->m = m;
    pdata->pnum1 = x_data;
    pdata->pnum2 = y_data;
    pdata->shadow = preview;
    pdata->fourway = GF4D_FOURWAY(fourway);

    g_signal_connect(GTK_OBJECT(fourway),"value_slightly_changed",
                       (GtkSignalFunc)fourway_set_preview_cb, pdata );

    g_signal_connect(GTK_OBJECT(fourway),"value_changed",
                       (GtkSignalFunc)fourway_set_cb, pdata );

    gtk_widget_show_all(fourway);

    return fourway;
}

void
deepen_now_cb(GtkWidget *button, model_t *m)
{
    if(model_cmd_start(m, "deepen"))
    {
        Gf4dFractal *f = model_get_fract(m);
        int nIters = gf4d_fractal_get_max_iterations(f);
        gf4d_fractal_set_max_iterations(f,nIters * 2);
        model_cmd_finish(m, "deepen");
    }
}

void
create_deepen_widget(GtkToolbar *toolbar, model_t *m)
{
    gchar *filename = gnome_program_locate_file(
	NULL,
	GNOME_FILE_DOMAIN_APP_DATADIR,
	PACKAGE "/pixmaps/deepen_now.png",
	FALSE,
	NULL);

    GtkWidget *deepen_pixmap = gtk_image_new_from_file(filename);

    GtkWidget *deepen_widget = gtk_toolbar_append_item(
        toolbar,_("Deepen"),
        _("Increase the maximum number of iterations"),
        NULL, deepen_pixmap, 
        GTK_SIGNAL_FUNC(deepen_now_cb), m);        

    gtk_widget_show_all(deepen_widget);
}


Gf4dFractal *preview_shadow = NULL;

Gf4dFractal *get_toolbar_preview_fract()
{
    return preview_shadow;
}

void
create_angle_widgets(
    GtkToolbar *toolbar,
    GtkWidget *appbar,
    model_t *m,
    Gf4dFractal *shadow)
{
    gtk_toolbar_append_widget (
        toolbar,
        create_angle_button(_("xy"), XYANGLE, m, appbar, shadow),
        _("XY angle"), NULL);

    gtk_toolbar_append_widget (
        toolbar,
        create_angle_button(_("xz"), XZANGLE, m, appbar, shadow),
        _("XZ angle"), NULL);

    gtk_toolbar_append_widget (
        toolbar,
        create_angle_button(_("xw"), XWANGLE, m, appbar, shadow),
        _("XW angle"), NULL);

    gtk_toolbar_append_widget (
        toolbar,
        create_angle_button(_("yz"), YZANGLE, m, appbar, shadow),
        _("YZ angle"), NULL);

    gtk_toolbar_append_widget (
        toolbar,
        create_angle_button(_("yw"), YWANGLE, m, appbar, shadow),
        _("YW angle"), NULL);

    gtk_toolbar_append_widget (
        toolbar,
        create_angle_button(_("zw"), ZWANGLE, m, appbar, shadow),
        _("ZW angle"), NULL);
}

void
create_undo_widgets(GtkToolbar *toolbar, model_t *m)
{
    /* UNDO */
    GtkWidget *undo_widget = gtk_image_new_from_stock(
        GTK_STOCK_UNDO, GTK_ICON_SIZE_SMALL_TOOLBAR);

    model_make_undo_sensitive(m,undo_widget);

    gtk_toolbar_append_item (
        toolbar, 
        _("Undo"),
        _("Undo the last action"),
        NULL,
        undo_widget,
        (GtkSignalFunc)undo_cb,
        m);

    /* REDO */
    GtkWidget *redo_widget = gtk_image_new_from_stock(
        GTK_STOCK_REDO, GTK_ICON_SIZE_SMALL_TOOLBAR);

    gtk_toolbar_append_item (
        toolbar, 
        _("Redo"),
        _("Redo the last action"),
        NULL,
        redo_widget,
        (GtkSignalFunc)redo_cb,
        m);

    model_make_redo_sensitive(m,redo_widget);
}

void
create_fourway_widgets(GtkToolbar *toolbar, model_t *m, Gf4dFractal *shadow)
{
    gtk_toolbar_append_widget (
        toolbar,
        create_param_button(_("xy"), XCENTER, YCENTER, m, shadow),
        _("XY position"),
        NULL);

    gtk_toolbar_append_widget (
        toolbar,
        create_param_button(_("zw"), ZCENTER, WCENTER, m, shadow),
        _("Y position"),
        NULL);
}

void
create_preview_widget(GtkToolbar *toolbar, Gf4dFractal *shadow)
{
    GtkWidget *preview_widget = create_preview(shadow);

    gtk_toolbar_append_widget (
        toolbar,
        preview_widget,
        _("Preview"),
        NULL);
}

void
create_explore_widgets(GtkToolbar *toolbar, model_t *m)
{
    GtkWidget *explore_widget = gtk_image_new_from_file(
	gnome_program_locate_file(
	    NULL,
	    GNOME_FILE_DOMAIN_APP_DATADIR,
	    PACKAGE "/pixmaps/explorer_mode.png",
	    TRUE,
	    NULL));

    gtk_toolbar_append_item (
        toolbar,
        _("Explore"),
        _("Toggle Explorer mode"),
        NULL,
        explore_widget,
        (GtkSignalFunc)explore_cb,
        m);

    GtkObject *explore_adj = 
        gtk_adjustment_new(0.2, 0.0, 1.0, 0.05, 0.05, 0.0);

    GtkWidget *explore_weirdness = 
        gtk_hscale_new(GTK_ADJUSTMENT(explore_adj));

    gtk_widget_set_size_request(explore_weirdness, 80, 40);
    gtk_range_set_update_policy(GTK_RANGE(explore_weirdness), GTK_UPDATE_DISCONTINUOUS);
    g_signal_connect(
        GTK_OBJECT(explore_adj),
        "value-changed",
        (GtkSignalFunc)weirdness_cb, 
        m);

    gtk_toolbar_append_widget(
        toolbar,
        explore_weirdness,
        _("How different the mutants are in Explore Mode"),
        NULL);

    gtk_widget_show(explore_weirdness);
    model_make_explore_sensitive(m, explore_weirdness);

    GtkWidget *explore_refresh = 
        gtk_image_new_from_stock(GTK_STOCK_REFRESH, GTK_ICON_SIZE_SMALL_TOOLBAR);

    gtk_toolbar_append_item (
        GTK_TOOLBAR(toolbar),
        NULL,
        _("Generate a new set of mutants"),
        NULL,
        explore_refresh,
        (GtkSignalFunc)explore_refresh_cb,
        m);

    gtk_widget_show(explore_refresh);
    model_make_explore_sensitive(m, explore_refresh);
}

GtkWidget*
create_move_toolbar (model_t *m, GtkWidget *appbar)
{
    GtkWidget *toolbar_widget = gtk_toolbar_new();
    // GTK_ORIENTATION_HORIZONTAL, GTK_TOOLBAR_ICONS);
    GtkToolbar *toolbar = GTK_TOOLBAR(toolbar_widget);

    preview_shadow = gf4d_fractal_copy(model_get_fract(m));
    g_signal_connect(
        GTK_OBJECT(model_get_fract(m)),
        "parameters_changed",
        GTK_SIGNAL_FUNC(preview_refresh_callback),
        preview_shadow);

    create_preview_widget(toolbar, preview_shadow);
    gtk_toolbar_append_space(toolbar);

    create_angle_widgets(toolbar, appbar, m, preview_shadow);
    gtk_toolbar_append_space(toolbar);

    create_fourway_widgets(toolbar, m, preview_shadow);
    create_deepen_widget(toolbar, m);
    gtk_toolbar_append_space(toolbar);

    create_undo_widgets(toolbar, m);
    gtk_toolbar_append_space(toolbar);
    
    create_explore_widgets(toolbar, m);

    return toolbar_widget;
}
