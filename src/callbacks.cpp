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
#include "fract.h"
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

void position_set_cb (GtkWidget *button, gpointer user_data)
{
	char buf[100];
	double val;
	double size;
	set_cb_data *pdata = (set_cb_data *)user_data;
	Gf4dFractal *f = model_get_fract(pdata->m);
	char *current_val = gf4d_fractal_get_param(f ,pdata->pnum);

	sscanf(current_val,"%lg",&val);
	g_free(current_val);

	current_val = gf4d_fractal_get_param(f,SIZE);
	sscanf(current_val,"%lg",&size);
	g_free(current_val);

	/* z,w have more spectacular visual effects than x,y, 
	   so do them more slowly */
	if(pdata->pnum == XCENTER || pdata->pnum == YCENTER)
	{
		val += size/ 6.0 * pdata->dir;
	}
	else
	{
		val += size/ 12.0 * pdata->dir;
	}
	sprintf(buf,"%g",val);

	model_cmd_start(pdata->m);
	gf4d_fractal_set_param(f,pdata->pnum, buf);
	model_cmd_finish(pdata->m);
}

void angle_set_cb (GtkAdjustment *adj, gpointer user_data)
{
	char buf[100];
	set_cb_data *pdata = (set_cb_data *)user_data;
	sprintf(buf,"%g",adj->value);
	model_cmd_start(pdata->m);
	gf4d_fractal_set_param(model_get_fract(pdata->m),pdata->pnum, buf);
	model_cmd_finish(pdata->m);
}

void adjustment_update_callback(Gf4dFractal *gf, gpointer user_data)
{
	set_cb_data *pdata = (set_cb_data *)user_data;
	gchar *sval = gf4d_fractal_get_param(gf,pdata->pnum);
	gfloat fval;
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
	gtk_widget_show (create_save_image ((model_t *)user_data));
}


void
save_param_cb(GtkMenuItem     *menuitem,
              gpointer         user_data)
{
	gtk_widget_show (create_save_param ((model_t *)user_data));
}


void
load_param_cb(GtkMenuItem     *menuitem,
              gpointer         user_data)
{
	gtk_widget_show (create_load_param ((model_t *)user_data));
}

void
preferences_cb(GtkMenuItem     *menuitem,
               gpointer         user_data)
{
	if (global_propertybox==NULL) {
		global_propertybox = create_propertybox ((model_t *)user_data); 
		property_box_refresh((model_t *)user_data);
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
	model_t *m = (model_t *)user_data;
	int Xres_new,Yres_new;
	double r,g,b,alpha;
	int i;
	GnomeColorPicker *cpicker;
	Gf4dFractal *f;
	GtkWidget *ctype;

	GtkWidget *pb = GTK_WIDGET(gnomepropertybox);
	if (arg1 != -1)
                 return;

	model_cmd_start(m);
	f = model_get_fract(m);
	Gf4dFractal *shadow = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(pb),"shadow"));
	*(f->f) = *(shadow->f);

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
propertybox_destroy (GtkObject *pb, gpointer user_data)
{
	// FIXME: do we need to delete shadow?
	//Gf4dFractal *shadow = GF4D_FRACTAL(gtk_object_get_data(pb, "shadow"));

	global_propertybox=NULL;
}


static void 
redraw_image_rect(GtkWidget *widget, guchar *img, int x, int y, int width, int height, int image_width)
{
	gdk_draw_rgb_image(widget->window,
			   widget->style->white_gc,
			   x, y, width, height,
			   GDK_RGB_DITHER_NONE,
			   img + 3*(x + y * image_width) ,
			   3*image_width);
}

void sub_mouse_event(GtkWidget *widget, GdkEvent *event, gpointer data)
{
	subfract_cb_data *pdata = (subfract_cb_data *)data;
	model_set_subfract(pdata->m, pdata->num);
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
			x = (int)event->button.x;
			y = (int)event->button.y;
			new_x = x ; new_y = y;
		}else if (event->button.button == 2) {
			model_cmd_start(m);
			gf4d_fractal_flip2julia(f, 
				   (int)event->button.x,
				   (int)event->button.y);
			model_cmd_finish(m);
		}else if (event->button.button == 3) {
			model_cmd_start(m);
			gf4d_fractal_relocate(f,
				 (int)event->button.x,
				 (int)event->button.y,
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

void redraw_callback(Gf4dFractal *f, gpointer m)
{
	property_box_refresh((model_t *)m);
	gf4d_fractal_calc(f);
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
	default: msg = _("error"); break;
	};
	gnome_appbar_push((GnomeAppBar *)user_data, msg);
	if(val == GF4D_FRACTAL_DEEPENING)
	{
		g_free(msg);
	}
}

void 
progress_callback(Gf4dFractal *f,gfloat percentage, void *user_data)
{
	gnome_appbar_set_progress((GnomeAppBar *)user_data,percentage);
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
	GtkWidget *propertybox = global_propertybox;

	Gf4dFractal *f = model_get_fract(m);
	int i;
	e_colorizer ctype;
	char *filename;


	if (propertybox!=NULL) {
		GtkWidget *w;

		Gf4dFractal *shadow;
		shadow = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(propertybox),"shadow"));
		// invoke assignment operator to copy entire state of fractal
		*(shadow->f) = *(f->f);
		// shadow updates all widgets 
		gf4d_fractal_parameters_changed(shadow);
		gnome_property_box_set_state(GNOME_PROPERTY_BOX(propertybox),
					     FALSE);
	}	
}

void
set_colortype_callback(GtkToggleButton *button, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);  
	gboolean b_is_set = gtk_toggle_button_get_active(button);
	if(b_is_set)
	{
		e_colorizer type = (e_colorizer)GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(button),"type"));
	
		gf4d_fractal_set_color_type(f,type);
		gf4d_fractal_parameters_changed(f);
	}
}

void
refresh_colortype_callback(Gf4dFractal *f, gpointer user_data)
{
	GtkToggleButton *b = GTK_TOGGLE_BUTTON(user_data);
	e_colorizer type = (e_colorizer)GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(b),"type"));
	if(gf4d_fractal_get_color_type(f) == type)
	{
		gtk_toggle_button_set_active(b,true);
	}
}
void
set_aa_callback(GtkToggleButton *button, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);
	gf4d_fractal_set_aa(f,gtk_toggle_button_get_active(button));
	gf4d_fractal_parameters_changed(f);
}

void
refresh_aa_callback(Gf4dFractal *f, gpointer user_data)
{
	GtkToggleButton *b = GTK_TOGGLE_BUTTON(user_data);
	gtk_toggle_button_set_active(b,gf4d_fractal_get_aa(f));
}

void
set_autodeepen_callback(GtkToggleButton *button, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);
	gf4d_fractal_set_auto(f,gtk_toggle_button_get_active(button));
	gf4d_fractal_parameters_changed(f);
}

void
refresh_autodeepen_callback(Gf4dFractal *f, gpointer user_data)
{
	GtkToggleButton *b = GTK_TOGGLE_BUTTON(user_data);
	gtk_toggle_button_set_active(b,gf4d_fractal_get_auto(f));
}

gboolean 
set_width_callback(GtkEntry *, GdkEventFocus *, gpointer user_data)
{
	// FIXME: doesn't do anything
	return TRUE;
}

void 
refresh_width_callback(Gf4dFractal *f, gpointer user_data)
{
	char buf[80];
	GtkEntry *e = GTK_ENTRY(user_data);
	sprintf(buf,"%d",gf4d_fractal_get_xres(f));
	gtk_entry_set_text(e,buf);
}


gboolean
set_height_callback(GtkEntry *, GdkEventFocus *, gpointer user_data)
{
	// FIXME : doesn't do anything
	return TRUE;
}

void 
refresh_height_callback(Gf4dFractal *f, gpointer user_data)
{
	char buf[80];
	GtkEntry *e = GTK_ENTRY(user_data);
	sprintf(buf,"%d",gf4d_fractal_get_yres(f));
	gtk_entry_set_text(e,buf);
}

gboolean
set_maxiter_callback(GtkEntry *e, GdkEventFocus *, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);
	gchar *s = gtk_entry_get_text(e);
	int niters=0;
	sscanf(s,"%d",&niters);
	if(niters==gf4d_fractal_get_max_iterations(f)) TRUE;

	gf4d_fractal_set_max_iterations(f,niters);
	gf4d_fractal_parameters_changed(f);	
	return TRUE;
}

void 
refresh_maxiter_callback(Gf4dFractal *f, gpointer user_data)
{
	char buf[80];
	GtkEntry *e = GTK_ENTRY(user_data);
	sprintf(buf,"%d",gf4d_fractal_get_max_iterations(f));
	gtk_entry_set_text(e,buf);
}

// ugh!
static param_t 
get_param(GtkEntry *e)
{
	return (param_t)GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(e),"param"));
}

gboolean
set_param_callback(GtkEntry *e, GdkEventFocus *, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);
	param_t param = get_param(e);
	char *text = gtk_entry_get_text(e);
	char *current = gf4d_fractal_get_param(f,param);
	if(strcmp(text,current)) 
	{		
		gf4d_fractal_set_param(f,param,text);
		gf4d_fractal_parameters_changed(f);
	}
	g_free(current);
	return TRUE;
}

void 
refresh_param_callback(Gf4dFractal *f, gpointer user_data)
{
	GtkEntry *e = GTK_ENTRY(user_data);
	param_t param = get_param(e);
	gchar *s = gf4d_fractal_get_param(f,param);
	gtk_entry_set_text(e,s);
	g_free(s);
}


void set_color_callback(GnomeColorPicker *picker, guint r, guint g, guint b, guint alpha, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);
	double dr, dg, db, da;
	gnome_color_picker_get_d(picker,&dr,&dg,&db,&da);
	gf4d_fractal_set_color(f,dr,dg,db);
	gf4d_fractal_parameters_changed(f);
}

void
refresh_color_callback(Gf4dFractal *f, gpointer user_data)
{
	GnomeColorPicker *picker = GNOME_COLOR_PICKER(user_data);
	e_colorizer type = gf4d_fractal_get_color_type(f);
	if(type != COLORIZER_RGB)
	{
		gtk_widget_set_sensitive(GTK_WIDGET(picker),false);
		return;
	}
	gtk_widget_set_sensitive(GTK_WIDGET(picker),true);
	
	gnome_color_picker_set_d(picker, 
				 gf4d_fractal_get_r(f),
				 gf4d_fractal_get_g(f),
				 gf4d_fractal_get_b(f),
				 0.0);

}

void set_cmap_callback(GtkEditable *e, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);

	gchar *s = gf4d_fractal_get_cmap_file(f);
	gchar *new_s = gtk_entry_get_text(GTK_ENTRY(e));
	if(strcmp(s,new_s)!=0)
	{
		gf4d_fractal_set_cmap_file(f,new_s);
		gf4d_fractal_parameters_changed(f);
	}
	g_free(s);
}

void refresh_cmap_callback(Gf4dFractal *f, gpointer user_data)
{
	GnomeFileEntry *selector = GNOME_FILE_ENTRY(user_data);
	GtkEntry *e = GTK_ENTRY(gnome_file_entry_gtk_entry(selector));

	e_colorizer type = gf4d_fractal_get_color_type(f);
	if(type != COLORIZER_CMAP)
	{
		gtk_widget_set_sensitive(GTK_WIDGET(selector),false);
		return;
	}
	gtk_widget_set_sensitive(GTK_WIDGET(selector),true);
	gchar *s = gf4d_fractal_get_cmap_file(f);
	gtk_entry_set_text(e,s);
	g_free(s);
}

void set_potential_callback(GtkToggleButton *button, gpointer user_data)
{
	Gf4dFractal *f = GF4D_FRACTAL(user_data);
	gf4d_fractal_set_potential(f,gtk_toggle_button_get_active(button));
	gf4d_fractal_parameters_changed(f);
}

void refresh_potential_callback(Gf4dFractal *f, gpointer user_data)
{
	GtkToggleButton *b = GTK_TOGGLE_BUTTON(user_data);
	gtk_toggle_button_set_active(b,gf4d_fractal_get_potential(f));
}
