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

#include "fract.h"
#include "colorizer_public.h"

GtkWidget *appbar1;
//GtkWidget *toolbar_move;
GtkWidget *propertybox=NULL;
  
static GnomeUIInfo file1_menu_uiinfo[] =
{
	{
		GNOME_APP_UI_ITEM, N_("Back to _Mandelbrot"),
		NULL,
		new_image_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_HOME,
		0, (enum GdkModifierType)'m', NULL
	},
	{
		GNOME_APP_UI_ITEM, N_("_Save image"),
		NULL,
		save_image_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_SAVE,
		0, (enum GdkModifierType)'s', NULL
	},
	{
		GNOME_APP_UI_ITEM, N_("Save _parameters"),
		NULL,
		save_param_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_SAVE_AS,
		0, (enum GdkModifierType)'p', NULL
	},
	{
		GNOME_APP_UI_ITEM, N_("_Load parameters"),
		NULL,
		load_param_cb, NULL, NULL,
		GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_OPEN,
		0, (enum GdkModifierType)'l', NULL
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

static GnomeUIInfo menubar1_uiinfo[] =
{
	GNOMEUIINFO_MENU_FILE_TREE (file1_menu_uiinfo),
	GNOMEUIINFO_MENU_SETTINGS_TREE (param_tres1_menu_uiinfo),
	GNOMEUIINFO_MENU_HELP_TREE (help1_menu_uiinfo),
	GNOMEUIINFO_END
};

GtkWidget*
create_angle_button(char *label_text, param_t data, model_t *m)
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
			   (GtkSignalFunc)angle_set_cb, pdata );
	
	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)),"parameters_changed",
			   (GtkSignalFunc)adjustment_update_callback, pdata);	
	return angle;
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
create_move_toolbar (model_t *m)
{
	GtkWidget *toolbar;
	GtkWidget *undo_widget;
	GtkWidget *redo_widget;

	toolbar = gtk_toolbar_new(GTK_ORIENTATION_HORIZONTAL, GTK_TOOLBAR_ICONS);

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

	/* connect to model - fatuous */
	model_set_subfract_widget(m,drawing_area,num);

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

GtkWidget *
create_app (model_t *m)
{
	GtkWidget *table;
	GtkWidget *scrolledwindow1;
	GtkWidget *drawing_area;

	GtkWidget *app = gnome_app_new ("Gnofract4D", _("Gnofract4D"));

	gnome_app_create_menus_with_data (GNOME_APP (app), menubar1_uiinfo, m);
	gtk_window_set_policy(GTK_WINDOW(app),true,true,false);

	GtkWidget *toolbar_move = create_move_toolbar(m);

	gnome_app_add_toolbar(GNOME_APP (app), 
			      GTK_TOOLBAR(toolbar_move),
			      "move",
			      GNOME_DOCK_ITEM_BEH_NORMAL,
			      GNOME_DOCK_TOP,
			      1,0,0);

	appbar1 = gnome_appbar_new(TRUE,TRUE,GNOME_PREFERENCES_NEVER); 
	gtk_widget_show (appbar1);
	gnome_app_set_statusbar (GNOME_APP (app), appbar1);

	table = gtk_table_new (3,3,false);
	gtk_widget_show (table);
	gnome_app_set_contents (GNOME_APP (app), table);

	drawing_area = create_drawing_area(m);
	gtk_widget_show (drawing_area);

	gtk_table_attach(GTK_TABLE(table),drawing_area,1,2,1,2, 
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL),
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL),
			 1,1);

	create_sub_drawing_area(m,table,0,0,0);
	create_sub_drawing_area(m,table,1,1,0);
	create_sub_drawing_area(m,table,2,2,0);
	create_sub_drawing_area(m,table,3,0,1);
	create_sub_drawing_area(m,table,4,2,1);
	create_sub_drawing_area(m,table,5,0,2);
	create_sub_drawing_area(m,table,6,1,2);
	create_sub_drawing_area(m,table,7,2,2);
	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)), "parameters_changed",
			   GTK_SIGNAL_FUNC(redraw_callback),
			   m);

	gtk_signal_connect (GTK_OBJECT (app), "delete_event",
			    GTK_SIGNAL_FUNC (quit_cb),
			    NULL);
	gtk_signal_connect (GTK_OBJECT (app), "destroy_event",
			    GTK_SIGNAL_FUNC (quit_cb),
			    m);

	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)),"progress_changed",
			   GTK_SIGNAL_FUNC(progress_callback),
			   appbar1);

	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)),"status_changed",
			   GTK_SIGNAL_FUNC(message_callback),
			   appbar1);
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
				   GTK_OBJECT(f));

	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->cancel_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   GTK_OBJECT(f));

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
				   GTK_OBJECT(f));

	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->cancel_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   GTK_OBJECT(f));

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
				   GTK_OBJECT(f));

	gtk_signal_connect_object (GTK_OBJECT (GTK_FILE_SELECTION(f)->cancel_button),
				   "clicked", 
				   GTK_SIGNAL_FUNC (gtk_widget_destroy),
				   GTK_OBJECT(f));

	return f;

}

void
create_entry_with_label(GtkWidget *propertybox,
			GtkWidget *table,
			GtkTooltips *tooltips,
			int row,
			gchar *label_text,
			Gf4dFractal *shadow,
			GtkSignalFunc set_cb,
			GtkSignalFunc refresh_cb,
			gchar *tip)
{
	GtkWidget *label = gtk_label_new (label_text);
	GtkWidget *combo_entry=gtk_entry_new();

	gtk_table_attach (GTK_TABLE (table), label, 0, 1, row, row+1,
			  (GtkAttachOptions) (0),
			  (GtkAttachOptions) (0), 0, 0);
	gtk_label_set_justify (GTK_LABEL (label), GTK_JUSTIFY_RIGHT);
	gtk_widget_show (label);

	gtk_table_attach (GTK_TABLE (table), combo_entry, 1, 2, row, row+1,
			  (GtkAttachOptions) (GTK_EXPAND | GTK_FILL),
			  (GtkAttachOptions) (0), 0, 0);
	
	gtk_tooltips_set_tip (tooltips, combo_entry, tip, NULL);
	gtk_widget_show (combo_entry);

	gtk_signal_connect(GTK_OBJECT(combo_entry),"focus-out-event",
			   set_cb,
			   shadow);

	gtk_signal_connect(GTK_OBJECT(shadow), "parameters_changed",
			   refresh_cb,
			   combo_entry);
};

void
create_param_entry_with_label(GtkWidget *table,
			      GtkTooltips *tooltips,
			      int row,
			      gchar *label_text,
			      Gf4dFractal *shadow,
			      param_t param,
			      gchar *tip)
{
	GtkWidget *label = gtk_label_new (label_text);
	GtkWidget *combo_entry=gtk_entry_new();

	gtk_table_attach (GTK_TABLE (table), label, 0, 1, row, row+1,
			  (GtkAttachOptions) (0),
			  (GtkAttachOptions) (0), 0, 0);
	gtk_label_set_justify (GTK_LABEL (label), GTK_JUSTIFY_RIGHT);
	gtk_widget_show (label);

	gtk_table_attach (GTK_TABLE (table), combo_entry, 1, 2, row, row+1,
			  (GtkAttachOptions) (GTK_EXPAND | GTK_FILL),
			  (GtkAttachOptions) (0), 0, 0);
	
	gtk_tooltips_set_tip (tooltips, combo_entry, tip, NULL);
	gtk_widget_show (combo_entry);

	gtk_signal_connect(GTK_OBJECT(combo_entry),"focus-out-event",
			   (GtkSignalFunc)set_param_callback,
			   shadow);

	gtk_signal_connect(GTK_OBJECT(shadow), "parameters_changed",
			   (GtkSignalFunc)refresh_param_callback,
			   combo_entry);

	gtk_object_set_data(GTK_OBJECT(combo_entry),"param",GINT_TO_POINTER(param));
};

void
create_propertybox_color_page(GtkWidget *propertybox,
			      GtkWidget *notebook,
			      GtkTooltips *tooltips,
			      Gf4dFractal *shadow)
{
	GtkWidget *vbox;
	GtkWidget *label;
	GtkWidget *table;
	GtkWidget *clabel, *cpicker;
	GtkWidget *cmaplabel;
	GtkWidget *cmapselector;

	vbox = gtk_vbox_new (FALSE, 0);

	gtk_widget_show (vbox);
	gtk_container_add (GTK_CONTAINER (notebook), vbox);

	/* create label for this page */
	label = gtk_label_new(_("Color"));
	gtk_widget_show(label);

	gtk_notebook_set_tab_label (GTK_NOTEBOOK (notebook), 
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 3), label);

	table = gtk_table_new (6, 2, FALSE);
	gtk_widget_show (table);
	gtk_box_pack_start (GTK_BOX (vbox), table, TRUE, TRUE, 0);

	/* create label for color range */
	clabel = gtk_radio_button_new_with_label(NULL,_("Color Range"));
	gtk_widget_show(clabel);
	gtk_tooltips_set_tip (tooltips, clabel, _("Use a range of colors. The effect is interesting but unpredictable."), NULL);

	gtk_table_attach(
		GTK_TABLE(table), 
		clabel,
		0,1,0,1, 
		(GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
		(GtkAttachOptions)0, 
		0, 2);

	/* create color picker widget */
	cpicker = gnome_color_picker_new();
	gtk_widget_show(cpicker);
	gtk_table_attach(GTK_TABLE(table), 
			 cpicker,
			 1,2,0,1,
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
			 (GtkAttachOptions) 0, 
			 0, 2);

	gtk_object_set_data (
		GTK_OBJECT (clabel), 
		"type",
		GINT_TO_POINTER(COLORIZER_RGB));

	gtk_signal_connect (
		GTK_OBJECT(cpicker),"color-set",
		GTK_SIGNAL_FUNC(set_color_callback),
		shadow);

	gtk_signal_connect (
		GTK_OBJECT(shadow),"parameters_changed",
		GTK_SIGNAL_FUNC(refresh_color_callback),
		cpicker);
	
	/* connect clabel widget */
	gtk_signal_connect(GTK_OBJECT(clabel),"toggled",
			   GTK_SIGNAL_FUNC(set_colortype_callback),
			   GTK_OBJECT(shadow));

	gtk_signal_connect(GTK_OBJECT(shadow), "parameters_changed",
			   GTK_SIGNAL_FUNC(refresh_colortype_callback),
			   GTK_OBJECT(clabel));
	
	/* create "color map" radiobutton */
	cmaplabel = gtk_radio_button_new_with_label_from_widget (
		GTK_RADIO_BUTTON(clabel),
		_("Color Map"));
	gtk_widget_show(cmaplabel);
	gtk_table_attach(GTK_TABLE(table), cmaplabel,0,1,1,2, 
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
			 (GtkAttachOptions)0, 
			 0, 2);

	// gtk_tooltips_set_tip (tooltips, cmaplabel, _("Use a predefined palette of colors loaded from a .map file"), NULL);

	gtk_object_set_data(
		GTK_OBJECT (cmaplabel), 
		"type",
		GINT_TO_POINTER(COLORIZER_CMAP));

	gtk_signal_connect(GTK_OBJECT(cmaplabel),"toggled",
		GTK_SIGNAL_FUNC(set_colortype_callback),
		GTK_OBJECT(shadow));

	gtk_signal_connect(GTK_OBJECT(shadow), "parameters_changed",
			   GTK_SIGNAL_FUNC(refresh_colortype_callback),
			   GTK_OBJECT(cmaplabel));

	/* a file selector for loading the .map files */
	cmapselector = gnome_file_entry_new("cmaps",_("Select a color map file"));
	
	gchar *dir = gnome_datadir_file("maps/" PACKAGE  "/");
	
	GtkWidget *entry = gnome_file_entry_gtk_entry(
		GNOME_FILE_ENTRY(cmapselector));
	
	gnome_file_entry_set_default_path(GNOME_FILE_ENTRY(cmapselector), dir);
	gtk_entry_set_text(GTK_ENTRY(entry), _("Default"));
	
	
	g_free(dir);

	gtk_widget_show(cmapselector);
	gtk_table_attach(GTK_TABLE(table), cmapselector,1,2,1,2, 
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
			 (GtkAttachOptions)0, 
			 0, 2);

	gtk_widget_set_sensitive(GTK_WIDGET(cmapselector),FALSE);

	GtkWidget *fentry = gnome_file_entry_gtk_entry(GNOME_FILE_ENTRY(cmapselector));
	gtk_signal_connect(GTK_OBJECT(fentry),
			   "changed",
			   GTK_SIGNAL_FUNC(set_cmap_callback),
			   shadow);

	gtk_signal_connect(GTK_OBJECT(shadow),
			   "parameters_changed",
			   GTK_SIGNAL_FUNC(refresh_cmap_callback),
			   cmapselector);

	GtkWidget *potential = gtk_check_button_new_with_label(_("Continuous Potential"));
	gtk_table_attach(GTK_TABLE(table), potential,0,1,2,3, 
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
			 (GtkAttachOptions)0, 
			 0, 2);

	gtk_signal_connect(GTK_OBJECT(potential),
			   "toggled",
			   GTK_SIGNAL_FUNC(set_potential_callback),
			   shadow);

	gtk_signal_connect(GTK_OBJECT(shadow),
			   "parameters_changed",
			   GTK_SIGNAL_FUNC(refresh_potential_callback),
			   potential);

	gtk_widget_show(potential);
}

void
create_propertybox_general_page(GtkWidget *propertybox, 
				GtkWidget *notebook,
				GtkTooltips *tooltips,
				Gf4dFractal *shadow)
{
	GtkWidget *vbox;
	GtkWidget *table;
	GtkWidget *label;
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


	create_entry_with_label(propertybox, 
				table, 
				tooltips, 
				0,
				_("Width :"),
				shadow,
				(GtkSignalFunc)set_width_callback,
				(GtkSignalFunc)refresh_width_callback,
				_("Image width (in pixels)"));


	create_entry_with_label(propertybox, table, tooltips, 1,
				_("Height :"),
				shadow,
				(GtkSignalFunc)set_height_callback,
				(GtkSignalFunc)refresh_height_callback,
				_("Image height (in pixels)"));

	create_entry_with_label(propertybox, table, tooltips, 2,
				_("Max Iterations :"),
				shadow,
				(GtkSignalFunc)set_maxiter_callback,
				(GtkSignalFunc)refresh_maxiter_callback,
				_("The further you zoom in the larger this needs to be"));

	create_param_entry_with_label(table, tooltips, 3,
				      _("Bailout :"),
				      shadow,
				      BAILOUT,
				      _("Stop iterating points which get further from the origin than this"));


	/* antialias */
	aa_button = gtk_check_button_new_with_label(_("Antialias"));
	gtk_table_attach(GTK_TABLE(table), aa_button, 
			 0,1,4,5,
			 (GtkAttachOptions)0,
			 (GtkAttachOptions)0,
			 0,2);

	gtk_tooltips_set_tip (tooltips, aa_button, 
			      _("If you turn this on the image looks smoother but takes longer to draw"), NULL);

	gtk_widget_show(aa_button);

	gtk_signal_connect (GTK_OBJECT(aa_button),"toggled",
			    GTK_SIGNAL_FUNC(set_aa_callback),
			    (gpointer) shadow);

	gtk_signal_connect (GTK_OBJECT(shadow),"parameters_changed",
			    GTK_SIGNAL_FUNC(refresh_aa_callback),
			    (gpointer) aa_button);

	/* auto-deepen */
	auto_deepen_button = gtk_check_button_new_with_label(_("Auto Deepening"));
	gtk_table_attach(GTK_TABLE(table), auto_deepen_button, 
			 1,2,4,5,
			 (GtkAttachOptions)0,
			 (GtkAttachOptions)0,
			 0,2);

	gtk_tooltips_set_tip (tooltips, auto_deepen_button, 
			      _("Work out how many iterations are required automatically"), NULL);

	gtk_widget_show(auto_deepen_button);

	gtk_signal_connect (GTK_OBJECT(auto_deepen_button),"toggled",
			    GTK_SIGNAL_FUNC(set_autodeepen_callback),
			    (gpointer) shadow);

	gtk_signal_connect (GTK_OBJECT(shadow),"parameters_changed",
			    GTK_SIGNAL_FUNC(refresh_autodeepen_callback),
			    (gpointer) auto_deepen_button);

}

void
create_propertybox_location_page(GtkWidget *propertybox, 
				 GtkWidget *notebook,
				 GtkTooltips *tooltips,
				 Gf4dFractal *shadow)
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

	create_param_entry_with_label(table, tooltips, 0,
				      _("X (Re) :"),
				      shadow,
				      XCENTER,
				      _("This is c.re in z^2 + c"));

	create_param_entry_with_label(table, tooltips, 1,
				      _("Y (Im) :"),
				      shadow,
				      YCENTER,
				      _("This is c.im in z^2 + c"));

	create_param_entry_with_label(table, tooltips, 2,
				      _("Z (Re) :"),
				      shadow,
				      ZCENTER,
				      _("This is z0.re in z^2 + c"));
	create_param_entry_with_label(table, tooltips, 3,
				      _("W (Im) :"),
				      shadow,
				      WCENTER,
				      _("This is z0.im in z^2 + c"));
	create_param_entry_with_label(table, tooltips, 4,
				      _("Size :"),
				      shadow,
				      SIZE,
				      _("Magnitude of image"));

}

void
create_propertybox_angles_page(GtkWidget *propertybox, 
			       GtkWidget *notebook,
			       GtkTooltips *tooltips,
			       Gf4dFractal *shadow)
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

	create_param_entry_with_label(table, tooltips, 0,
				      _("XY :"),
				      shadow,
				      XYANGLE,
				      NULL);
	create_param_entry_with_label(table, tooltips, 1,
				      _("XZ :"),
				      shadow,
				      XZANGLE,
				      NULL);
	create_param_entry_with_label(table, tooltips, 2,
				      _("XW :"),
				      shadow,
				      XWANGLE,
				      NULL);
	create_param_entry_with_label(table, tooltips, 3,
				      _("YZ :"),
				      shadow,
				      YZANGLE,
				      NULL);
	create_param_entry_with_label(table, tooltips, 4,
				      _("YW :"),
				      shadow,
				      YWANGLE,
				      NULL);
	create_param_entry_with_label(table, tooltips, 5,
				      _("ZW :"),
				      shadow,
				      ZWANGLE,
				      NULL);
}

GtkWidget*
create_propertybox (model_t *m)
{
	GtkWidget *notebook;
	GtkWidget *propertybox;
	GtkTooltips *tooltips;
	Gf4dFractal *shadow = gf4d_fractal_copy(model_get_fract(m));
	tooltips = gtk_tooltips_new ();

	propertybox = gnome_property_box_new ();

	notebook = GNOME_PROPERTY_BOX (propertybox)->notebook;
	gtk_widget_show (notebook);
	
	create_propertybox_general_page(propertybox,notebook,tooltips, shadow);
	create_propertybox_location_page(propertybox, notebook, tooltips, shadow);
	create_propertybox_angles_page(propertybox, notebook, tooltips, shadow);
	create_propertybox_color_page(propertybox, notebook, tooltips, shadow);

	gtk_signal_connect (GTK_OBJECT (propertybox), "apply",
			    GTK_SIGNAL_FUNC (propertybox_apply),
			    m);
  
	gtk_signal_connect (GTK_OBJECT (propertybox), "help",
			    GTK_SIGNAL_FUNC (propertybox_help),
			    "preferences.html");

	gtk_signal_connect_object (GTK_OBJECT (propertybox), "destroy",
				   GTK_SIGNAL_FUNC (propertybox_destroy),
				   NULL);

	gtk_signal_connect_object (GTK_OBJECT(shadow),"parameters_changed",
				   GTK_SIGNAL_FUNC(gnome_property_box_changed),
				   GTK_OBJECT(propertybox));

	gtk_object_set_data (GTK_OBJECT (propertybox), "shadow", shadow);
	return propertybox;
}
