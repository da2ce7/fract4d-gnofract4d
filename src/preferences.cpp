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

#include "preferences.h"
#include "properties.h" // for create_page

GtkWidget *global_prefs_box = NULL;

gboolean
set_cpath_cb(GtkEntry *e, GdkEventFocus *, gpointer user_data)
{
    model_t *m = (model_t *)(m);
    char *text = gtk_entry_get_text(e);
    model_set_compiler_location(m,text);
    return TRUE;
}

gboolean
set_cflags_cb(GtkEntry *e, GdkEventFocus *, gpointer user_data)
{
    model_t *m = (model_t *)(m);
    char *text = gtk_entry_get_text(e);
    model_set_compiler_flags(m,text,true);
    return TRUE;
}

void
create_prefs_compiler_page(
    model_t *m,
    GtkWidget *vbox,
    GtkTooltips *tooltips)
{
    GtkWidget *table = gtk_table_new (2, 2, FALSE);
    GtkWidget *page = create_page(vbox, table, _("Compiler"));
    gtk_box_pack_start( GTK_BOX (vbox), page, 1, 1, 0 );

    // Compiler location
    GtkWidget *cpath_label= gtk_label_new(_("Path to Compiler"));
    gtk_widget_show(cpath_label);
    gtk_table_attach(GTK_TABLE(table), cpath_label, 0,1,0,1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    GtkWidget *cpath_entry= gnome_file_entry_new("cpath",_("Location of C++ Compiler"));    
    gtk_widget_show(cpath_entry);
    gtk_table_attach(GTK_TABLE(table), cpath_entry, 1,2,0,1, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    GtkWidget *entry = gnome_file_entry_gtk_entry( GNOME_FILE_ENTRY(cpath_entry));
    gtk_entry_set_text(GTK_ENTRY(entry),model_get_compiler_location(m));

    gtk_signal_connect(GTK_OBJECT(entry),"focus-out-event",
                       (GtkSignalFunc)set_cpath_cb,
                       m);

    // Compiler flags
    GtkWidget *cflags_label= gtk_label_new(_("Compiler Flags"));
    gtk_widget_show(cflags_label);
    gtk_table_attach(GTK_TABLE(table), cflags_label, 0,1,1,2, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    GtkWidget *cflags_entry= gnome_entry_new("cflags");
    gtk_widget_show(cflags_entry);
    gtk_table_attach(GTK_TABLE(table), cflags_entry, 1,2,1,2, 
                     (GtkAttachOptions)(GTK_EXPAND | GTK_FILL), 
                     (GtkAttachOptions)0, 
                     0, 2);

    entry = gnome_entry_gtk_entry( GNOME_ENTRY(cflags_entry));
    gtk_entry_set_text(GTK_ENTRY(entry),model_get_compiler_flags(m));

    gtk_signal_connect(GTK_OBJECT(entry),"focus-out-event",
                       (GtkSignalFunc)set_cflags_cb,
                       m);
    
}

void create_prefs_box (model_t *m)
{
    // if it already exists, just show it
    if (global_prefs_box!=NULL) {
        gtk_widget_show(global_prefs_box);
	gdk_window_raise(global_prefs_box->window);
        return;
    }

    GtkTooltips *tooltips = gtk_tooltips_new ();

    global_prefs_box = gnome_dialog_new(
        _("User Preferences"), GNOME_STOCK_BUTTON_CLOSE, NULL);

    GtkWidget *vbox = (GNOME_DIALOG(global_prefs_box))->vbox;

    create_prefs_compiler_page(m,vbox,tooltips);

    gnome_dialog_set_close(GNOME_DIALOG(global_prefs_box), TRUE);
    gnome_dialog_close_hides(GNOME_DIALOG(global_prefs_box), TRUE);

    gtk_widget_show(global_prefs_box);
}
