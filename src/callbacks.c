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

#include <gnome.h>

#include <math.h>

#include "model.h"
#include "callbacks.h"
#include "interface.h"
#include "support.h"
#include "gf4d_fractal.h"
#include "colorizer_public.h"

GtkWidget *global_propertybox=NULL;
extern GtkWidget *app;
extern GtkWidget *propertybox;
extern GtkWidget *toolbar_move;
extern GtkWidget *toolbar_main;

gint
quit_session_cb(GnomeClient* client, gpointer client_data)
{
	gtk_main_quit();
	return TRUE;
}

gint
save_session_cb(GnomeClient* client, gint phase, GnomeSaveStyle save_style,
		gint is_shutdown, GnomeInteractStyle interact_style,
		gint is_fast, gpointer client_data)
{
	g_print("saving session\n");
	return TRUE;
}

void set_cb (GtkAdjustment *adj, gpointer user_data)
{
	char buf[100];
	set_cb_data *pdata = (set_cb_data *)user_data;
	sprintf(buf,"%g",adj->value);
	g_print("set_cb\n");
	model_cmd_start(pdata->m);
	gf4d_fractal_set_param(model_get_fract(pdata->m),pdata->pnum, buf);
	model_cmd_finish(pdata->m);
}

void adjustment_update_callback(Gf4dFractal *gf, gpointer user_data)
{
	set_cb_data *pdata = (set_cb_data *)user_data;
	gchar *sval = gf4d_fractal_get_param(gf,pdata->pnum);
	gfloat fval;
	g_print("adjustment_cb\n");
	sscanf(sval,"%f",&fval);
	gtk_adjustment_set_value(pdata->adj, fval);

	g_free(sval);
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

void redraw_image_rect(GtkWidget *widget, guchar *img, int x, int y, int width, int height, int image_width);

gboolean
quit_cb(GtkWidget       *widget,
        gpointer         user_data)
{
	model_t *m = (model_t *)user_data;
	gf4d_fractal_interrupt(model_get_fract(m));
	gtk_main_quit();
	return FALSE;
}


void
new_image_cb(GtkMenuItem     *menuitem,
             gpointer         user_data)
{
	model_t *m = (model_t *)user_data;
	model_cmd_start(m);
	gf4d_fractal_reset(model_get_fract(m));
	model_cmd_finish(m);
}


void
save_image_cb(GtkMenuItem     *menuitem,
              gpointer         user_data)
{
	gtk_widget_show (create_save_image (user_data));
}


void
save_param_cb(GtkMenuItem     *menuitem,
              gpointer         user_data)
{
	gtk_widget_show (create_save_param (user_data));
}


void
load_param_cb(GtkMenuItem     *menuitem,
              gpointer         user_data)
{
	gtk_widget_show (create_load_param (user_data));
}

void
preferences_cb(GtkMenuItem     *menuitem,
               gpointer         user_data)
{
	if (global_propertybox==NULL) {
		global_propertybox = create_propertybox (user_data); 
		property_box_refresh(user_data);
		gtk_widget_show(global_propertybox);
	}
}

void
save_image_ok_cb(GtkButton       *button,
                 gpointer         user_data)
{
	save_cb_data *p = (save_cb_data *)user_data;
	char *name;

	GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
	name = gtk_file_selection_get_filename (f);

	model_cmd_save_image(p->m,name);
}


void
save_param_ok_cb(GtkButton       *button,
                 gpointer         user_data)
{
	save_cb_data *p = (save_cb_data *)user_data;
	char *name;
	GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
	name = gtk_file_selection_get_filename (f);
	model_cmd_save(p->m,name);
}


void
load_param_ok_cb(GtkButton       *button,
                 gpointer         user_data)
{
	save_cb_data *p = (save_cb_data *)user_data;
	char *name;
	GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
	name = gtk_file_selection_get_filename (f);
	model_cmd_load(p->m,name);
}

gchar *param_by_name(GtkWidget *pb, 
		      gchar *name)
{
	GtkWidget *gtkentry = lookup_widget(pb,name);
	return g_strdup(gtk_entry_get_text(GTK_ENTRY(gtkentry)));
}
		      
void
propertybox_apply(GnomePropertyBox *gnomepropertybox,
                  gint arg1,
                  gpointer user_data)
{
	// FIXME: get rid of stupid naming thing?
	char *pnames[N_PARAMS] = {
		"combo_entry_bailout",
		"combo_entry_xcenter",
		"combo_entry_ycenter",
		"combo_entry_zcenter",
		"combo_entry_wcenter",
		"combo_entry_size",					   
		"combo_entry_xyangle",
		"combo_entry_xzangle",
		"combo_entry_xwangle",
		"combo_entry_yzangle",
		"combo_entry_ywangle",
		"combo_entry_zwangle"
	};
	model_t *m = (model_t *)user_data;
	int Xres_new,Yres_new;
	double r,g,b,alpha;
	int i;
	GnomeColorPicker *cpicker;
	Gf4dFractal *f;
	GtkWidget *aa, *auto_deepen;
	GtkWidget *ctype;

	GtkWidget *pb = GTK_WIDGET(gnomepropertybox);
	if (arg1 != -1)
                 return;

	model_cmd_start(m);
	f = model_get_fract(m);
	/* FIXME: -ve combo_s? */
	Xres_new = atoi(param_by_name(pb,"combo_entry_image_width"));
	Yres_new = atoi(param_by_name(pb,"combo_entry_image_height"));

	gf4d_fractal_freeze(f);
	gf4d_fractal_set_max_iterations(f,atoi(param_by_name(pb,"combo_entry_max_iterations")));
	for(i = 0; i < N_PARAMS; i++)
	{
		char *s = param_by_name(pb,pnames[i]);
		gf4d_fractal_set_param(f,i,s);
		g_free(s);
	}
	
	aa = lookup_widget(pb,"checkbutton_antialias");
	gf4d_fractal_set_aa(f,(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(aa))));

	auto_deepen = lookup_widget(pb,"checkbutton_auto_deepen");
	gf4d_fractal_set_auto(f,gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(auto_deepen)));

	gf4d_fractal_set_resolution(f,Xres_new,Yres_new);

	cpicker = (GnomeColorPicker *)lookup_widget(pb,"color_picker");
	gnome_color_picker_get_d(cpicker,&r,&g, &b,&alpha);

	ctype = lookup_widget(pb,"rgb_toggle");
	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(ctype)))
	{
		gf4d_fractal_set_color_type(f,COLORIZER_RGB);
		gf4d_fractal_set_color(f,r,g,b);
	}
	else
	{
		/* assume cmap for now */
		char *file = param_by_name(pb, "cmap_entry");
		gf4d_fractal_set_color_type(f,COLORIZER_CMAP);
		gf4d_fractal_set_cmap_file(f,file);
		g_free(file);
	}
	gf4d_fractal_thaw(f);
	model_cmd_finish(m);
}


void
propertybox_help(GnomePropertyBox *gnomepropertybox,
                 gint             arg1,
                 gpointer         user_data)
{
	static GnomeHelpMenuEntry property_help = { PACKAGE ,"preferences.html" };
	gnome_help_display(NULL,&property_help);
}


void
propertybox_destroy (GtkObject *gnomepropertybox, gpointer user_data)
{
	global_propertybox=NULL;
}


void 
redraw_image_rect(GtkWidget *widget, guchar *img, int x, int y, int width, int height, int image_width)
{
	gdk_draw_rgb_image(widget->window,
			   widget->style->white_gc,
			   x, y, width, height,
			   GDK_RGB_DITHER_NONE,
			   img + 3*(x + y * image_width) ,
			   3*image_width);
}

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
			x = event->button.x;
			y = event->button.y;
			new_x = x ; new_y = y;
		}else if (event->button.button == 2) {
			model_cmd_start(m);
			gf4d_fractal_flip2julia(f, 
				   event->button.x,
				   event->button.y);
			model_cmd_finish(m);
		}else if (event->button.button == 3) {
			model_cmd_start(m);
			gf4d_fractal_relocate(f,
				 event->button.x,
				 event->button.y,
				 (1.0/zoom) );
			model_cmd_finish(m);
		}
		break;

	case GDK_MOTION_NOTIFY:
		/* inefficiently erase old rectangle */
		redraw_image_rect(widget,gf4d_fractal_get_image(f),
				  0,0,
				  gf4d_fractal_get_xres(f), 
				  gf4d_fractal_get_yres(f),
				  gf4d_fractal_get_xres(f));
		/* draw new one */
		gdk_window_get_pointer(widget->window,
				       &new_x, &new_y,NULL);

		/* correct rectangle to screen aspect ratio */
		dy = abs(new_x - x) * gf4d_fractal_get_ratio(f);
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
			redraw_image_rect(widget,gf4d_fractal_get_image(f),
					  0,0,
					  gf4d_fractal_get_xres(f),
					  gf4d_fractal_get_yres(f),
					  gf4d_fractal_get_xres(f));

			/* zoom factor */
			if(x == new_x || y == new_y)
			{
				this_zoom=zoom;
			} else {
				this_zoom=(double)gf4d_fractal_get_xres(f)/abs(x - new_x);
			}

			/* coords of rectangle midpoint */
			x = (x + new_x)/2;
			y = (y + new_y)/2;

			model_cmd_start(m);
			gf4d_fractal_relocate(f,
				 x,
				 y,
				 this_zoom);
			model_cmd_finish(m);
		}
	default:
		break;

	}
}

gint 
expose_event (GtkWidget *widget, GdkEventExpose *event, gpointer user_data)
{
	model_t *m = (model_t *)user_data;
	Gf4dFractal *f = model_get_fract(m);
	redraw_image_rect(widget, gf4d_fractal_get_image(f),
			  event->area.x, event->area.y,
			  event->area.width, event->area.height,
			  gf4d_fractal_get_xres(f));
	return FALSE;
}

gint 
configure_event(GtkWidget *widget, GdkEventConfigure *event, gpointer user_data)
{
	model_t *m = (model_t *)user_data;

	gf4d_fractal_set_resolution(model_get_fract(m),
			 widget->allocation.width, 
			 widget->allocation.height);
	gf4d_fractal_parameters_changed(model_get_fract(m));
	return TRUE;
}

void redraw_callback(Gf4dFractal *f, gpointer m)
{
	f = model_get_fract(m);
	property_box_refresh(m);
	gf4d_fractal_calc(f);
}


void 
message_callback(Gf4dFractal *m, gint val, void *user_data)
{
	gchar *msg;
	switch(val)
	{
	case GF4D_FRACTAL_DONE: msg = _("finished"); break;
	case GF4D_FRACTAL_DEEPENING: msg = _("deepening..."); break;
	case GF4D_FRACTAL_ANTIALIASING: msg = _("antialiasing..."); break;
	case GF4D_FRACTAL_CALCULATING: msg = _("calculating..."); break;
	default: msg = _("error"); break;
	};
	gnome_appbar_push((GnomeAppBar *)user_data, msg);
}

static void
toggle_visibility(GtkWidget *item)
{
	if(GTK_WIDGET_VISIBLE(item)) {
		gtk_widget_hide(item);
	} else {
		gtk_widget_show(item);
	}
}

static void
hide_dock_item(char *name)
{
	GtkWidget *dock = GNOME_APP(app)->dock;
	GnomeDockPlacement place;
	guint band,pos,off;
	GnomeDockItem *item = 
		gnome_dock_get_item_by_name(GNOME_DOCK(dock),name,
					    &place,&band,&pos,&off);
	
	toggle_visibility(GTK_WIDGET(item));
}

int g_x;

void
hide_move_toolbar_cb(GtkMenuItem *widget, gpointer user_data)
{
	GtkWidget *dock = GNOME_APP(app)->dock;
	static GnomeDockPlacement place;
	static guint band,pos,off;
	GnomeDockItem *item = 
		gnome_dock_get_item_by_name(GNOME_DOCK(dock),"move",
					    &place,&band,&pos,&off);

	if(item) {
		GnomeDockLayout *layout = gnome_dock_get_layout(GNOME_DOCK(dock));
		g_x = gnome_dock_layout_remove_item_by_name(GNOME_DOCK_LAYOUT(layout),
						      "move");
	} else {
		gnome_app_add_toolbar(GNOME_APP (app), 
				      GTK_TOOLBAR(toolbar_move),
				      "move",
				      GNOME_DOCK_ITEM_BEH_NORMAL,
				      place,
				      band,pos,off);
	}
	gtk_item_toggle(GTK_ITEM(widget));
}

void
hide_main_toolbar_cb(GtkMenuItem *widget, gpointer user_data)
{
	gtk_item_toggle(GTK_ITEM(widget));
	hide_dock_item("main");
}

void
hide_status_bar_cb(GtkMenuItem *widget, gpointer user_data)
{
	gtk_item_toggle(GTK_ITEM(widget));
}

void
full_screen_cb(GtkWidget *widget, gpointer user_data)
{
	static gboolean enlarged=0;
	static int x=0, y=0, w=0, h=0;
	if(enlarged) {
		gdk_window_move_resize(app->window,x,y,w,h);
		enlarged=0;
	} else {
		gdk_window_get_root_origin(app->window,&x,&y);
		gdk_window_get_size(app->window,&w,&h);
		gdk_window_move_resize(app->window,0,0,gdk_screen_width(), gdk_screen_height());
		enlarged=1;
	}
}

void 
progress_callback(Gf4dFractal *f,gfloat percentage, void *user_data)
{
	gnome_appbar_set_progress((GnomeAppBar *)user_data,percentage);

	/* allows interaction during calculation 
	while (gtk_events_pending())
		gtk_main_iteration();
	*/
}

void 
update_callback(Gf4dFractal *f, GdkEventExpose *ev, void *user_data)
{
	GtkWidget *drawing_area = GTK_WIDGET(user_data);
	gtk_widget_draw(drawing_area,&(ev->area));
}

void 
property_box_refresh(model_t *m)
{
	char *combo_names[] = {
		"combo_entry_bailout",
		"combo_entry_xcenter",
		"combo_entry_ycenter",
		"combo_entry_zcenter",
		"combo_entry_wcenter",
		"combo_entry_size",
		"combo_entry_xyangle",
		"combo_entry_xzangle",
		"combo_entry_xwangle",
		"combo_entry_yzangle",
		"combo_entry_ywangle",
		"combo_entry_zwangle"
	};

	GtkWidget *propertybox = global_propertybox;

	Gf4dFractal *f = model_get_fract(m);
	int i;
	e_colorizer ctype;
	char *filename;


	if (propertybox!=NULL) {
		GtkWidget *w;

		w = lookup_widget(propertybox,"combo_entry_image_width");
		gtk_entry_set_text(GTK_ENTRY(w),
				   g_strdup_printf("%d",gf4d_fractal_get_xres(f)));

		w = lookup_widget(propertybox,"combo_entry_image_height");
		gtk_entry_set_text(GTK_ENTRY(w),
				   g_strdup_printf("%d",gf4d_fractal_get_yres(f)));

		w = lookup_widget(propertybox,"combo_entry_max_iterations");
		gtk_entry_set_text(GTK_ENTRY(w),
				   g_strdup_printf("%d",gf4d_fractal_get_max_iterations(f)));

		w = lookup_widget(propertybox,"checkbutton_antialias");
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(w),gf4d_fractal_get_aa(f));

		w = lookup_widget(propertybox,"checkbutton_auto_deepen");
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(w),
					     gf4d_fractal_get_auto(f));
			
		for(i = 0; i < N_PARAMS; i++) {

			w = lookup_widget(propertybox,combo_names[i]);
			gtk_entry_set_text(GTK_ENTRY(w),
					   gf4d_fractal_get_param(f,i));
		}

		ctype = gf4d_fractal_get_color_type(f);
		switch(ctype)
		{
		case COLORIZER_RGB:
			w = lookup_widget(propertybox,"color_picker");
			gnome_color_picker_set_d(GNOME_COLOR_PICKER(w),
						 gf4d_fractal_get_r(f), 
						 gf4d_fractal_get_g(f), 
						 gf4d_fractal_get_b(f), 0.0);
			w = lookup_widget(propertybox, "rgb_toggle");
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(w),1);
			break;
		case COLORIZER_CMAP:
			w = lookup_widget(propertybox, "cmap_toggle");
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(w),1);
			w = lookup_widget(propertybox, "cmap_entry");
			filename = gf4d_fractal_get_cmap_file(f);
			gtk_entry_set_text(GTK_ENTRY(w),filename);
			g_free(filename);
			break;
		default:
		}

		gnome_property_box_set_state(GNOME_PROPERTY_BOX(propertybox),
					     FALSE);
	}	
	
}

void
color_picker_cb(GnomeColorPicker *colorpicker, 
		guint arg1, guint arg2, guint arg3, guint arg4,
		gpointer user_data)
{
	gnome_property_box_changed (GNOME_PROPERTY_BOX(user_data));
}

void
color_type_changed(GtkToggleButton *button, gpointer user_data)
{
	GtkWidget *widget = GTK_WIDGET(user_data); // 
	gboolean b_is_set = gtk_toggle_button_get_active(button);
	gtk_widget_set_sensitive(widget,b_is_set);
}
