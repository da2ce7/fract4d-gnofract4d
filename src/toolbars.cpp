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

GtkWidget*
create_move_toolbar (model_t *m, GtkWidget *appbar)
{
    GtkWidget *toolbar;
    GtkWidget *undo_widget;
    GtkWidget *redo_widget;

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

    undo_widget = gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_UNDO);
    redo_widget = gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_REDO);

    model_make_undo_sensitive(m,undo_widget);
    model_make_redo_sensitive(m,redo_widget);

    gtk_toolbar_append_item (GTK_TOOLBAR(toolbar), 
                             _("Undo"),
                             _("Undo the last action"),
                             NULL,
                             undo_widget,
                             (GtkSignalFunc)undo_cb,
                             m);

    gtk_toolbar_append_item (GTK_TOOLBAR(toolbar), 
                             _("Redo"),
                             _("Redo the last action"),
                             NULL,
                             redo_widget,
                             (GtkSignalFunc)redo_cb,
                             m);

    gtk_toolbar_append_space(GTK_TOOLBAR(toolbar));

    GtkWidget *explore_widget = gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_SEARCH);
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

    gtk_widget_show(explore_weirdness);
    gtk_toolbar_append_widget(GTK_TOOLBAR(toolbar),
                              explore_weirdness,
                              _("How different the mutants are in Explore Mode"),
                              NULL);

    return toolbar;
}
