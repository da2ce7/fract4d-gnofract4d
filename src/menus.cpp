/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
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

#include "menus.h"
#include "model.h"
#include "properties.h"
#include "cmapbrowser.h"
#include "movie_editor.h"

typedef struct {
    model_t *m;
    GtkWidget *f;
} save_cb_data;

// invoked when OK clicked on save image file selector
void 
save_image_ok_cb(GtkButton *button, gpointer user_data)
{
    save_cb_data *p = (save_cb_data *)user_data;
    char *name;

    GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
    name = gtk_file_selection_get_filename (f);

    model_cmd_save_image(p->m,name);
    g_free(user_data);
}

// invoked when OK clicked on save param file selector
void 
save_param_ok_cb(GtkButton *button, gpointer user_data)
{
    save_cb_data *p = (save_cb_data *)user_data;
    char *name;
    GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
    name = gtk_file_selection_get_filename (f);
    model_cmd_save(p->m,name);
    g_free(user_data);
}

// invoked when OK clicked on load param file selector
void 
load_param_ok_cb(GtkButton *button, gpointer user_data)
{
    save_cb_data *p = (save_cb_data *)user_data;
    char *name;
    GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
    name = gtk_file_selection_get_filename (f);
    model_cmd_load(p->m,name);
    g_free(user_data);
}

/* Ensure that the dialog box is destroyed when the user clicks a button. */
void 
ensure_destruction(GtkFileSelection *f)
{
    gtk_signal_connect_object (
        GTK_OBJECT (f->ok_button),
        "clicked", 
        GTK_SIGNAL_FUNC (gtk_widget_destroy),
        GTK_OBJECT(f));
    
    gtk_signal_connect_object (
        GTK_OBJECT (f->cancel_button),
        "clicked", 
        GTK_SIGNAL_FUNC (gtk_widget_destroy),
        GTK_OBJECT(f));
}

/* a general load/save box */
GtkWidget*
create_generic_file_dialog(
    model_t *m, 
    gchar *title, 
    gchar *default_name,
    GtkSignalFunc func)
{
    GtkWidget *f;
    save_cb_data *pdata = g_new0(save_cb_data,1);
    
    f = gtk_file_selection_new(title);
    
    gtk_file_selection_set_filename(GTK_FILE_SELECTION(f), default_name);
    
    pdata->f = f;
    pdata->m = m;
    gtk_signal_connect (
        GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
        "clicked", func, pdata);
                             
    ensure_destruction(GTK_FILE_SELECTION(f));

    return f;
}

GtkWidget*
create_save_image (model_t *m)
{
    return create_generic_file_dialog(m,
        _("Save Image as"), 
        _("image.png"), 
        GTK_SIGNAL_FUNC(save_image_ok_cb));
}

GtkWidget*
create_save_param (model_t *m)
{    
    return create_generic_file_dialog(m,
        _("Save Parameters as"), 
        _("param.fct"), 
        GTK_SIGNAL_FUNC(save_param_ok_cb));
}

GtkWidget*
create_load_param (model_t *m)
{
    return create_generic_file_dialog(m,
        _("Load Parameters"), 
        _("param.fct"), 
        GTK_SIGNAL_FUNC(load_param_ok_cb));
}

gint
menu_quit_cb(GtkWidget       *widget,
             gpointer        user_data)
{
    model_t *m = (model_t *)user_data;
    gf4d_fractal_interrupt(model_get_fract(m));

    model_write_autosave_file(m);
    gtk_main_quit();
    return FALSE;
}

void
reset_cb(GtkMenuItem     *menuitem,
             gpointer         user_data)
{
    model_t *m = (model_t *)user_data;
    if(model_cmd_start(m,"reset"))
    {
        gf4d_fractal_reset(model_get_fract(m));
        model_cmd_finish(m, "reset");
    }
}

void
reset_zoom_cb(GtkMenuItem *menuitem, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    if(model_cmd_start(m,"reset_zoom"))
    {
        Gf4dFractal *f = model_get_fract(m);
        gf4d_fractal_set_param(f, MAGNITUDE, "4.0");
        model_cmd_finish(m,"reset_zoom");
    }
    
}
void
save_image_cb(GtkMenuItem *menuitem,
              gpointer user_data)
{
    gtk_widget_show (create_save_image ((model_t *)user_data));
}

void
save_param_cb(GtkMenuItem *menuitem,
              gpointer user_data)
{
    gtk_widget_show (create_save_param ((model_t *)user_data));
}

void
load_param_cb(GtkMenuItem *menuitem,
              gpointer user_data)
{
    gtk_widget_show (create_load_param ((model_t *)user_data));
}

void
pause_cb(GtkMenuItem *menuitem,
         gpointer user_data)
{
    Gf4dFractal *f = model_get_fract((model_t *)user_data);
    bool isPaused = GTK_CHECK_MENU_ITEM(menuitem)->active;
    gf4d_fractal_pause(f,isPaused);
}

void
preferences_cb(GtkMenuItem *menuitem,
               gpointer user_data)
{
    create_propertybox((model_t *)user_data);
}

static GnomeUIInfo file1_menu_uiinfo[] =
{
    {
        GNOME_APP_UI_ITEM, N_("_Save image"),
        NULL,
        (void *)save_image_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_SAVE,
        0, (enum GdkModifierType)'s', NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("_Reset parameters"),
        NULL,
        (void *)reset_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_HOME,
        0, (enum GdkModifierType)'m', NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("_Reset Zoom"),
        NULL,
        (void *)reset_zoom_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_BLANK,
        0, (enum GdkModifierType) 'z', NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("Save _parameters"),
        NULL,
        (void *)save_param_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_SAVE_AS,
        0, (enum GdkModifierType)'p', NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("_Load parameters"),
        NULL,
        (void *)load_param_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_OPEN,
        0, (enum GdkModifierType)'l', NULL
    },
    {
        GNOME_APP_UI_TOGGLEITEM, N_("P_ause"),
        NULL,
        (void *)pause_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_BLANK,
        0, (enum GdkModifierType)'a', NULL
    },
    GNOMEUIINFO_SEPARATOR,
    GNOMEUIINFO_MENU_EXIT_ITEM ((void *)menu_quit_cb, NULL),
    GNOMEUIINFO_END
};

static GnomeUIInfo parameters1_menu_uiinfo[] =
{
    GNOMEUIINFO_MENU_PREFERENCES_ITEM (preferences_cb, NULL),
    {
        GNOME_APP_UI_ITEM, N_("_Colors..."),
        NULL,
        (void *)create_cmap_browser, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_BLANK,
        0, (enum GdkModifierType) 'c', NULL
    },
    /*
    {
        GNOME_APP_UI_ITEM, N_("_Movie Editor..."),
        NULL,
        (void *)create_movie_editor, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_MENU_BLANK,
        0, (enum GdkModifierType)'m', NULL
    },
    */
    GNOMEUIINFO_END
};

static GnomeUIInfo help1_menu_uiinfo[] =
{
    GNOMEUIINFO_HELP ((void *)PACKAGE),
    GNOMEUIINFO_END
};

GnomeUIInfo menubar1_uiinfo[] =
{
    GNOMEUIINFO_MENU_FILE_TREE (file1_menu_uiinfo),
    GNOMEUIINFO_MENU_SETTINGS_TREE (parameters1_menu_uiinfo),
    GNOMEUIINFO_MENU_HELP_TREE (help1_menu_uiinfo),
    GNOMEUIINFO_END
};

