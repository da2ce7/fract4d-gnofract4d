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
#  include <config.h>
#endif

#include "properties.h"
#include "callbacks.h"

#include <gnome.h>
#include "gf4d_fractal.h"
#include <cstdlib>

GtkWidget *global_propertybox=NULL;


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
			  (GtkAttachOptions) (GTK_FILL),
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


void set_bailout_callback(GtkWidget *widget, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);

    e_bailFunc type = (e_bailFunc)GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(widget),"type"));

    e_bailFunc old_type = gf4d_fractal_get_bailout_type(f);
    if(type != old_type)
    {
        gf4d_fractal_set_bailout_type(f,type);
        gf4d_fractal_parameters_changed(f);
    }
}

void refresh_bailout_callback(Gf4dFractal *f, gpointer user_data)
{
    GtkOptionMenu *om = GTK_OPTION_MENU(user_data);
    GtkWidget *m = gtk_option_menu_get_menu(om);

    GList *list = gtk_container_children(GTK_CONTAINER(m));
    int index=0;
    e_bailFunc bailType = gf4d_fractal_get_bailout_type(f);

    // find an element with the same bailtype as the one the fractal has
    while(list)
    {
        GtkMenuItem *mi = GTK_MENU_ITEM(list->data);
        e_bailFunc t = (e_bailFunc)GPOINTER_TO_INT(
            gtk_object_get_data(GTK_OBJECT(mi),"type"));
        
        if(t == bailType)
        {
            gtk_option_menu_set_history(om,index);
            return;
        }
        list = g_list_next(list);
        index++;
    }
    g_warning(_("Unknown bailout type ignored"));
}

GtkWidget *create_bailout_menu(Gf4dFractal *shadow)
{
    GtkWidget *bailout_type = gtk_option_menu_new();
    GtkWidget *bailout_menu = gtk_menu_new();

    static const gchar *bailout_names[] = 
    {
        N_("Magnitude"),
        N_("Manhattan Distance"),
        N_("Manhattan Variant"),
        N_("Or"),
        N_("And")
    };

    for(int i=0; i < sizeof(bailout_names)/sizeof(bailout_names[0]); ++i)
    {
        GtkWidget *menu_item = gtk_menu_item_new_with_label(bailout_names[i]);
    
        gtk_object_set_data(
            GTK_OBJECT (menu_item), 
            "type",
            GINT_TO_POINTER((e_bailFunc)i));
    
        gtk_signal_connect(
            GTK_OBJECT(menu_item),
            "activate",
            GTK_SIGNAL_FUNC(set_bailout_callback),
            shadow);
    
        gtk_menu_append(GTK_MENU(bailout_menu), menu_item);
        gtk_widget_show(menu_item);
        gtk_option_menu_set_menu(GTK_OPTION_MENU(bailout_type), bailout_menu);
    }    

    // refresh when shadow changes
    gtk_signal_connect(
        GTK_OBJECT(shadow),
        "parameters_changed",
        GTK_SIGNAL_FUNC(refresh_bailout_callback),
        bailout_type);

    return bailout_type;
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
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 0), label);

	table = gtk_table_new (6, 3, FALSE);
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

        // bailout type
        GtkWidget *bailout_label= gtk_label_new(_("Bailout Function"));
        gtk_widget_show(bailout_label);
        gtk_table_attach(GTK_TABLE(table), bailout_label, 0,1,2,3, 
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
			 (GtkAttachOptions)0, 
			 0, 2);
        
        GtkWidget *bailout_type = create_bailout_menu(shadow);

        gtk_widget_show(bailout_type);

        gtk_table_attach(GTK_TABLE(table), bailout_type ,1,2,2,3, 
			 (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
			 (GtkAttachOptions)0, 
			 0, 2);

	create_param_entry_with_label(
            table, tooltips, 4,
            _("Bailout Distance:"),
            shadow,
            BAILOUT,
            _("Stop iterating points which get further from the origin than this"));

	/* antialias */
	GtkWidget *aa_button = gtk_check_button_new_with_label(_("Antialias"));
	gtk_table_attach(GTK_TABLE(table), aa_button, 
			 2,3,0,1,
			 (GtkAttachOptions)GTK_FILL,
			 (GtkAttachOptions)0,
			 0,2);

	gtk_tooltips_set_tip (tooltips, aa_button, 
			      _("If you turn this on the image looks smoother but takes longer to draw"), NULL);

        gtk_label_set_justify(
            GTK_LABEL(GTK_BIN(aa_button)->child),GTK_JUSTIFY_LEFT);

	gtk_widget_show(aa_button);

	gtk_signal_connect (GTK_OBJECT(aa_button),"toggled",
			    GTK_SIGNAL_FUNC(set_aa_callback),
			    (gpointer) shadow);

	gtk_signal_connect (GTK_OBJECT(shadow),"parameters_changed",
			    GTK_SIGNAL_FUNC(refresh_aa_callback),
			    (gpointer) aa_button);

        // continuous potential
	GtkWidget *potential = gtk_check_button_new_with_label(_("Continuous Potential"));
	gtk_table_attach(GTK_TABLE(table), potential,
                         2,3,1,2, 
			 (GtkAttachOptions)0, 
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

        gtk_label_set_justify(
            GTK_LABEL(GTK_BIN(potential)->child),GTK_JUSTIFY_LEFT);

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
	GtkWidget *auto_deepen_button;

	vbox = gtk_vbox_new (FALSE, 0);

	gtk_widget_show (vbox);
	gtk_container_add (GTK_CONTAINER (notebook), vbox);

	table = gtk_table_new (6, 3, FALSE);
	gtk_widget_show (table);
	gtk_box_pack_start (GTK_BOX (vbox), table, TRUE, TRUE, 0);

	label = gtk_label_new (_("Image"));
	gtk_widget_show (label);

	gtk_notebook_set_tab_label (GTK_NOTEBOOK (notebook), 
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 1), label);


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

	/* auto-deepen */
	auto_deepen_button = gtk_check_button_new_with_label(_("Auto Deepening"));
        gtk_label_set_justify(
            GTK_LABEL(GTK_BIN(auto_deepen_button)->child),GTK_JUSTIFY_LEFT);

	gtk_table_attach(GTK_TABLE(table), auto_deepen_button, 
			 2,3,1,2,
			 (GtkAttachOptions)GTK_FILL,
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
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 2), label);

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
				    gtk_notebook_get_nth_page (GTK_NOTEBOOK (notebook), 3), label);

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

void 
propertybox_refresh(model_t *m)
{
    GtkWidget *propertybox = global_propertybox;

    Gf4dFractal *f = model_get_fract(m);
    int i;
    e_colorizer ctype;
    char *filename;

    // property box is NULL if it's not currently displayed
    if (propertybox!=NULL) {
        GtkWidget *w;

        Gf4dFractal *shadow;
        shadow = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(propertybox),"shadow"));
        // invoke assignment operator to copy entire state of fractal
        gf4d_fractal_update_fract(shadow,f);

        // shadow updates all widgets 
        gf4d_fractal_parameters_changed(shadow);
        gnome_property_box_set_state(GNOME_PROPERTY_BOX(propertybox),
                                     FALSE);
    }	
}

void
propertybox_destroy (GtkObject *pb, gpointer user_data)
{
    // FIXME: leaks like a sieve
    global_propertybox=NULL;
}

/* all operations inside the property box have updated a "shadow"
 * Gf4dFractal object. Now we apply those changes to the main object 
 */

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

    if(model_cmd_start(m))
    {
        f = model_get_fract(m);
        Gf4dFractal *shadow = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(pb),"shadow"));
        gf4d_fractal_update_fract(f,shadow);

        model_cmd_finish(m);
    }
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
create_propertybox (model_t *m)
{
    if (global_propertybox!=NULL) {
        return;
    }

    GtkWidget *notebook;
    GtkWidget *propertybox;
    GtkTooltips *tooltips;
    Gf4dFractal *shadow = gf4d_fractal_copy(model_get_fract(m));
    tooltips = gtk_tooltips_new ();
    
    global_propertybox = propertybox = gnome_property_box_new ();
    
    notebook = GNOME_PROPERTY_BOX (propertybox)->notebook;
    gtk_widget_show (notebook);
    
    create_propertybox_color_page(propertybox, notebook, tooltips, shadow);	
    create_propertybox_general_page(propertybox,notebook,tooltips, shadow);
    create_propertybox_location_page(propertybox, notebook, tooltips, shadow);
    create_propertybox_angles_page(propertybox, notebook, tooltips, shadow);
    
    
    gtk_signal_connect (GTK_OBJECT (propertybox), "apply",
                        GTK_SIGNAL_FUNC (propertybox_apply),
                        m);
  
    gtk_signal_connect (GTK_OBJECT (propertybox), "help",
                        GTK_SIGNAL_FUNC (propertybox_help),
                        (char *)"preferences.html");
    
    gtk_signal_connect_object (GTK_OBJECT (propertybox), "destroy",
                               GTK_SIGNAL_FUNC (propertybox_destroy),
                               NULL);
    
    gtk_signal_connect_object (GTK_OBJECT(shadow),"parameters_changed",
                               GTK_SIGNAL_FUNC(gnome_property_box_changed),
                               GTK_OBJECT(propertybox));
    
    gtk_object_set_data (GTK_OBJECT (propertybox), "shadow", shadow);

    propertybox_refresh(m);
    gtk_widget_show(global_propertybox);
}
