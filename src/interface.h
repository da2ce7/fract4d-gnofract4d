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

GtkWidget* create_app (model_t *);
GtkWidget* create_about (void);
GtkWidget* create_save_image (model_t *);
GtkWidget* create_save_param (model_t *);
GtkWidget* create_load_param (model_t *);
GtkWidget* create_propertybox (model_t *);
GtkWidget* create_move_toolbar(model_t *);
GtkWidget* create_main_toolbar(model_t *);
GtkWidget* create_drawing_area(model_t *);

void
create_propertybox_general_page(GtkWidget *propertybox, 
				GtkWidget *notebook,
				GtkTooltips *tooltips);

void
create_propertybox_location_page(GtkWidget *propertybox, 
				 GtkWidget *notebook,
				 GtkTooltips *tooltips);

void
create_propertybox_angles_page(GtkWidget *propertybox, 
			       GtkWidget *notebook,
			       GtkTooltips *tooltips);

void
create_propertybox_color_page(GtkWidget *propertybox,
			      GtkWidget *notebook,
			      GtkTooltips *tooltips);

void
create_entry_with_label(GtkWidget *propertybox,
			      GtkWidget *table,
			      GtkTooltips *tooltips,
			      int row,
			      gchar *label_text,
			      gchar *combo_name,
			      gchar *tip);

GtkWidget* create_angle_button(char *text, int data, model_t *m);
GtkWidget* create_param_slider(char *label_text, int data, model_t *m);

GtkWidget* create_main_toolbar(model_t *m);


