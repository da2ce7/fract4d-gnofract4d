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
#include "callbacks.h"
#include "model.h"
#include "properties.h"
#include "preferences.h"
#include "cmapbrowser.h"
#include "interface.h"
//#include "movie_editor.h"
#include "gf4d_fractal.h"

typedef struct {
    model_t *m;
    GtkWidget *f;
} save_cb_data;


bool check_overwrite(const gchar *fname)
{
    if(!g_file_test(fname, G_FILE_TEST_EXISTS))
    {
	return true;
    }

    gchar *msg = g_strdup_printf(_("File %s already exists : Overwrite it?"), 
				 fname);
    /* file exists, check with user */
    GtkWidget *dialog = gtk_message_dialog_new (
	GTK_WINDOW(main_app_window),
	GTK_DIALOG_DESTROY_WITH_PARENT,
	GTK_MESSAGE_WARNING,
	GTK_BUTTONS_OK_CANCEL,
	msg);
    gint choice = gtk_dialog_run (GTK_DIALOG (dialog));
    gtk_widget_destroy (dialog);
    g_free(msg);    
    return choice == GTK_RESPONSE_OK;
}

// invoked when OK clicked on save image file selector
void 
save_image_ok_cb(GtkButton *button, gpointer user_data)
{
    save_cb_data *p = (save_cb_data *)user_data;

    GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
    const gchar *name = gtk_file_selection_get_filename (f);

    if(check_overwrite(name))
    {
	model_cmd_save_image(p->m,name);
    }
    g_free(user_data);
}

// invoked when OK clicked on save param file selector
void 
save_param_ok_cb(GtkButton *button, gpointer user_data)
{
    save_cb_data *p = (save_cb_data *)user_data;

    GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
    const gchar *name = gtk_file_selection_get_filename (f);
    if(check_overwrite(name))
    {
	g_print("saving\n");
	model_cmd_save(p->m,name);
    }
    g_free(user_data);
}

// invoked when OK clicked on load param file selector
void 
load_param_ok_cb(GtkButton *button, gpointer user_data)
{
    save_cb_data *p = (save_cb_data *)user_data;

    GtkFileSelection *f = GTK_FILE_SELECTION(p->f);
    const gchar *name = gtk_file_selection_get_filename (f);
    model_cmd_load(p->m,name);
    g_free(user_data);
}


/* Ensure that the dialog box is destroyed when the user clicks a button. */
void 
ensure_destruction(GtkFileSelection *f)
{
    g_signal_connect_swapped (
        G_OBJECT (f->ok_button),
        "clicked", 
        GTK_SIGNAL_FUNC (gtk_widget_destroy),
        G_OBJECT(f));
    
    g_signal_connect_swapped (
        G_OBJECT (f->cancel_button),
        "clicked", 
        GTK_SIGNAL_FUNC (gtk_widget_destroy),
        G_OBJECT(f));
}

/* a general load/save box */
GtkWidget*
create_generic_file_dialog(
    model_t *m, 
    gchar *title, 
    gchar *default_name,
    gchar *extension,
    GtkSignalFunc func)
{
    GtkWidget *f;
    save_cb_data *pdata = g_new0(save_cb_data,1);
    
    f = gtk_file_selection_new(title);
    
    gtk_file_selection_complete(GTK_FILE_SELECTION(f), extension);
    gtk_file_selection_set_filename(GTK_FILE_SELECTION(f), default_name);
    
    pdata->f = f;
    pdata->m = m;
    g_signal_connect (
        GTK_OBJECT (GTK_FILE_SELECTION(f)->ok_button),
        "clicked", func, pdata);
                             
    ensure_destruction(GTK_FILE_SELECTION(f));

    return f;
}

GtkWidget*
create_save_image (model_t *m)
{
    return create_generic_file_dialog(
	m,
        _("Save Image as"), 
        _("image.png"),
	".png",			      
        GTK_SIGNAL_FUNC(save_image_ok_cb));
}

GtkWidget*
create_save_param (model_t *m)
{    
    return create_generic_file_dialog(
	m,
        _("Save Parameters as"), 
        _("param.fct"),
	"*.fct",			      
        GTK_SIGNAL_FUNC(save_param_ok_cb));
}

GtkWidget*
create_load_param (model_t *m)
{
    return create_generic_file_dialog(
	m,
        _("Load Parameters"), 
        _("param.fct"),
	"*.fct",			      
        GTK_SIGNAL_FUNC(load_param_ok_cb));
}

gint
menu_quit_cb(GtkWidget       *widget,
             gpointer        user_data)
{
    model_t *m = (model_t *)user_data;
    gf4d_fractal_interrupt(model_get_fract(m));

    gnome_config_sync();
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
fractal_settings_cb(GtkMenuItem *menuitem,
               gpointer user_data)
{
    create_propertybox((model_t *)user_data);
}

void 
preferences_cb(GtkMenuItem *menuitem,
               gpointer user_data)
{
    create_prefs_box((model_t *)user_data);
}

static GnomeUIInfo file1_menu_uiinfo[] =
{
    {
        GNOME_APP_UI_ITEM, N_("_Open Parameter File"),
        NULL,
        (void *)load_param_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GTK_STOCK_OPEN,
        'o', GDK_CONTROL_MASK, NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("_Save Parameter File"),
        NULL,
        (void *)save_param_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GTK_STOCK_SAVE,
        's', GDK_CONTROL_MASK, NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("Save _Image"),
        NULL,
        (void *)save_image_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GTK_STOCK_SAVE,
        'i', GDK_CONTROL_MASK, NULL
    },
    {
        GNOME_APP_UI_TOGGLEITEM, N_("_Pause"),
        NULL,
        (void *)pause_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GNOME_STOCK_BLANK,
        'p', GDK_CONTROL_MASK, NULL
    },
    GNOMEUIINFO_SEPARATOR,
    GNOMEUIINFO_MENU_EXIT_ITEM ((void *)menu_quit_cb, NULL),
    GNOMEUIINFO_END
};

static GnomeUIInfo edit_menu_uiinfo[] =
{
    {
        GNOME_APP_UI_ITEM, N_("_Fractal Settings..."),
        NULL,
        (void *)fractal_settings_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GTK_STOCK_PROPERTIES,
         'f', GDK_CONTROL_MASK, NULL
    },
    {
        GNOME_APP_UI_ITEM, N_("Co_lors..."),
        NULL,
        (void *)create_cmap_browser, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, "",
         'l', GDK_CONTROL_MASK, NULL
    },
    GNOMEUIINFO_MENU_PREFERENCES_ITEM (preferences_cb, NULL),
    GNOMEUIINFO_MENU_UNDO_ITEM(undo_cb, NULL),
    GNOMEUIINFO_MENU_REDO_ITEM(redo_cb, NULL),
    {
        GNOME_APP_UI_ITEM, N_("Reset"),
        NULL,
        (void *)reset_cb, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, GTK_STOCK_HOME,
        GDK_Home, (GdkModifierType)0, NULL
    },
/*
    {
        GNOME_APP_UI_ITEM, N_("_Movie Editor..."),
        NULL,
        (void *)create_movie_editor, NULL, NULL,
        GNOME_APP_PIXMAP_STOCK, "",
        'm', GDK_CONTROL_MASK, NULL
    },
*/
    GNOMEUIINFO_END
};

static GnomeUIInfo help1_menu_uiinfo[] =
{
    GNOMEUIINFO_HELP ((void *)PACKAGE "-manual"),
    GNOMEUIINFO_END
};

GnomeUIInfo menubar1_uiinfo[] =
{
    GNOMEUIINFO_MENU_FILE_TREE (file1_menu_uiinfo),
    GNOMEUIINFO_MENU_EDIT_TREE (edit_menu_uiinfo),
    GNOMEUIINFO_MENU_HELP_TREE (help1_menu_uiinfo),
    GNOMEUIINFO_END
};

