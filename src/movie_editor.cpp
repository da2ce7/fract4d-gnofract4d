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
#include <config.h>
#endif

#include "movie_editor.h"
#include "preview.h"
#include "gf4d_movie.h"

static GtkWidget *movie_editor = NULL;
static Gf4dFractal *selected_fractal = NULL;

GtkWidget *create_strip_item(Gf4dFractal *f)
{
    GtkWidget *item = gtk_list_item_new();

    GtkWidget *hbox = gtk_hbox_new(false,0);
    GtkWidget *vbox = gtk_vbox_new(false,0);
    GtkWidget *frames_box = gtk_hbox_new(false,0);

    GtkWidget *preview = create_preview(f);
    
    GtkWidget *frames_entry = gtk_entry_new();
    GtkWidget *frames_label = gtk_label_new(_("Frames :"));
    GtkWidget *type_menu = gtk_option_menu_new(); 
    GtkWidget *type_sub_menu = gtk_menu_new();
    GtkWidget *cut_item = gtk_menu_item_new_with_label(_("Cut to"));
    GtkWidget *line_item = gtk_menu_item_new_with_label(_("Straight line to"));
    GtkWidget *spline_item = gtk_menu_item_new_with_label(_("Curved line to"));

    gtk_menu_append(GTK_MENU(type_sub_menu), spline_item);
    gtk_menu_append(GTK_MENU(type_sub_menu), line_item);
    gtk_menu_append(GTK_MENU(type_sub_menu), cut_item);
    gtk_option_menu_set_menu(GTK_OPTION_MENU(type_menu), type_sub_menu);

    gtk_box_pack_start(GTK_BOX(frames_box), frames_label, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(frames_box), frames_entry, TRUE, TRUE, 0);

    gtk_box_pack_start(GTK_BOX(vbox), frames_box, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), type_menu, TRUE, TRUE, 0);
    
    gtk_box_pack_start(GTK_BOX(hbox), preview, FALSE, FALSE, 0);
    gtk_box_pack_end(GTK_BOX(hbox), vbox, TRUE, TRUE, 0);

    gtk_object_set_data(
        GTK_OBJECT(item), "shadow", preview_get_shadow(preview));

    gtk_container_add(GTK_CONTAINER(item), hbox);
    gtk_widget_show_all(item);
    
    return item;
}

// given a pointer to a listitem, extract the relevant info
Gf4dFractal *film_strip_get_fractal(GtkWidget *item)
{
    return GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(item), "shadow"));
}

/*
void create_strip_items(GtkWidget *strip)
{
    GList *itemlist = NULL;
    for(int i = 0; i < 5; ++i)
    {
        GtkWidget *item = create_strip_item();
        itemlist = g_list_prepend(itemlist, item);
    }

    gtk_list_append_items(GTK_LIST(strip), itemlist);

}
*/

// update the visible list to match the one in the object
void list_update_callback(Gf4dMovie *m, gpointer user_data)
{
    GtkWidget *display_list = GTK_WIDGET(user_data);

    // clear the current list
    g_print("clear\n");    
    gtk_list_clear_items(GTK_LIST(display_list), 0, -1);
    g_print("cleared\n");

    GList *keyframes = m->keyframes;

    GList *widgets = NULL;
    while(keyframes)
    {
        GtkWidget *listitem = create_strip_item(GF4D_FRACTAL(keyframes->data));
        g_print("item\n");
        widgets = g_list_append(widgets, listitem);
        keyframes = keyframes->next;
    }
    if(widgets)
    {
        gtk_list_append_items(GTK_LIST(display_list), widgets);
    }
    g_print("added to list\n");
}

void
list_set_selection(GtkWidget *strip, GtkWidget *child, gpointer user_data)
{
    selected_fractal = film_strip_get_fractal(child);
    g_print("selected %x\n", selected_fractal);
}

void
list_clear_selection(GtkWidget *strip, gpointer user_data)
{
    selected_fractal = NULL;
    g_print("cleared selection\n");
}

GtkWidget *create_film_strip(model_t *m)
{
    GtkWidget *strip = gtk_list_new();
    Gf4dMovie *movie = model_get_movie(m);

    gtk_list_set_selection_mode(GTK_LIST(strip), GTK_SELECTION_SINGLE);

    gtk_widget_show_all(strip);
    
    gtk_signal_connect(
        GTK_OBJECT(movie), "list_changed", 
        (GtkSignalFunc) list_update_callback,
        strip);

    gtk_signal_connect(
        GTK_OBJECT(strip), "selection_changed",
        (GtkSignalFunc) list_clear_selection, 
        NULL);

    gtk_signal_connect_after(
        GTK_OBJECT(strip), "select-child", 
        (GtkSignalFunc) list_set_selection,
        NULL);


    return strip;
}

void add_button_callback(GtkWidget *button, model_t *m)
{
    model_add_fract_to_movie(m, selected_fractal);
}

void render_button_callback(GtkWidget *button, model_t *m)
{
    static bool bStartRendering = true;
    Gf4dMovie *mov = model_get_movie(m);

    if(bStartRendering)
    {
        gtk_label_set_text(GTK_LABEL(GTK_BIN(button)->child), _("Cancel"));
        gf4d_movie_calc(mov, 1);        
    }
    else
    {
        gtk_label_set_text(GTK_LABEL(GTK_BIN(button)->child), _("Render"));
        gf4d_movie_interrupt(mov);
    }
    bStartRendering = !bStartRendering;
}

void remove_button_callback(GtkWidget *button, model_t *m)
{
    g_print("remove callback\n");
    Gf4dMovie *mov = model_get_movie(m);
    gf4d_movie_remove(mov, selected_fractal);
}

GtkWidget *create_movie_commands(GtkWidget *strip, model_t *m)
{
    GtkWidget *hbox = gtk_hbox_new(TRUE, 0);

    // Add
    GtkWidget *add_button = gtk_button_new_with_label(_("Add"));
    gtk_box_pack_start(GTK_BOX(hbox), add_button, TRUE, TRUE, 0);

    gtk_signal_connect(GTK_OBJECT(add_button), "clicked", 
                       (GtkSignalFunc)add_button_callback, m);

    // Remove
    GtkWidget *remove_button = gtk_button_new_with_label(_("Remove"));
    gtk_box_pack_start(GTK_BOX(hbox), remove_button, TRUE, TRUE, 0);

    gtk_signal_connect(GTK_OBJECT(remove_button), "clicked", 
                       (GtkSignalFunc)remove_button_callback, m);

    // Render
    GtkWidget *render_button = gtk_button_new_with_label(_("Render"));
    gtk_box_pack_start(GTK_BOX(hbox), render_button, TRUE, TRUE, 0);

    gtk_signal_connect(
        GTK_OBJECT(render_button), 
        "clicked", 
        (GtkSignalFunc)render_button_callback, 
        m);

    gtk_widget_show_all(hbox);

    return hbox;
}

void update_movie_progress_bar(Gf4dFractal *f, gfloat progress, gpointer user_data)
{
    GtkProgressBar *bar = GTK_PROGRESS_BAR(user_data);

    gtk_progress_bar_update(bar, progress);
}

void create_movie_editor(GtkWidget *menuitem, model_t *m)
{
    if(movie_editor)
    {
        gtk_widget_show(movie_editor);
        return;
    }

    movie_editor = gnome_dialog_new(PACKAGE " Movie Editor", _("Close"), NULL);

    gnome_dialog_button_connect_object(
        GNOME_DIALOG(movie_editor), 0,
        (GtkSignalFunc)gnome_dialog_close,
        GTK_OBJECT(movie_editor));

    gnome_dialog_close_hides(GNOME_DIALOG(movie_editor), TRUE);

    GtkWidget *film_strip = create_film_strip(m);
    GtkWidget *window = gtk_scrolled_window_new(NULL,NULL);
    gtk_scrolled_window_add_with_viewport(GTK_SCROLLED_WINDOW(window), film_strip);
    gtk_widget_set_usize(window, 300, 200);

    GtkWidget *commands = create_movie_commands(film_strip, m);

    GtkWidget *progress_bar = gtk_progress_bar_new();
    
    gtk_signal_connect(GTK_OBJECT(model_get_movie(m)), "progress_changed",
                       (GtkSignalFunc) update_movie_progress_bar, progress_bar);

    GtkWidget *vbox = GNOME_DIALOG(movie_editor)->vbox;
    gtk_box_pack_start(GTK_BOX(vbox), window, TRUE, TRUE, 1);
    gtk_box_pack_start(GTK_BOX(vbox), commands, TRUE, TRUE, 1);
    gtk_box_pack_start(GTK_BOX(vbox), progress_bar, TRUE, TRUE, 1);
    gtk_widget_show_all(movie_editor);
}



