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

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

#include <gnome.h>
#include <gtk/gtk.h>

#include "model.h"
#include "callbacks.h"
#include "interface.h"
#include "support.h"
#include "gf4d_angle.h"

GtkWidget *appbar1;
GtkWidget *app;
GtkWidget *toolbar_move;
GtkWidget *toolbar_main;
GtkWidget *propertybox=NULL;
  
static GnomeUIInfo file1_menu_uiinfo[] =
{
	{
		GNOME_APP_UI_ITEM, N_("Back to _Mandelbrot"),
		NULL,
		new_image_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_HOME,
		0, 'm', NULL
	},
	{
		GNOME_APP_UI_ITEM, N_("_Save image"),
		NULL,
		save_image_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_SAVE,
		0, 's', NULL
	},
	{
		GNOME_APP_UI_ITEM, N_("Save _parameters"),
		NULL,
		save_param_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_SAVE_AS,
		0, 'p', NULL
	},
	{
		GNOME_APP_UI_ITEM, N_("_Load parameters"),
		NULL,
		load_param_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_OPEN,
		0, 'l', NULL
	},
	GNOMEUIINFO_SEPARATOR,
	GNOMEUIINFO_MENU_EXIT_ITEM (quit_cb, NULL),
	GNOMEUIINFO_END
};

static GnomeUIInfo param_tres1_menu_uiinfo[] =
{
	GNOMEUIINFO_MENU_PREFERENCES_ITEM (preferences_cb, NULL),
	GNOMEUIINFO_END
};

static GnomeUIInfo help1_menu_uiinfo[] =
{
	GNOMEUIINFO_HELP (PACKAGE),
	GNOMEUIINFO_END
};

/* not implemented yet 
static GnomeUIInfo view_menu_uiinfo[] =
{
	GNOMEUIINFO_TOGGLEITEM(N_("Hide/Show Mo_ve Toolbar"),
			       NULL,hide_move_toolbar_cb,NULL),
	GNOMEUIINFO_TOGGLEITEM(N_("Hide/Show _Main Toolbar"),
			       NULL,hide_main_toolbar_cb,NULL),
	GNOMEUIINFO_TOGGLEITEM(N_("Hide/Show _Status Bar"),
			       NULL,hide_status_bar_cb,NULL),
	{
		GNOME_APP_UI_ITEM, N_("_Full Screen"),
		NULL,
		full_screen_cb, NULL, NULL,
		GNOME_APP_PIXMAP_FILENAME, PACKAGE "/full_screen.png",
		0, 'f', NULL
	},


	GNOMEUIINFO_END
};
*/

static GnomeUIInfo menubar1_uiinfo[] =
{
	GNOMEUIINFO_MENU_FILE_TREE (file1_menu_uiinfo),
	GNOMEUIINFO_MENU_SETTINGS_TREE (param_tres1_menu_uiinfo),
	/* GNOMEUIINFO_MENU_VIEW_TREE(view_menu_uiinfo), */
	GNOMEUIINFO_MENU_HELP_TREE (help1_menu_uiinfo),
	GNOMEUIINFO_END
};

GtkWidget*
create_angle_button(char *label_text, int data, model_t *m)
{
	GtkWidget *angle;
	GtkAdjustment *adjustment;
	set_cb_data *pdata;

	adjustment = GTK_ADJUSTMENT(gtk_adjustment_new(0, 0.0, M_PI * 2.0, 0.01, 0.01, 0));
	angle = gf4d_angle_new(adjustment);
	gf4d_angle_set_update_policy(GF4D_ANGLE(angle),GTK_UPDATE_DISCONTINUOUS);
	gf4d_angle_set_label(GF4D_ANGLE(angle),label_text);

	pdata = g_new0(set_cb_data,1);
	pdata->m = m;
	pdata->pnum = data;
	pdata->adj = adjustment;

	gtk_widget_show(angle);
	
	gtk_signal_connect(GTK_OBJECT(adjustment),"value_changed",
			   set_cb, pdata );
	
	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)),"parameters_changed",
			   adjustment_update_callback, pdata);	
	return angle;
}

GtkWidget*
create_param_slider(char *label_text, int data, model_t *m)
{
	GtkWidget *angle;
	GtkAdjustment *adjustment;
	set_cb_data *pdata;

	adjustment = GTK_ADJUSTMENT(gtk_adjustment_new(0, -2.0, 2.0, 0.01, 0.01, 0));
	angle = gtk_hscale_new(adjustment);

	pdata = g_new0(set_cb_data,1);
	pdata->m = m;
	pdata->pnum = data;

	gtk_widget_show(angle);
	
	gtk_signal_connect(GTK_OBJECT(adjustment),"value_changed",
			   set_cb, pdata );
			     
	return angle;
}

GtkWidget*
create_main_toolbar(model_t *m)
{
	GtkWidget *toolbar;
	GtkWidget *undo_widget = gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_UNDO);
	GtkWidget *redo_widget = gnome_stock_new_with_icon(GNOME_STOCK_PIXMAP_REDO);

	gtk_widget_set_sensitive(undo_widget,FALSE);
	gtk_widget_set_sensitive(redo_widget,FALSE);

	toolbar = gtk_toolbar_new(GTK_ORIENTATION_HORIZONTAL, GTK_TOOLBAR_ICONS);

	gtk_toolbar_append_item (GTK_TOOLBAR(toolbar), 
				 _("Undo"),
				 _("Undo the last action"),
				 NULL,
				 undo_widget,
				 undo_cb,
				 m);

	gtk_toolbar_append_item (GTK_TOOLBAR(toolbar), 
				 _("Undo"),
				 _("Undo the last action"),
				 NULL,
				 redo_widget,
				 redo_cb,
				 m);

	model_set_undo_status_callback(m,undo_status_callback,undo_widget);
	model_set_redo_status_callback(m,undo_status_callback,redo_widget);
	return toolbar;
}

GtkWidget*
create_move_toolbar (model_t *m)
{
	GtkWidget *toolbar;

	toolbar = gtk_toolbar_new(GTK_ORIENTATION_HORIZONTAL, GTK_TOOLBAR_BOTH);

	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_angle_button(_("xy"), XYANGLE, m),
				   _("XY angle"),
				   NULL);

	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_angle_button(_("xz"), XZANGLE, m),
				   _("XZ angle"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_angle_button(_("xw"), XWANGLE, m),
				   _("XW angle"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_angle_button(_("yz"), YZANGLE, m),
				   _("YZ angle"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_angle_button(_("yw"), YWANGLE, m),
				   _("YW angle"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_angle_button(_("zw"), ZWANGLE, m),
				   _("ZW angle"),
				   NULL);
			     
	gtk_toolbar_append_space(GTK_TOOLBAR(toolbar));

	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_param_slider(_("x"), XCENTER, m),
				   _("X position"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_param_slider(_("y"), YCENTER, m),
				   _("Y position"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_param_slider(_("z"), ZCENTER, m),
				   _("Z position"),
				   NULL);
	gtk_toolbar_append_widget (GTK_TOOLBAR(toolbar),
				   create_param_slider(_("w"), WCENTER, m),
				   _("W position"),
				   NULL);

	return toolbar;
}

GtkWidget*
create_drawing_area(model_t *m)
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
			    (GtkSignalFunc) expose_event, m);

	gtk_signal_connect (GTK_OBJECT(drawing_area), "configure_event",
			    (GtkSignalFunc) configure_event, m);

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

	return drawing_area;
}

GtkWidget*
create_app (model_t *m)
{
	GtkWidget *vbox1;
	GtkWidget *scrolledwindow1;
	GtkWidget *drawing_area;

	app = gnome_app_new ("Gnofract4D", _("Gnofract4D"));
	gtk_window_set_policy (GTK_WINDOW (app), TRUE, TRUE, FALSE);

	gnome_app_create_menus_with_data (GNOME_APP (app), menubar1_uiinfo, m);

	toolbar_move = create_move_toolbar(m);
	toolbar_main = create_main_toolbar(m);

	gtk_widget_ref(toolbar_move);
	gtk_widget_ref(toolbar_main);

	gnome_app_add_toolbar(GNOME_APP (app), 
			      GTK_TOOLBAR(toolbar_move),
			      "move",
			      GNOME_DOCK_ITEM_BEH_NORMAL,
			      GNOME_DOCK_TOP,
			      1,0,0);

	gnome_app_add_toolbar(GNOME_APP (app), 
			      GTK_TOOLBAR(toolbar_main),
			      "main",
			      GNOME_DOCK_ITEM_BEH_NORMAL,
			      GNOME_DOCK_TOP,
			      1,1,0);

	appbar1 = gnome_appbar_new (TRUE, TRUE, GNOME_PREFERENCES_NEVER);
	gtk_widget_show (appbar1);
	gnome_app_set_statusbar (GNOME_APP (app), appbar1);

	vbox1 = gtk_vbox_new (FALSE, 0);
	gtk_widget_show (vbox1);
	gnome_app_set_contents (GNOME_APP (app), vbox1);

	scrolledwindow1 = gtk_scrolled_window_new (NULL, NULL);
	gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolledwindow1),
				       GTK_POLICY_AUTOMATIC,
				       GTK_POLICY_AUTOMATIC);

	drawing_area = create_drawing_area(m);
	gtk_widget_show (drawing_area);

	/* the scrolledwindow seems to produce a 2-pixel border around the 
	 * drawing area */
	gtk_widget_set_usize(GTK_WIDGET(scrolledwindow1),640+4,480+4);

	gtk_container_set_border_width(GTK_CONTAINER(scrolledwindow1),0);
	gtk_widget_show (scrolledwindow1);

	gtk_box_pack_start (GTK_BOX (vbox1), scrolledwindow1, TRUE, TRUE, 0);


	gtk_scrolled_window_add_with_viewport (GTK_SCROLLED_WINDOW (scrolledwindow1),
					       drawing_area);


	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)), "progress_changed",
			   GTK_SIGNAL_FUNC (progress_callback),
			   appbar1);

	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)), "status_changed",
			   GTK_SIGNAL_FUNC (message_callback),
			   appbar1);

	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)), "parameters_changed",
			   GTK_SIGNAL_FUNC(redraw_callback),
			   m);

	/* FIXME: causes an endless loop
	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)), "parameters_changed",
			   GTK_SIGNAL_FUNC(resize_callback),
			   scrolledwindow1);
	*/
	gtk_signal_connect (GTK_OBJECT (app), "delete_event",
			    GTK_SIGNAL_FUNC (quit_cb),
			    NULL);
	gtk_signal_connect (GTK_OBJECT (app), "destroy_event",
			    GTK_SIGNAL_FUNC (quit_cb),
			    m);

	return app;
}

GtkWidget*
create_save_image (model_t *m)
{
	GtkWidget *f;
	save_cb_data *pdata = g_new0(save_cb_data,1);

	f = gtk_file_selection_new(_("Save Image as"));

	gtk_file_selection_set_filename(GTK_FILE_SELECTION(f), _("image.png"));
	
	pdata->f = f;
	pdata->m = m;
	gtk_signal_connect (GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
                             "clicked", GTK_SIGNAL_FUNC (save_image_ok_cb), pdata);
                             
	/* Ensure that the dialog box is destroyed when the user clicks a button. */
     
	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   (gpointer)f);

	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->cancel_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   (gpointer)f);

	return f;
}

GtkWidget*
create_save_param (model_t *m)
{
	GtkWidget *f;
	save_cb_data *pdata = g_new0(save_cb_data,1);

	f = gtk_file_selection_new(_("Save Parameters as"));
	
	gtk_file_selection_set_filename(GTK_FILE_SELECTION(f), _("param.fct"));

	pdata->f = f;
	pdata->m = m;
	gtk_signal_connect (GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
                             "clicked", GTK_SIGNAL_FUNC (save_param_ok_cb), pdata);
                             
	/* Ensure that the dialog box is destroyed when the user clicks a button. */
     
	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   (gpointer)f);

	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->cancel_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   (gpointer)f);

	return f;
}

GtkWidget*
create_load_param (model_t *m)
{
	GtkWidget *f;
	save_cb_data *pdata = g_new0(save_cb_data,1);

	f = gtk_file_selection_new(_("Load Parameters"));

	gtk_file_selection_set_filename(GTK_FILE_SELECTION(f), _("param.fct"));
	
	pdata->f = f;
	pdata->m = m;
	gtk_signal_connect (GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
                             "clicked", GTK_SIGNAL_FUNC (load_param_ok_cb), pdata);
                             
	/* Ensure that the dialog box is destroyed when the user clicks a button. */
     
	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   (gpointer)f);

	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->cancel_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   (gpointer)f);

	return f;

}

void
create_entry_with_label(GtkWidget *propertybox,
			GtkWidget *table,
			GtkTooltips *tooltips,
			int row,
			gchar *label_text,
			gchar *combo_name,
			gchar *tip)
{
	GtkWidget *label = gtk_label_new (label_text);
	GtkWidget *combo_entry=gtk_entry_new();

	gtk_table_attach (GTK_TABLE (table), label, 0, 1, row, row+1,
			  (GtkAttachOptions) (0),
			  (GtkAttachOptions) (0), 0, 0);
	gtk_label_set_justify (GTK_LABEL (label), GTK_JUSTIFY_RIGHT);
	gtk_widget_show (label);
	gtk_widget_show (combo_entry);
	gtk_table_attach (GTK_TABLE (table), combo_entry, 1, 2, row, row+1,
			  (GtkAttachOptions) (GTK_EXPAND | GTK_FILL),
			  (GtkAttachOptions) (0), 0, 0);
		
	gtk_widget_set_name (combo_entry, combo_name);

	gtk_widget_ref (combo_entry);
	gtk_object_set_data_full (GTK_OBJECT (propertybox), 
				  combo_name,
				  combo_entry,
				  (GtkDestroyNotify) gtk_widget_unref);

	gtk_tooltips_set_tip (tooltips, combo_entry, tip, NULL);

	gtk_signal_connect_object (GTK_OBJECT(combo_entry),"changed",
				   GTK_SIGNAL_FUNC(gnome_property_box_changed),
				   GTK_OBJECT(propertybox));
};

void
create_propertybox_general_page(GtkWidget *propertybox, 
				GtkWidget *notebook,
				GtkTooltips *tooltips)
{
	GtkWidget *vbox;
	GtkWidget *table;
	GtkWidget *label;
	GtkWidget *clabel, *cpicker;
	GtkWidget *aa_button;
	GtkWidget *auto_deepen_button;

	vbox = gtk_vbox_new (FALSE, 0);

	gtk_widget_show (vbox);
	gtk_container_add (GTK_CONTAINER (notebook), vbox);

	table = gtk_table_new (6, 2, FALSE);
	gtk_widget_show (table);
	gtk_box_pack_start (GTK_BOX (vbox), table, TRUE, TRUE, 0);

	label = gtk_label_new (_("Image"));
	gtk_widget_show (label);

	gtk_notebook_set_tab_label (GTK_NOTEBOOK (notebook), 
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 0), label);

	create_entry_with_label(propertybox, table, tooltips, 0,
				_("Width :"),
				"combo_entry_image_width",
				_("Image width (in pixels)"));

	create_entry_with_label(propertybox, table, tooltips, 1,
				_("Height :"),
				"combo_entry_image_height",
				_("Image height (in pixels)"));

	create_entry_with_label(propertybox, table, tooltips, 2,
				_("Max Iterations :"),
				"combo_entry_max_iterations",
				_("The further you zoom in the larger this needs to be"));

	create_entry_with_label(propertybox, table, tooltips, 3,
				_("Bailout :"),
				"combo_entry_bailout",
				_("Stop iterating points which get further from the origin than this"));

	/* antialias */
	aa_button = gtk_check_button_new_with_label(_("Antialias"));
	gtk_table_attach(GTK_TABLE(table), aa_button, 0,1,4,5,0,0,0,2);

	gtk_widget_set_name (aa_button, "checkbutton_antialias");

	gtk_widget_ref (aa_button);
	gtk_object_set_data_full (GTK_OBJECT (propertybox), 
				  "checkbutton_antialias",
				  aa_button,
				  (GtkDestroyNotify) gtk_widget_unref);

	gtk_tooltips_set_tip (tooltips, aa_button, 
			      _("If you turn this on the image looks smoother but takes longer"), NULL);

	gtk_widget_show(aa_button);

	gtk_signal_connect_object (GTK_OBJECT(aa_button),"toggled",
				   GTK_SIGNAL_FUNC(gnome_property_box_changed),
				   GTK_OBJECT(propertybox));

	/* auto-deepen */
	auto_deepen_button = gtk_check_button_new_with_label(_("Auto Deepening"));
	gtk_table_attach(GTK_TABLE(table), auto_deepen_button, 1,2,4,5,0,0,0,2);

	gtk_widget_set_name (auto_deepen_button, "checkbutton_auto_deepen");

	gtk_widget_ref (auto_deepen_button);

	gtk_object_set_data_full (GTK_OBJECT (propertybox), 
				  "checkbutton_auto_deepen",
				  auto_deepen_button,
				  (GtkDestroyNotify) gtk_widget_unref);

	gtk_tooltips_set_tip (tooltips, auto_deepen_button, 
			      _("Work out how many iterations are required automatically"), NULL);

	gtk_widget_show(auto_deepen_button);

	gtk_signal_connect_object (GTK_OBJECT(auto_deepen_button),"toggled",
				   GTK_SIGNAL_FUNC(gnome_property_box_changed),
				   GTK_OBJECT(propertybox));

	clabel = gtk_label_new(_("color"));
	cpicker = gnome_color_picker_new();

	gtk_widget_show(cpicker);
	gtk_widget_show(clabel);

	gtk_table_attach(GTK_TABLE(table), clabel,0,1,5,6, 
			 GTK_EXPAND | GTK_FILL, 0, 0, 2);
	gtk_table_attach(GTK_TABLE(table), cpicker,1,2,5,6,
			 GTK_EXPAND | GTK_FILL, 0, 0, 2);
	gtk_widget_set_name(cpicker, "color_picker");
	gtk_widget_ref (cpicker);
	gtk_object_set_data_full (GTK_OBJECT (propertybox), 
				  "color_picker",
				  cpicker,
				  (GtkDestroyNotify) gtk_widget_unref);

	gtk_signal_connect(GTK_OBJECT(cpicker),"color-set",
			   GTK_SIGNAL_FUNC(color_picker_cb),propertybox);
}

void
create_propertybox_location_page(GtkWidget *propertybox, 
				 GtkWidget *notebook,
				 GtkTooltips *tooltips)
{
	GtkWidget *vbox = gtk_vbox_new (FALSE, 0);
	GtkWidget *table;
	GtkWidget *label;

	gtk_widget_show (vbox);
	gtk_container_add (GTK_CONTAINER (notebook), vbox);

	table = gtk_table_new (5, 2, FALSE);

	gtk_widget_show (table);
	gtk_box_pack_start (GTK_BOX (vbox), table, TRUE, TRUE, 0);

	label = gtk_label_new (_("Location"));
	gtk_widget_show (label);

	gtk_notebook_set_tab_label (GTK_NOTEBOOK (notebook), 
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 1), label);

	create_entry_with_label(propertybox, table, tooltips, 0,
				_("X (Re) :"),
				"combo_entry_xcenter",
				_("This is c.re in z^2 + c"));

	create_entry_with_label(propertybox, table, tooltips, 1,
				_("Y (Im) :"),
				"combo_entry_ycenter",
				_("This is c.im in z^2 + c"));
	create_entry_with_label(propertybox, table, tooltips, 2,
				_("Z (Re) :"),
				"combo_entry_zcenter",
				_("This is z0.re in z^2 + c"));
	create_entry_with_label(propertybox, table, tooltips, 3,
				_("W (Im) :"),
				"combo_entry_wcenter",
				_("This is z0.im in z^2 + c"));
	create_entry_with_label(propertybox, table, tooltips, 4,
				_("Size :"),
				"combo_entry_size",
				_("Magnitude of image"));
}

void
create_propertybox_angles_page(GtkWidget *propertybox, 
			       GtkWidget *notebook,
			       GtkTooltips *tooltips)
{
	GtkWidget *vbox = gtk_vbox_new (FALSE, 0);
	GtkWidget *table;
	GtkWidget *label;

	gtk_widget_show (vbox);
	gtk_container_add (GTK_CONTAINER (notebook), vbox);

	table = gtk_table_new (6, 2, FALSE);

	gtk_widget_show (table);
	gtk_box_pack_start (GTK_BOX (vbox), table, TRUE, TRUE, 0);

	label = gtk_label_new (_("Angles"));
	gtk_widget_show (label);

	gtk_notebook_set_tab_label (GTK_NOTEBOOK (notebook), 
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 2), label);

	create_entry_with_label(propertybox, table, tooltips, 0,
				_("XY :"),
				"combo_entry_xyangle",
				NULL);
	create_entry_with_label(propertybox, table, tooltips, 1,
				_("XZ :"),
				"combo_entry_xzangle",
				NULL);
	create_entry_with_label(propertybox, table, tooltips, 2,
				_("XW :"),
				"combo_entry_xwangle",
				NULL);
	create_entry_with_label(propertybox, table, tooltips, 3,
				_("YZ :"),
				"combo_entry_yzangle",
				NULL);
	create_entry_with_label(propertybox, table, tooltips, 4,
				_("YW :"),
				"combo_entry_ywangle",
				NULL);
	create_entry_with_label(propertybox, table, tooltips, 5,
				_("ZW :"),
				"combo_entry_zwangle",
				NULL);
}

GtkWidget*
create_propertybox (model_t *m)
{
	GtkWidget *notebook;
	GtkWidget *propertybox;
	GtkTooltips *tooltips;
  
	tooltips = gtk_tooltips_new ();

	propertybox = gnome_property_box_new ();
	gtk_widget_set_name (propertybox, "propertybox");
	gtk_object_set_data (GTK_OBJECT (propertybox), "propertybox", propertybox);
	
	notebook = GNOME_PROPERTY_BOX (propertybox)->notebook;
	gtk_widget_show (notebook);
	
	create_propertybox_general_page(propertybox,notebook,tooltips);
	create_propertybox_location_page(propertybox, notebook, tooltips);
	create_propertybox_angles_page(propertybox, notebook, tooltips);

	gtk_signal_connect (GTK_OBJECT (propertybox), "apply",
			    GTK_SIGNAL_FUNC (propertybox_apply),
			    m);
  
	gtk_signal_connect (GTK_OBJECT (propertybox), "help",
			    GTK_SIGNAL_FUNC (propertybox_help),
			    "preferences.html");

	gtk_signal_connect_object (GTK_OBJECT (propertybox), "destroy",
				   GTK_SIGNAL_FUNC (propertybox_destroy),
				   NULL);

                                             
	gtk_object_set_data (GTK_OBJECT (propertybox), "tooltips", tooltips);
  
	return propertybox;
}
