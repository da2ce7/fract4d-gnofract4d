/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 2000 Edwin Young
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

void position_set_cb (GtkWidget *button, gpointer user_data)
{
    set_cb_data *pdata = (set_cb_data *)user_data;

    if(model_cmd_start(pdata->m,"setpos"))
    {

        Gf4dFractal *f = model_get_fract(pdata->m);
        gf4d_fractal_move(f,pdata->pnum,pdata->dir);
        model_cmd_finish(pdata->m,"setpos");
    }
}

void undo_cb(GtkMenuItem *menuitem, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    model_undo(m);
}

void redo_cb(GtkMenuItem *menuitem, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    model_redo(m);
}

void explore_cb(GtkWidget *widget, gpointer user_data)
{
    model_t *m = (model_t *)user_data;	
    model_toggle_explore_mode(m);
}

void explore_refresh_cb(GtkWidget *widget, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    model_update_subfracts(m);
}

void weirdness_callback(GtkAdjustment *adj, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    model_set_weirdness_factor(m,adj->value);
}

GtkWidget*
create_param_button(char *label_text, param_t data, model_t *m)
{
    GtkWidget *left_button;
    GtkWidget *right_button;
    GtkWidget *vbox;
    GtkWidget *hbox;
    GtkWidget *label;

    set_cb_data *pdata_left;
    set_cb_data *pdata_right;

    left_button = gtk_button_new_with_label("<<");
    right_button = gtk_button_new_with_label(">>");

    hbox = gtk_hbox_new(1,0);
    gtk_box_pack_start_defaults(GTK_BOX(hbox),left_button);
    gtk_box_pack_start_defaults(GTK_BOX(hbox),right_button);

    vbox = gtk_vbox_new(1,0);
    label = gtk_label_new(label_text);
    gtk_box_pack_start_defaults(GTK_BOX(vbox),label);
    gtk_box_pack_start_defaults(GTK_BOX(vbox),hbox);

    gtk_widget_show(vbox);
    gtk_widget_show(hbox);
    gtk_widget_show(left_button);
    gtk_widget_show(right_button);
    gtk_widget_show(label);

    pdata_left = g_new0(set_cb_data,1);
    pdata_left->m = m;
    pdata_left->pnum = data;
    pdata_left->dir= -1;

    pdata_right = g_new0(set_cb_data,1);
    pdata_right->m = m;
    pdata_right->pnum = data;
    pdata_right->dir = 1;

    gtk_signal_connect(GTK_OBJECT(left_button),"clicked",
                       (GtkSignalFunc)position_set_cb, pdata_left );

    gtk_signal_connect(GTK_OBJECT(right_button),"clicked",
                       (GtkSignalFunc)position_set_cb, pdata_right );
			     
    return vbox;
}

void
pause_status_callback(Gf4dFractal *f, gint val, void *user_data)
{
    GtkWidget *pause_widget = GTK_WIDGET(user_data);
    GtkWidget *pause_pixmap = GTK_BIN(pause_widget)->child;
    switch(val)
    {
    case GF4D_FRACTAL_CALCULATING: 
        //gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(pause_widget), FALSE);
        gtk_widget_set_sensitive(pause_widget, TRUE); 
        break;
    case GF4D_FRACTAL_DONE:
        //gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(pause_widget), FALSE);
        gtk_widget_set_sensitive(pause_widget, FALSE); 
        break;        
    default:
        // do nothing
        ;
    }
}

void
pause_toggled_callback(GtkToggleButton *button, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);
    gf4d_fractal_pause(f,gtk_toggle_button_get_active(button));
}

void
add_pause_widget(GtkWidget *toolbar, model_t *m)
{
    GtkWidget *pause_pixmap = gnome_pixmap_new_from_file(
        gnome_pixmap_file(PACKAGE "/pause.png"));

    GtkWidget *pause_widget = gtk_toggle_button_new();
    gtk_container_add(GTK_CONTAINER(pause_widget),pause_pixmap);

    gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
                               pause_widget,
                               _("Pause"),
                               _("Pause the current calculation"));

    // connect the fractal's stop/start calculation callbacks to 
    // the pause button's sensitivity
    Gf4dFractal *f = model_get_fract(m);

    gtk_signal_connect(GTK_OBJECT(f),
                       "status_changed",
                       (GtkSignalFunc)pause_status_callback,
                       pause_widget);

    // connect the pause button's signal to the fractal
    gtk_signal_connect(GTK_OBJECT(pause_widget),
                       "toggled",
                       (GtkSignalFunc)pause_toggled_callback,
                       f);

    // initially insensitive
    gtk_widget_set_sensitive(pause_widget, FALSE);

    gtk_widget_show_all(pause_widget);
}

GtkWidget*
create_move_toolbar (model_t *m, GtkWidget *appbar)
{
    GtkWidget *toolbar;
    toolbar = gtk_toolbar_new(GTK_ORIENTATION_HORIZONTAL, GTK_TOOLBAR_ICONS);

    gtk_toolbar_append_widget (
        GTK_TOOLBAR(toolbar),
        create_angle_button(_("xy"), XYANGLE, m, appbar),
        _("XY angle"),
        NULL);

    gtk_toolbar_append_widget (
        GTK_TOOLBAR(toolbar),
        create_angle_button(_("xz"), XZANGLE, m, appbar),
        _("XZ angle"),
        NULL);

    gtk_toolbar_append_widget (
        GTK_TOOLBAR(toolbar),
        create_angle_button(_("xw"), XWANGLE, m, appbar),
        _("XW angle"),
        NULL);

    gtk_toolbar_append_widget (
        GTK_TOOLBAR(toolbar),
        create_angle_button(_("yz"), YZANGLE, m, appbar),
        _("YZ angle"),
        NULL);

    gtk_toolbar_append_widget (
        GTK_TOOLBAR(toolbar),
        create_angle_button(_("yw"), YWANGLE, m, appbar),
        _("YW angle"),
        NULL);

    gtk_toolbar_append_widget (
        GTK_TOOLBAR(toolbar),
        create_angle_button(_("zw"), ZWANGLE, m, appbar),
        _("ZW angle"),
        NULL);
			     
    gtk_toolbar_append_space(GTK_TOOLBAR(toolbar));

    gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
                               create_param_button(_("x"), XCENTER, m),
                               _("X position"),
                               NULL);
    gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
                               create_param_button(_("y"), YCENTER, m),
                               _("Y position"),
                               NULL);
    gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
                               create_param_button(_("z"), ZCENTER, m),
                               _("Z position"),
                               NULL);
    gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
                               create_param_button(_("w"), WCENTER, m),
                               _("W position"),
                               NULL);

    gtk_toolbar_append_space(GTK_TOOLBAR(toolbar));

    /* UNDO */
    GtkWidget *undo_widget = gnome_stock_new_with_icon(
        GNOME_STOCK_PIXMAP_UNDO);

    model_make_undo_sensitive(m,undo_widget);

    gtk_toolbar_append_item (GTK_TOOLBAR(toolbar), 
                             _("Undo"),
                             _("Undo the last action"),
                             NULL,
                             undo_widget,
                             (GtkSignalFunc)undo_cb,
                             m);

    /* REDO */
    GtkWidget *redo_widget = gnome_stock_new_with_icon(
        GNOME_STOCK_PIXMAP_REDO);


    gtk_toolbar_append_item (GTK_TOOLBAR(toolbar), 
                             _("Redo"),
                             _("Redo the last action"),
                             NULL,
                             redo_widget,
                             (GtkSignalFunc)redo_cb,
                             m);

    model_make_redo_sensitive(m,redo_widget);

    /* PAUSE */
    add_pause_widget(toolbar, m);

    gtk_toolbar_append_space(GTK_TOOLBAR(toolbar));

    GtkWidget *explore_widget = 
        gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_SEARCH);
    
    gtk_toolbar_append_item (GTK_TOOLBAR(toolbar),
                             _("Explore"),
                             _("Toggle Explorer mode"),
                             NULL,
                             explore_widget,
                             (GtkSignalFunc)explore_cb,
                             m);

    GtkObject *explore_adj = gtk_adjustment_new(0.5, 0.0, 1.0, 0.05, 0.05, 0.0);
    GtkWidget *explore_weirdness = gtk_hscale_new(GTK_ADJUSTMENT(explore_adj));

    gtk_signal_connect(GTK_OBJECT(explore_adj),
                       "value-changed",
                       (GtkSignalFunc)weirdness_callback, 
                       m);

    gtk_toolbar_append_widget(
        GTK_TOOLBAR(toolbar),
        explore_weirdness,
        _("How different the mutants are in Explore Mode"),
        NULL);

    gtk_widget_show(explore_weirdness);
    model_make_explore_sensitive(m, explore_weirdness);

    GtkWidget *explore_refresh = gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_REFRESH);

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

    return toolbar;
}
