/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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
#include "calc.h"
#include "callbacks.h"
#include "toolbars.h"

#include <gnome.h>
#include "gf4d_fractal.h"
#include "iterFunc.h"
#include <cstdlib>

GtkWidget *global_propertybox=NULL;

gboolean 
set_width_callback(GtkEntry *e, GdkEventFocus *, model_t *m)
{
    char *s = gtk_entry_get_text(e);
    int width=0;
    sscanf(s,"%d",&width);
    model_set_width(m,width);
    return TRUE;
}

void 
refresh_width_callback(Gf4dFractal *f, GtkEntry *e)
{
    char buf[80];
    sprintf(buf,"%d",gf4d_fractal_get_xres(f));
    gtk_entry_set_text(e,buf);
}

gboolean
set_height_callback(GtkEntry *e, GdkEventFocus *, model_t *m)
{
    char *s = gtk_entry_get_text(e);
    int height=0;
    sscanf(s,"%d",&height);
    model_set_height(m,height);
    return TRUE;
}

void 
refresh_height_callback(Gf4dFractal *f, GtkEntry *e)
{
    char buf[80];
    sprintf(buf,"%d",gf4d_fractal_get_yres(f));
    gtk_entry_set_text(e,buf);
}

gboolean
set_maxiter_callback(GtkEntry *e, GdkEventFocus *, Gf4dFractal *f)
{
    gchar *s = gtk_entry_get_text(e);
    int niters=0;
    sscanf(s,"%d",&niters);
    g_free(s);
    if(niters==gf4d_fractal_get_max_iterations(f)) return TRUE;

    gf4d_fractal_set_max_iterations(f,niters);
    gf4d_fractal_parameters_changed(f);	
    return TRUE;
}

void 
refresh_maxiter_callback(Gf4dFractal *f, GtkEntry *e)
{
    char buf[80];
    sprintf(buf,"%d",gf4d_fractal_get_max_iterations(f));
    gtk_entry_set_text(e,buf);
}

void
create_entry_with_label(
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

void
create_image_entry(
    GtkWidget *table,
    GtkTooltips *tooltips,
    int row,
    gchar *label_text,
    Gf4dFractal *f,
    model_t *m,
    int initial_val,
    GtkSignalFunc set_cb,
    GtkSignalFunc refresh_cb,
    gchar *tip)
{
    GtkWidget *label = gtk_label_new (label_text);
    GtkWidget *combo_entry=gtk_entry_new();
    
    char buf[80];
    sprintf(buf,"%d",initial_val);

    gtk_entry_set_text(GTK_ENTRY(combo_entry), buf);

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
                       m);
    
    gtk_signal_connect(GTK_OBJECT(f), "parameters_changed",
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
create_param_entry_with_label(
    GtkWidget *table,
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
        N_("And"),
        N_("Real part"),
        N_("Imaginary part"),
        N_("Difference")
    };

    for(unsigned int i=0; i < sizeof(bailout_names)/sizeof(bailout_names[0]); ++i)
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
set_aa_callback(GtkWidget *widget, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);

    e_antialias aa_type = (e_antialias)GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(widget),"type"));

    e_antialias old_type = gf4d_fractal_get_aa(f);
    if(aa_type != old_type)
    {
        gf4d_fractal_set_aa(f,aa_type);
        gf4d_fractal_parameters_changed(f);
    }
}

void
set_cf_callback(GtkWidget *widget, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);

    e_colorFunc cf_type = (e_colorFunc)GPOINTER_TO_INT(gtk_object_get_data(
        GTK_OBJECT(widget),"type"));

    int whichCf = GPOINTER_TO_INT(gtk_object_get_data(
        GTK_OBJECT(widget->parent), "whichCf"));

    e_colorFunc old_type = gf4d_fractal_get_colorFunc(f,whichCf);
    if(cf_type != old_type)
    {
        gf4d_fractal_set_colorFunc(f,cf_type,whichCf);
        gf4d_fractal_parameters_changed(f);
    }
}

void
refresh_aa_callback(Gf4dFractal *f, gpointer user_data)
{
    GtkOptionMenu *om = GTK_OPTION_MENU(user_data);
    GtkWidget *m = gtk_option_menu_get_menu(om);

    GList *list = gtk_container_children(GTK_CONTAINER(m));
    int index=0;
    e_antialias aa_val = gf4d_fractal_get_aa(f);

    // find an element with the same antialias value as the one the fractal has
    while(list)
    {
        GtkMenuItem *mi = GTK_MENU_ITEM(list->data);
        e_antialias aa = (e_antialias)GPOINTER_TO_INT(
            gtk_object_get_data(GTK_OBJECT(mi),"type"));
        
        if(aa == aa_val)
        {
            gtk_option_menu_set_history(om,index);
            return;
        }
        list = g_list_next(list);
        index++;
    }
    g_warning(_("Unknown antialias type ignored"));
}

void
refresh_cf_callback(Gf4dFractal *f, gpointer user_data)
{
    GtkOptionMenu *om = GTK_OPTION_MENU(user_data);
    GtkWidget *m = gtk_option_menu_get_menu(om);

    int whichCf = GPOINTER_TO_INT(gtk_object_get_data(
        GTK_OBJECT(m), "whichCf"));

    GList *list = gtk_container_children(GTK_CONTAINER(m));
    int index=0;
    e_colorFunc cf_val = gf4d_fractal_get_colorFunc(f,whichCf);

    // find an element with the same antialias value as the one the fractal has
    while(list)
    {
        GtkMenuItem *mi = GTK_MENU_ITEM(list->data);
        e_colorFunc cf = (e_colorFunc)GPOINTER_TO_INT(
            gtk_object_get_data(GTK_OBJECT(mi),"type"));
        
        if(cf == cf_val)
        {
            gtk_option_menu_set_history(om,index);
            return;
        }
        list = g_list_next(list);
        index++;
    }
    g_warning(_("Unknown antialias type ignored"));
}

GtkWidget *create_aa_menu(Gf4dFractal *shadow)
{
    GtkWidget *aa_type = gtk_option_menu_new();
    GtkWidget *aa_menu = gtk_menu_new();

    static const gchar *aa_names[] = 
    {
        N_("None (Fastest)"),
        N_("Default"),
        N_("Best (Slowest)")
    };

    for(unsigned int i=0; i < sizeof(aa_names)/sizeof(aa_names[0]); ++i)
    {
        GtkWidget *menu_item = gtk_menu_item_new_with_label(aa_names[i]);
    
        gtk_object_set_data(
            GTK_OBJECT (menu_item), 
            "type",
            GINT_TO_POINTER(i));
    
        gtk_signal_connect(
            GTK_OBJECT(menu_item),
            "activate",
            GTK_SIGNAL_FUNC(set_aa_callback),
            shadow);
    
        gtk_menu_append(GTK_MENU(aa_menu), menu_item);
        gtk_widget_show(menu_item);
        gtk_option_menu_set_menu(GTK_OPTION_MENU(aa_type), aa_menu);
    }    

    // refresh when shadow changes
    gtk_signal_connect(
        GTK_OBJECT(shadow),
        "parameters_changed",
        GTK_SIGNAL_FUNC(refresh_aa_callback),
        aa_type);

    return aa_type;
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


void show_page_child_callback(GtkWidget *button, GtkWidget *child)
{
    GtkWidget *arrow = GTK_BIN(button)->child;

    if(GTK_WIDGET_VISIBLE(child))
    {
        gtk_widget_hide_all(child);
        gtk_arrow_set(GTK_ARROW(arrow), GTK_ARROW_RIGHT, GTK_SHADOW_OUT); 
    }
    else
    {
        gtk_widget_show_all(child);
        gtk_arrow_set(GTK_ARROW(arrow), GTK_ARROW_DOWN, GTK_SHADOW_OUT); 
    }
}

/* a compound widget which hides and shows its child in a box below the title */
GtkWidget *create_page(GtkWidget *child, gchar *title)
{
    GtkWidget *title_frame = gtk_frame_new(NULL);
    GtkWidget *vbox = gtk_vbox_new(FALSE, 0);
    GtkWidget *title_hbox = gtk_hbox_new(FALSE, 0);
    GtkWidget *label = gtk_label_new(title);
    GtkWidget *arrow = gtk_arrow_new(GTK_ARROW_RIGHT,GTK_SHADOW_OUT);
    GtkWidget *arrowbut = gtk_button_new();
    GtkWidget *hsep = gtk_hseparator_new();

    gtk_container_add(GTK_CONTAINER(arrowbut),arrow);
    gtk_button_set_relief(GTK_BUTTON(arrowbut), GTK_RELIEF_NONE);

    gtk_box_pack_start(GTK_BOX(title_hbox), label, 1, 1, 1);
    gtk_box_pack_end(GTK_BOX(title_hbox), arrowbut, 0, 0, 1);

    gtk_box_pack_start(GTK_BOX(vbox), title_hbox, 0, 1, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hsep, 0, 1, 1);
    gtk_box_pack_start(GTK_BOX(vbox), child, 1, 1, 1);

    gtk_container_add(GTK_CONTAINER(title_frame), vbox);

    gtk_widget_show_all(title_frame);
    gtk_widget_hide_all(child);

    gtk_signal_connect(
        GTK_OBJECT(arrowbut), 
        "clicked", 
        GTK_SIGNAL_FUNC(show_page_child_callback), 
        (gpointer) child);

    return title_frame;
}

void
create_propertybox_bailout_page(
    GtkWidget *vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow)
{
    GtkWidget *table = gtk_table_new (2, 2, FALSE);
    GtkWidget *test_page = create_page(table, _("Bailout"));
    gtk_box_pack_start( GTK_BOX (vbox), test_page, 1, 1, 0 );

    // bailout type
    GtkWidget *bailout_label= gtk_label_new(_("Function"));
    gtk_widget_show(bailout_label);
    gtk_table_attach(GTK_TABLE(table), bailout_label, 0,1,0,1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);
        
    GtkWidget *bailout_type = create_bailout_menu(shadow);

    gtk_widget_show(bailout_type);

    gtk_table_attach(GTK_TABLE(table), bailout_type ,1,2,0,1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    // Bailout distance
    create_param_entry_with_label(
        table, tooltips, 1,
        _("Distance"),
        shadow,
        BAILOUT,
        _("Stop iterating points which get further from the origin than this"));
}

GtkWidget *
create_cf_menu(Gf4dFractal *shadow, int whichCf)
{
    GtkWidget *cf_type = gtk_option_menu_new();
    GtkWidget *cf_menu = gtk_menu_new();

    static const gchar *cf_names[] = 
    {
        N_("Iteration Count"),
        N_("Continuous Potential"),
        N_("Color Zero"),
        N_("Magnitude")
    };

    gtk_object_set_data(
        GTK_OBJECT (cf_menu),
        "whichCf",
        GINT_TO_POINTER(whichCf));

    for(unsigned int i=0; i < sizeof(cf_names)/sizeof(cf_names[0]); ++i)
    {
        GtkWidget *menu_item = gtk_menu_item_new_with_label(cf_names[i]);
    
        gtk_object_set_data(
            GTK_OBJECT (menu_item), 
            "type",
            GINT_TO_POINTER(i));
    
        gtk_signal_connect(
            GTK_OBJECT(menu_item),
            "activate",
            GTK_SIGNAL_FUNC(set_cf_callback),
            shadow);

        gtk_menu_append(GTK_MENU(cf_menu), menu_item);
        gtk_widget_show(menu_item);
    }    

    gtk_option_menu_set_menu(GTK_OPTION_MENU(cf_type), cf_menu);

    // refresh when shadow changes

    gtk_signal_connect(
        GTK_OBJECT(shadow),
        "parameters_changed",
        GTK_SIGNAL_FUNC(refresh_cf_callback),
        cf_type);

    return cf_type;
}

void
create_propertybox_rendering_page(
    GtkWidget *vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow)
{
    GtkWidget *table = gtk_table_new (4, 2, FALSE);
    GtkWidget *auto_deepen_button;
    
    GtkWidget *general_page = create_page(table,_("Rendering"));
    
    gtk_box_pack_start( GTK_BOX (vbox), general_page, 1, 1, 0 );

    /* antialias */
    GtkWidget *aa_label= gtk_label_new(_("Antialiasing"));

    gtk_table_attach(GTK_TABLE(table), aa_label, 0,1,0,1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);
        
    GtkWidget *aa_type = create_aa_menu(shadow);

    gtk_table_attach(GTK_TABLE(table), aa_type ,1,2,0,1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    // iteration count
    create_entry_with_label(
        table, tooltips, 1,
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
                     0,1,2,3,
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

    /* outer colorFunc type */
    GtkWidget *outerCfMenu = create_cf_menu(shadow,OUTER);
    gtk_table_attach(GTK_TABLE(table), outerCfMenu, 1,2,3,4, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    /* outer label */
    GtkWidget *outerCfLabel = gtk_label_new(_("Outer"));
    gtk_table_attach(GTK_TABLE(table), outerCfLabel, 0,1,3,4, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);
    gtk_widget_show(outerCfLabel);

    /* inner colorFunc type */
    GtkWidget *innerCfMenu = create_cf_menu(shadow,INNER);
    gtk_table_attach(GTK_TABLE(table), innerCfMenu, 1,2,4,5, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    /* inner label */
    GtkWidget *innerCfLabel = gtk_label_new(_("Inner"));
    gtk_table_attach(GTK_TABLE(table), innerCfLabel, 0,1,4,5, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);
    gtk_widget_show(innerCfLabel);

}

void
set_func_callback(GtkWidget *widget, gpointer user_data)
{
    Gf4dFractal *f = GF4D_FRACTAL(user_data);

    const char *func_type = (const char *)gtk_object_get_data(GTK_OBJECT(widget),"type");

    iterFunc *old_func = gf4d_fractal_get_func(f);
    if(strcmp(func_type, old_func->type()))
    {
        gf4d_fractal_set_func(f,func_type);
        gf4d_fractal_parameters_changed(f);
    }
}

void
refresh_func_callback(Gf4dFractal *f, gpointer user_data)
{
    GtkOptionMenu *om = GTK_OPTION_MENU(user_data);
    GtkWidget *m = gtk_option_menu_get_menu(om);

    GList *list = gtk_container_children(GTK_CONTAINER(m));
    int index=0;
    iterFunc *func = gf4d_fractal_get_func(f);
    const char *func_val = func->type();

    // find an element with the same antialias value as the one the fractal has
    while(list)
    {
        GtkMenuItem *mi = GTK_MENU_ITEM(list->data);
        const char *func = (const char *)(gtk_object_get_data(GTK_OBJECT(mi),"type"));
        
        if(0 == strcmp(func,func_val))
        {
            gtk_option_menu_set_history(om,index);
            return;
        }
        list = g_list_next(list);
        index++;
    }
    g_warning(_("Unknown function type ignored"));
}

GtkWidget *create_function_menu(Gf4dFractal *shadow)
{
    GtkWidget *func_type = gtk_option_menu_new();
    GtkWidget *func_menu = gtk_menu_new();

    const ctorInfo *names = iterFunc_names();
    int i = 0;
    while(names[i].name)
    {
        const char *name = names[i].name;
        GtkWidget *menu_item = gtk_menu_item_new_with_label(name);
    
        gtk_object_set_data(
            GTK_OBJECT (menu_item), 
            "type",
            const_cast<char *>(name));
    
        gtk_signal_connect(
            GTK_OBJECT(menu_item),
            "activate",
            GTK_SIGNAL_FUNC(set_func_callback),
            shadow);
    
        gtk_menu_append(GTK_MENU(func_menu), menu_item);
        gtk_widget_show(menu_item);
        gtk_option_menu_set_menu(GTK_OPTION_MENU(func_type), func_menu);
        ++i;
    };

    // refresh when shadow changes
    gtk_signal_connect(
        GTK_OBJECT(shadow),
        "parameters_changed",
        GTK_SIGNAL_FUNC(refresh_func_callback),
        func_type);

    return func_type;
}

void
create_propertybox_function_page(
    GtkWidget *vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow)
{
    GtkWidget *table = gtk_table_new (3, 2, FALSE);
    
    GtkWidget *general_page = create_page(table,_("Function"));
    
    gtk_box_pack_start( GTK_BOX (vbox), general_page, 1, 1, 0 );

    /* iteration function */
    GtkWidget *func_label= gtk_label_new(_("Function"));

    gtk_table_attach(
        GTK_TABLE(table), func_label, 0,1,0,1, 
        (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
        (GtkAttachOptions)0, 
        0, 2);
        
    GtkWidget *func_type = create_function_menu(shadow);

    gtk_table_attach(
        GTK_TABLE(table), func_type ,1,2,0,1, 
        (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
        (GtkAttachOptions)0, 
        0, 2);
}

void
set_func_parameter_cb(GtkWidget * entry, GdkEventFocus *, model_t *m)
{
    Gf4dFractal *f = model_get_fract(m);
    iterFunc *func = gf4d_fractal_get_func(f);
    int index = GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(entry),"index"));
    const char *text = gtk_entry_get_text(GTK_ENTRY(entry));

    double newPart = strtod(text,NULL);
    std::complex<double> oldVal = func->getOption(index/2);
    std::complex<double> newVal;

    if(index % 2)
    {
        // odd index = imaginary part
        newVal = std::complex<double>(oldVal.real(),newPart);
    }
    else
    {
        // real part
        newVal = std::complex<double>(newPart,oldVal.imag());
    }
    
    if(newVal != oldVal && model_cmd_start(m,"set_func_param"))
    {
        func->setOption(index/2,newVal);
        model_cmd_finish(m,"set_func_param");
    }        
}

void make_func_label(const char *name, const char *part_name, GtkWidget *table, int i)
{
    char *decorated_name = g_strdup_printf("%s.%s :",name, part_name);
    GtkWidget *label = gtk_label_new(decorated_name);
    g_free(decorated_name);
    
    gtk_table_attach(
        GTK_TABLE(table), label, 0,1,i,i+1, 
        (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
        (GtkAttachOptions)0, 
        0, 2);
}

void refresh_funcparam_cb(Gf4dFractal *f, GtkWidget *entry)
{
    int index = GPOINTER_TO_INT(gtk_object_get_data(GTK_OBJECT(entry),"index"));
    iterFunc *func = gf4d_fractal_get_func(f);
    
    std::complex<double> newVal = func->getOption(index/2);
    double d;
    if(index % 2)
    {
        d = newVal.imag();
    }
    else
    {
        d = newVal.real();
    }
    
    char strOpt[30];
    sprintf(strOpt,"%g",d);
    
    gtk_entry_set_text(GTK_ENTRY(entry),strOpt);
}

void make_func_entry(Gf4dFractal *shadow, double d, GtkWidget *table, int i)
{
    /* widget to enter new parameter value */
    GtkWidget *entry = gtk_entry_new();

    /* data for callbacks */
    gtk_object_set_data(GTK_OBJECT(entry), "index", GINT_TO_POINTER(i));
    
    gtk_table_attach(
        GTK_TABLE(table), entry, 1,2,i,i+1, 
        (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
        (GtkAttachOptions)0, 
        0, 2);
    
    model_t *m = (model_t *)gtk_object_get_data(GTK_OBJECT(table),"model");
    assert(m);

    gtk_signal_connect(
        GTK_OBJECT(entry),"focus-out-event",
        GTK_SIGNAL_FUNC(set_func_parameter_cb),
        m);

    gtk_signal_connect_while_alive(
        GTK_OBJECT(shadow), "parameters_changed",
        GTK_SIGNAL_FUNC(refresh_funcparam_cb),
        entry, GTK_OBJECT(entry));

    refresh_funcparam_cb(shadow,entry);
}

void
fourway_set_param_cb(
    Gf4dFourway *fourway, 
    gint deltax, 
    gint deltay, 
    model_t *m)
{
    if(model_cmd_start(m, "func_param"))
    {
        Gf4dFractal *f = model_get_fract(m);
        iterFunc *func = gf4d_fractal_get_func(f);
        int index = GPOINTER_TO_INT(
            gtk_object_get_data(GTK_OBJECT(fourway),"index"));
        
        std::complex<double> oldVal = func->getOption(index);
        std::complex<double> delta(deltax / 100.0 , deltay / 100.0);
        std::complex<double> newVal = oldVal + delta;

        func->setOption(index,newVal);
        model_cmd_finish(m, "func_param");
    }

}

void
fourway_preview_param_cb(
    Gf4dFourway *fourway, 
    gint deltax, 
    gint deltay, 
    model_t *m)
{
    Gf4dFractal *f = get_toolbar_preview_fract();
    iterFunc *func = gf4d_fractal_get_func(f);
    int index = GPOINTER_TO_INT(
        gtk_object_get_data(GTK_OBJECT(fourway),"index"));
    
    std::complex<double> oldVal = func->getOption(index);
    std::complex<double> delta(deltax / 100.0 , deltay / 100.0);
    std::complex<double> newVal = oldVal + delta;

    func->setOption(index,newVal);
    gf4d_fractal_calc(f,1);
}

void
make_func_edit_widgets(
    Gf4dFractal *shadow, 
    iterFunc *func, 
    GtkWidget *table, 
    int i)
{
    /* labels for parameter names */
    const char *name = func->optionName(i);
    make_func_label(name,_("real"),table,2*i);
    make_func_label(name,_("imag"),table,2*i+1);
    
    /* entry widgets for changing params */
    std::complex<double> opt = func->getOption(i);
    
    make_func_entry(shadow, opt.real(),table,2*i);
    make_func_entry(shadow, opt.imag(),table,2*i+1);
    
    /* fourway widget for interactive twiddling */
    GtkWidget *fourway = gf4d_fourway_new(name);

    gtk_object_set_data(GTK_OBJECT(fourway), "index", GINT_TO_POINTER(i));
    
    gtk_table_attach(
        GTK_TABLE(table), fourway, 2, 3, 2*i, 2*i+2,
        (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
        (GtkAttachOptions)0, 
        0, 2);

    model_t *m = (model_t *)gtk_object_get_data(GTK_OBJECT(table),"model");
    assert(m);

    gtk_signal_connect(GTK_OBJECT(fourway), "value_changed",
                       (GtkSignalFunc)fourway_set_param_cb,
                       (gpointer)m);

    gtk_signal_connect(GTK_OBJECT(fourway), "value_slightly_changed",
                       (GtkSignalFunc)fourway_preview_param_cb,
                       (gpointer)m);
}

void
refresh_func_parameters_callback(Gf4dFractal *f, GtkWidget *table)
{
    /* has the function type changed? */
    const char *current_type = (const char *)
        gtk_object_get_data(GTK_OBJECT(table),"type");

    iterFunc *func = gf4d_fractal_get_func(f);
    const char *new_type = func->type();

    if(0 == strcmp(current_type, new_type))
    {
        // type hasn't changed - do nothing
        return;
    }

    /* update current type */
    gtk_object_set_data(GTK_OBJECT(table),"type",const_cast<char *>(new_type));

    /* delete current widgets under table */
    GList *children = gtk_container_children(GTK_CONTAINER(table));
    while(children)
    {
        gtk_container_remove(GTK_CONTAINER(table), GTK_WIDGET(children->data));
        children = children->next;
    }

    /* add new widgets */
    int nOptions = func->nOptions();
    if(nOptions == 0)
    {
        GtkWidget *label = 
            gtk_label_new(_("This fractal type has no parameters"));

        gtk_table_attach(
            GTK_TABLE(table), label, 0,2,0,1, 
            (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
            (GtkAttachOptions)0, 
            0, 2);
    }        
    else
    {
        /* fractal has parameters */
        for(int i = 0; i < nOptions; ++i)
        {
            make_func_edit_widgets(f,func, table, i);
        }
    }
    /* table will be visible if this tab has been expanded */
    if(GTK_WIDGET_VISIBLE(table))
    {
        gtk_widget_show_all(table);
    }
}

void
create_propertybox_func_parameters_page(
    GtkWidget *vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow,
    model_t *m)
{
    GtkWidget *table = gtk_table_new (1, 3, FALSE);
    
    GtkWidget *general_page = create_page(table,_("Parameters"));
    
    gtk_box_pack_start( GTK_BOX (vbox), general_page, 1, 1, 0 );

    gtk_object_set_data(GTK_OBJECT(table), "type", (gpointer)"");
    gtk_object_set_data(GTK_OBJECT(table), "model", (gpointer)m);

    gtk_signal_connect(
        GTK_OBJECT(shadow),
        "parameters_changed",
        GTK_SIGNAL_FUNC(refresh_func_parameters_callback),
        table);
}

void
create_propertybox_image_page(
    GtkWidget *main_vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow,
    model_t *m)
{
    GtkWidget *table = gtk_table_new (2, 2, FALSE);    
    GtkWidget *image_page = create_page(table,_("Image"));
    
    gtk_box_pack_start( GTK_BOX (main_vbox), image_page, 1, 1, 0 );
    
    int height, width;
    model_get_dimensions(m,&width,&height);

    create_image_entry(
        table, 
        tooltips, 
        0,
        _("Width :"),
        model_get_fract(m),
        m, width,
        (GtkSignalFunc)set_width_callback,
        (GtkSignalFunc)refresh_width_callback,
        _("Image width (in pixels)"));
    
    create_image_entry(
        table, tooltips, 1,
        _("Height :"),
        model_get_fract(m),
        m, height,
        (GtkSignalFunc)set_height_callback,
        (GtkSignalFunc)refresh_height_callback,
        _("Image height (in pixels)"));
}

void
create_propertybox_location_page(
    GtkWidget *main_vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow)
{
    GtkWidget *table = gtk_table_new (5, 2, FALSE);
    
    GtkWidget *location_page = create_page(table,_("Location"));

    gtk_box_pack_start( GTK_BOX (main_vbox), location_page, 1, 1, 0 );
            
    create_param_entry_with_label(
        table, tooltips, 0, _("X (Re) :"), shadow, XCENTER, _("This is c.re in z^2 + c"));
    
    create_param_entry_with_label(
        table, tooltips, 1, _("Y (Im) :"), shadow, YCENTER, _("This is c.im in z^2 + c"));
    
    create_param_entry_with_label(
        table, tooltips, 2, _("Z (Re) :"), shadow, ZCENTER, _("This is z0.re in z^2 + c"));

    create_param_entry_with_label(
        table, tooltips, 3, _("W (Im) :"), shadow, WCENTER, _("This is z0.im in z^2 + c"));

    create_param_entry_with_label(
        table, tooltips, 4, _("Size :"), shadow, MAGNITUDE, _("Magnitude of image"));
}

void
create_propertybox_angles_page(
    GtkWidget *main_vbox,
    GtkTooltips *tooltips,
    Gf4dFractal *shadow)
{
    GtkWidget *table = gtk_table_new (6, 2, FALSE);;
    GtkWidget *angles_page = create_page(table,_("Angles"));
    
    gtk_box_pack_start( GTK_BOX (main_vbox), angles_page, 1, 1, 0 );
    
    create_param_entry_with_label(table, tooltips, 0, _("XY :"), shadow, XYANGLE, NULL);
    create_param_entry_with_label(table, tooltips, 1, _("XZ :"), shadow, XZANGLE, NULL);
    create_param_entry_with_label(table, tooltips, 2, _("XW :"), shadow, XWANGLE, NULL);
    create_param_entry_with_label(table, tooltips, 3, _("YZ :"), shadow, YZANGLE, NULL);
    create_param_entry_with_label(table, tooltips, 4, _("YW :"), shadow, YWANGLE, NULL);
    create_param_entry_with_label(table, tooltips, 5, _("ZW :"), shadow, ZWANGLE, NULL);
}

void 
propertybox_refresh(model_t *m)
{
    GtkWidget *propertybox = global_propertybox;
    Gf4dFractal *f = model_get_fract(m);

    // property box is NULL if it's not currently displayed
    if (propertybox!=NULL) {

        Gf4dFractal *shadow;
        shadow = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(propertybox),"shadow"));
        // invoke assignment operator to copy entire state of fractal
        gf4d_fractal_update_fract(shadow,f);

        // shadow updates all widgets - but make sure it doesn't re-update the main one!
        model_set_cmd_in_progress(m,true);
        gf4d_fractal_parameters_changed(shadow);
        model_set_cmd_in_progress(m,false);
    }	
}

/* all operations inside the property box have updated a "shadow"
 * Gf4dFractal object. Now we apply those changes to the main object 
 */

void
update_main_fractal(Gf4dFractal *shadow, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    Gf4dFractal *f = model_get_fract(m);

    if(!gf4d_fractal_is_equal(f,shadow) && model_cmd_start(m,"update"))
    {
        gf4d_fractal_update_fract(f,shadow);
        model_cmd_finish(m,"update");
    }
}

void
create_propertybox (model_t *m)
{
    // if it already exists, just show it
    if (global_propertybox!=NULL) {
        gtk_widget_show(global_propertybox);
        return;
    }

    GtkWidget *propertybox;
    GtkTooltips *tooltips;
    GtkWidget *vbox;
    Gf4dFractal *shadow = gf4d_fractal_copy(model_get_fract(m));
    tooltips = gtk_tooltips_new ();
    
    global_propertybox = propertybox = gnome_dialog_new(
        _("Fractal Properties"), GNOME_STOCK_BUTTON_CLOSE, NULL);

    vbox = GNOME_DIALOG(propertybox)->vbox;

    gtk_box_set_spacing(GTK_BOX(vbox),0);
    create_propertybox_function_page(vbox, tooltips, shadow);
    create_propertybox_func_parameters_page(vbox, tooltips, shadow, m);
    create_propertybox_rendering_page(vbox, tooltips, shadow);
    create_propertybox_bailout_page(vbox, tooltips, shadow);
    create_propertybox_image_page(vbox,tooltips, shadow, m);
    create_propertybox_location_page(vbox, tooltips, shadow);
    create_propertybox_angles_page(vbox, tooltips, shadow);
    
    gnome_dialog_set_close(GNOME_DIALOG(propertybox), TRUE);
    gnome_dialog_close_hides(GNOME_DIALOG(propertybox), TRUE);
    
    /* whenever the shadow fractal changes, update the main one */
    gtk_signal_connect (
        GTK_OBJECT(shadow), "parameters_changed",
        GTK_SIGNAL_FUNC(update_main_fractal), (gpointer) m);
    
    gtk_object_set_data (GTK_OBJECT (propertybox), "shadow", shadow);

    propertybox_refresh(m);

    gtk_widget_show(global_propertybox);
}
