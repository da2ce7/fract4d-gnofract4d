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

#include <gnome.h>
#include <gdk/gdk.h>

typedef struct {
	model_t *m;
	GtkWidget *f;
} save_cb_data;

typedef struct {
	model_t *m;
	param_t pnum;
	GtkAdjustment *adj;
	gint dir;
} set_cb_data;
		
gboolean
quit_cb                                (GtkWidget       *widget,
                                        gpointer         user_data);

void
new_image_cb                           (GtkMenuItem     *menuitem,
                                        gpointer         user_data);

void
save_image_cb                          (GtkMenuItem     *menuitem,
                                        gpointer         user_data);

void
save_param_cb                          (GtkMenuItem     *menuitem,
                                        gpointer         user_data);

void
load_param_cb                          (GtkMenuItem     *menuitem,
                                        gpointer         user_data);

void
render_to_disk_cb                      (GtkMenuItem     *menuitem,
                                        gpointer         user_data);

void
preferences_cb                         (GtkMenuItem     *menuitem,
                                        gpointer         user_data);

void
about_cb                               (GtkMenuItem     *menuitem,
                                        gpointer         user_data);
void
help_content_cb               			(GtkMenuItem     *menuitem,
                                        gpointer         user_data);
void
save_image_ok_cb                       (GtkButton       *button,
                                        gpointer         user_data);

void
save_param_ok_cb                       (GtkButton       *button,
                                        gpointer         user_data);

void
load_param_ok_cb                       (GtkButton       *button,
                                        gpointer         user_data);

void
full_screen_cb(GtkWidget *widget, gpointer user_data);

void undo_cb(GtkMenuItem *menuitem, gpointer user_data);
void redo_cb(GtkMenuItem *menuitem, gpointer user_data);

void
propertybox_apply                      (GnomePropertyBox *gnomepropertybox,
                                        gint             arg1,
                                        gpointer         user_data);

void
propertybox_help                       (GnomePropertyBox *gnomepropertybox,
                                        gint             arg1,
                                        gpointer         user_data);
void
propertybox_destroy                    (GtkObject *gnomepropertybox, gpointer user_data );

void
mouse_event		               (GtkWidget *widget, 
					GdkEvent *event, 
					gpointer user_data);

void property_box_refresh (model_t *);

gint configure_event(GtkWidget *widget, GdkEventConfigure *event, gpointer user_data);
gint expose_event (GtkWidget *widget, GdkEventExpose *event, gpointer user_data);

double parameter_by_name(GtkWidget *pb, gchar *name);

void do_nothing_cb(GtkButton *button,gpointer user_data);
void set_down_cb(GtkToggleButton *button, gpointer user_data);

void position_set_cb (GtkWidget *widget, gpointer user_data);
void angle_set_cb(GtkAdjustment *adj, gpointer user_data);

gchar *param_by_name(GtkWidget *pb, 
		     gchar *name);


void color_picker_cb(GnomeColorPicker *colorpicker, 
		     guint arg1, guint arg2, guint arg3, guint arg4,
		     gpointer user_data);

void hide_move_toolbar_cb(GtkMenuItem *widget, gpointer user_data);
void hide_main_toolbar_cb(GtkMenuItem *widget, gpointer user_data);
void hide_status_bar_cb(GtkMenuItem *widget, gpointer user_data);

void redraw_callback(Gf4dFractal *gf, gpointer user_data);
void message_callback(Gf4dFractal *gf, gint status, gpointer user_data);
void progress_callback(Gf4dFractal *gf, gfloat progress, gpointer user_data);
void update_callback(Gf4dFractal *gf, GdkEventExpose *ev, gpointer user_data);

void adjustment_update_callback(Gf4dFractal *gf, gpointer user_data);

gint save_session_cb(GnomeClient* client, gint phase, GnomeSaveStyle save_style,
		     gint is_shutdown, GnomeInteractStyle interact_style,
		     gint is_fast, gpointer client_data);

gint quit_session_cb(GnomeClient* client, gpointer client_data);

void color_type_changed(GtkToggleButton *, gpointer user_data);
