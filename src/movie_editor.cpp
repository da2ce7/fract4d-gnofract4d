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
#include <config.h>
#endif

#include "movie_editor.h"
#include "preview.h"
#include "gf4d_movie.h"
#include "tls.h"

static GtkWidget *movie_editor = NULL;
static Gf4dMovieFrame *selected_frame = NULL;

void update_frames_entry(GtkEntry *entry, gpointer user_data)
{
    Gf4dMovieFrame *fr = (Gf4dMovieFrame *)user_data;

    const gchar *text = gtk_entry_get_text(entry);
    int nFrames = 0;
    sscanf(text,"%d",&nFrames);
    
    gf4d_movie_frame_set_frames(fr, nFrames);
}


GtkWidget *create_frames_entry(Gf4dMovieFrame *fr)
{
    GtkWidget *frames_entry = gtk_entry_new();
    char text[17];
    sprintf(text, "%d", fr->nFrames);
    gtk_entry_set_text(GTK_ENTRY(frames_entry),text);

    /*
    g_signal_connect(GTK_OBJECT(frames_entry), "changed",
                       (GtkSignalFunc)update_frames_entry, fr);
                       
    */
    return frames_entry;
}

GtkWidget *create_strip_item(Gf4dMovieFrame *fr)
{
    Gf4dFractal *f = fr->f;
    GtkWidget *item = gtk_list_item_new();

    GtkWidget *hbox = gtk_hbox_new(false,0);
    GtkWidget *vbox = gtk_vbox_new(false,0);
    GtkWidget *frames_box = gtk_hbox_new(false,0);

    GtkWidget *preview = create_preview(f);
    
    GtkWidget *frames_entry = create_frames_entry(fr);
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

    gtk_object_set_data(GTK_OBJECT(item), "frame", fr);

    gtk_container_add(GTK_CONTAINER(item), hbox);
    gtk_widget_show_all(item);
    
    return item;
}

// given a pointer to a listitem, extract the relevant info
Gf4dMovieFrame *film_strip_get_frame(GtkWidget *item)
{
    return (Gf4dMovieFrame *)(gtk_object_get_data(GTK_OBJECT(item), "frame"));
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
        Gf4dMovieFrame *fr = (Gf4dMovieFrame *)(keyframes->data);
        GtkWidget *listitem = create_strip_item(fr);
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
    selected_frame = film_strip_get_frame(child);
    g_print("list selected %p\n", selected_frame);
}

void
list_clear_selection(GtkWidget *strip, gpointer user_data)
{
    selected_frame = NULL;
    g_print("cleared selection\n");
}

GtkWidget *create_film_strip(model_t *m)
{
    GtkWidget *strip = gtk_list_new();
    Gf4dMovie *movie = model_get_movie(m);

    gtk_list_set_selection_mode(GTK_LIST(strip), GTK_SELECTION_SINGLE);

    gtk_widget_show_all(strip);
    
    g_signal_connect(
        GTK_OBJECT(movie), "list_changed", 
        (GtkSignalFunc) list_update_callback,
        strip);

    g_signal_connect(
        GTK_OBJECT(strip), "selection_changed",
        (GtkSignalFunc) list_clear_selection, 
        NULL);

    g_signal_connect(
        GTK_OBJECT(strip), "select-child", 
        (GtkSignalFunc) list_set_selection,
        NULL);

    return strip;
}

void add_button_callback(GtkWidget *button, model_t *m)
{
    Gf4dMovieFrame *fr = 
        gf4d_movie_frame_new(model_get_fract(m), DEFAULT_FRAMES);

    gf4d_movie_add(model_get_movie(m), fr, selected_frame);
}

void render_button_callback(GtkWidget *button, model_t *m)
{
    Gf4dMovie *mov = model_get_movie(m);

    gboolean bIsRendering = gf4d_movie_is_calculating(mov);
    
    if(bIsRendering)
    {
        g_print("Currently Running - Interrupting\n");
        gf4d_movie_interrupt(mov);
    }
    else
    {
        g_print("Not Running - Starting\n");
        gf4d_movie_calc(mov, 1);        
    }
}

void remove_button_callback(GtkWidget *button, model_t *m)
{
    g_print("remove callback\n");
    Gf4dMovie *mov = model_get_movie(m);
    gf4d_movie_remove(mov, selected_frame);
}

void update_movie_button_text(Gf4dMovie *mov, gint status, gpointer user_data)
{
    GtkButton *button = GTK_BUTTON(user_data);
    GtkLabel *label = GTK_LABEL(GTK_BIN(button)->child);
    switch(status) {
    case GF4D_MOVIE_CALCULATING:
        gtk_label_set_text(label, _("Cancel"));
        break;
    case GF4D_MOVIE_DONE:
        gtk_label_set_text(label, _("Render"));
        break;
    default:
        gtk_label_set_text(label, _("Error"));
    }
}

void save_image_callback(Gf4dMovie *mov, int frame, model_t *m)
{
    // save the image
    gchar *savefile = g_strdup_printf("gf4d%03d.ppm",frame);
    g_print("saved %s\n",savefile);
    model_cmd_save_image(m,savefile);
    g_free(savefile);
}

GtkWidget *create_movie_commands(GtkWidget *strip, model_t *m)
{
    GtkWidget *hbox = gtk_hbox_new(TRUE, 0);

    // Add
    GtkWidget *add_button = gtk_button_new_with_label(_("Add"));
    gtk_box_pack_start(GTK_BOX(hbox), add_button, TRUE, TRUE, 0);

    g_signal_connect(GTK_OBJECT(add_button), "clicked", 
                       (GtkSignalFunc)add_button_callback, m);

    // Remove
    GtkWidget *remove_button = gtk_button_new_with_label(_("Remove"));
    gtk_box_pack_start(GTK_BOX(hbox), remove_button, TRUE, TRUE, 0);

    g_signal_connect(GTK_OBJECT(remove_button), "clicked", 
                       (GtkSignalFunc)remove_button_callback, m);

    // Render
    GtkWidget *render_button = gtk_button_new_with_label(_("Render"));
    gtk_box_pack_start(GTK_BOX(hbox), render_button, TRUE, TRUE, 0);

    g_signal_connect(
        GTK_OBJECT(render_button), 
        "clicked", 
        (GtkSignalFunc)render_button_callback, 
        m);

    Gf4dMovie *mov = model_get_movie(m);
    g_signal_connect(GTK_OBJECT(mov), "status_changed",
                       (GtkSignalFunc)update_movie_button_text,render_button);

    g_signal_connect(GTK_OBJECT(mov), "image_complete",
		       (GtkSignalFunc)save_image_callback, m);

    gtk_widget_show_all(hbox);

    return hbox;
}


void update_movie_progress_bar(Gf4dMovie *mov, gfloat progress, gpointer user_data)
{
    GtkProgressBar *bar = GTK_PROGRESS_BAR(user_data);

    gtk_progress_bar_update(bar, progress);
}

void update_movie_status_text(Gf4dMovie *mov, gint status, gpointer user_data)
{
    GtkLabel *label = GTK_LABEL(user_data);
    switch(status) {
    case GF4D_MOVIE_CALCULATING:
        gtk_label_set_text(label, _("Calculating..."));
        break;
    case GF4D_MOVIE_DONE:
        gtk_label_set_text(label, _("Finished"));
        break;
    default:
        gtk_label_set_text(label, _("Error"));
    }
}

void create_movie_editor(GtkWidget *menuitem, model_t *m)
{
    if(movie_editor)
    {
        gtk_widget_show(movie_editor);
	gdk_window_raise(movie_editor->window);
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
    GtkWidget *status_text = gtk_label_new("");

    g_signal_connect(
        GTK_OBJECT(model_get_movie(m)), 
        "progress_changed",
        (GtkSignalFunc) update_movie_progress_bar, 
        progress_bar);

    g_signal_connect(
        GTK_OBJECT(model_get_movie(m)), 
        "status_changed",
        (GtkSignalFunc) update_movie_status_text,
        status_text);

    GtkWidget *vbox = GNOME_DIALOG(movie_editor)->vbox;
    gtk_box_pack_start(GTK_BOX(vbox), window, TRUE, TRUE, 1);
    gtk_box_pack_start(GTK_BOX(vbox), commands, TRUE, TRUE, 1);
    gtk_box_pack_start(GTK_BOX(vbox), progress_bar, TRUE, TRUE, 1);
    gtk_box_pack_start(GTK_BOX(vbox), status_text, TRUE, TRUE, 1);
    
    gtk_widget_show_all(movie_editor);
}



