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

#include "cmapbrowser.h"
#include "drawingareas.h"
#include "colorizer_public.h"

#include <dirent.h>

#define PREVIEW_SIZE 40
#define BYTE_SIZE ((PREVIEW_SIZE) * (PREVIEW_SIZE) * 3)
void
preview_status_callback(Gf4dFractal *f, gint val, void *user_data)
{
    if(val != GF4D_FRACTAL_DONE) return;
    
    // finished: start filling in drawing areas
    GtkWidget *table = GTK_WIDGET(user_data);

    // for each list item
    GList *children = gtk_container_children(GTK_CONTAINER(table));
    while(children)
    {
        GtkWidget *button = GTK_WIDGET(children->data);
        GtkWidget *drawable = GTK_BIN(button)->child;
        g_assert(drawable);

        // recolor with image's colormap
        char *fname= (char *)gtk_object_get_data(GTK_OBJECT(drawable), "filename");

        gf4d_fractal_set_color_type(f, COLORIZER_CMAP);
        gf4d_fractal_set_cmap_file(f, fname);
        gf4d_fractal_recolor(f);

        // copy contents of image
        guchar *img = (guchar *)gtk_object_get_data(GTK_OBJECT(drawable),"image");
        g_assert(img);
        memcpy(img,gf4d_fractal_get_image(f), BYTE_SIZE);

        redraw_image_rect(drawable, img, 0, 0, PREVIEW_SIZE, PREVIEW_SIZE, PREVIEW_SIZE);

        children = children->next;
    }
}

gint 
preview_expose_event (GtkWidget *widget, GdkEventExpose *event, gpointer user_data)
{
    guchar *image = (guchar *)gtk_object_get_data(GTK_OBJECT(widget), "image");

    if(image)
    {
        redraw_image_rect(widget, image, 
                          event->area.x, event->area.y, 
                          event->area.width, event->area.height,
                          PREVIEW_SIZE);
    }
    return FALSE;
}

void
preview_button_clicked(GtkWidget *button, gpointer user_data)
{
    GtkWidget *drawable = GTK_BIN(button)->child;
    model_t *m = (model_t *)user_data;

    char *filename = (char *)gtk_object_get_data(GTK_OBJECT(drawable), "filename");

    if(model_cmd_start(m, "preview"))
    {
        Gf4dFractal *f = model_get_fract(m);
        gf4d_fractal_set_color_type(f, COLORIZER_CMAP);
        gf4d_fractal_set_cmap_file(f, filename);
        model_cmd_finish(m, "preview");
    }
}

GtkWidget *
create_cmap_browser_item(
    GtkWidget *table, 
    model_t *m, 
    GtkTooltips *tips,
    gchar *dirname, 
    gchar *filename,
    int x,
    int y)
{
    // make the button 
    GtkWidget *button = gtk_button_new();
    gtk_widget_show(button);
    gtk_container_set_border_width(GTK_CONTAINER(button), 0);

    // make the drawable 
    GtkWidget *drawing_area=NULL;
    gtk_widget_push_visual (gdk_rgb_get_visual ());
    gtk_widget_push_colormap (gdk_rgb_get_cmap ());    
    drawing_area = gtk_drawing_area_new();
    gtk_widget_pop_colormap ();
    gtk_widget_pop_visual ();

    // resize
    gtk_drawing_area_size(GTK_DRAWING_AREA(drawing_area), PREVIEW_SIZE, PREVIEW_SIZE);

    // buffer for image
    guchar *img = new guchar[BYTE_SIZE];
    gtk_object_set_data(GTK_OBJECT(drawing_area), "image", img);

    // store filename of .map file
    char *full_name = g_concat_dir_and_file(dirname, filename);
    gtk_object_set_data(GTK_OBJECT(drawing_area), "filename", full_name);

    // get drawable to redraw itself properly
    gtk_signal_connect (
        GTK_OBJECT(drawing_area), "expose_event", 
        (GtkSignalFunc) preview_expose_event, NULL);
    
    gtk_widget_show(drawing_area);

    // add to table 
    gtk_table_attach(
        GTK_TABLE(table), 
        button,
        x,x+1,y,y+1, 
        (enum GtkAttachOptions)0, (enum GtkAttachOptions)0, 
        0, 0);

    // set tip to filename
    gtk_tooltips_set_tip(tips, button, filename, NULL);

    gtk_container_add(GTK_CONTAINER(button), drawing_area);
 
    // button callback
    gtk_signal_connect (
        GTK_OBJECT(button), "clicked",
        (GtkSignalFunc) preview_button_clicked, m);

    return button;
}

void 
update_previews(GtkWidget *button, gpointer user_data)
{
    model_t *m = (model_t *)user_data;
    GtkWidget *dialog = gtk_widget_get_toplevel(button);
    Gf4dFractal *f = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(dialog), "fractal"));

    // update this fractal with the main one
    gf4d_fractal_update_fract(f,model_get_fract(m));
 
    // tweak its parameters
    gf4d_fractal_set_resolution(f,PREVIEW_SIZE,PREVIEW_SIZE);
    gf4d_fractal_set_aa(f, (e_antialias)0);
    
    // recalc
    gf4d_fractal_calc(f,1 );
}

static GtkWidget *dialog = NULL;

GtkWidget *
create_cmap_browser(GtkMenuItem *menu, model_t *m)
{
    if(dialog) 
    {
        gtk_widget_show(dialog);
        return dialog;
    }

    /* toplevel */
    dialog = gnome_dialog_new(
        _("Choose a colormap"), 
        _("Update"), GNOME_STOCK_BUTTON_CLOSE, NULL);

    gnome_dialog_button_connect(
        GNOME_DIALOG(dialog), 0,
        (GtkSignalFunc)update_previews,
        m);

    gnome_dialog_button_connect_object(
        GNOME_DIALOG(dialog), 1,
        (GtkSignalFunc)gnome_dialog_close,
        GTK_OBJECT(dialog));


    gnome_dialog_close_hides(GNOME_DIALOG(dialog), TRUE);
    gtk_window_set_policy(GTK_WINDOW(dialog), TRUE, TRUE, FALSE);
    gtk_window_set_default_size(GTK_WINDOW(dialog), PREVIEW_SIZE * 5 , PREVIEW_SIZE * 12);
    gtk_widget_show(dialog);

    /* retrieve vbox */
    GtkWidget *vbox = GNOME_DIALOG(dialog)->vbox;
    
    /* make a scrolling window w. viewport for list to live in */
    GtkWidget *scrolledwindow = gtk_scrolled_window_new(NULL, NULL);

    gtk_widget_show(scrolledwindow);

    /* add scrolling list */
    GtkWidget *table = gtk_table_new(17,4, TRUE);
    gtk_widget_show(table);

    gtk_scrolled_window_add_with_viewport(
        GTK_SCROLLED_WINDOW(scrolledwindow),table);

    gtk_box_pack_start(GTK_BOX(vbox), scrolledwindow, TRUE, TRUE, 0);

    /* create tooltip group */
    GtkTooltips *tips = gtk_tooltips_new();
    gtk_tooltips_enable(tips);

    /* copy the main fractal and make a mini version */
    Gf4dFractal *f = gf4d_fractal_copy(model_get_fract(m));
    gf4d_fractal_set_resolution(f,PREVIEW_SIZE,PREVIEW_SIZE);
    gf4d_fractal_set_aa(f, (e_antialias)0);
 
    // store a pointer to the fract
    gtk_object_set_data(GTK_OBJECT(dialog), "fractal", f);

    gchar *mapdir = gnome_datadir_file("maps/" PACKAGE  "/");

    DIR *dir = opendir(mapdir);
    struct dirent *dirEntry;

    int i = 0;
    while(dir && (dirEntry = readdir (dir)))
    {
        const char *ext = g_extension_pointer(dirEntry->d_name);
        if(ext && strcmp(ext,"map")==0)
        {
            // it's probably a map file: try to add to table
            create_cmap_browser_item(table, m, tips, mapdir, dirEntry->d_name, i % 4, i/4);
            ++i;
        }

    }
    if(dir) closedir(dir);

    gtk_signal_connect(
        GTK_OBJECT(f), "status_changed", 
        GTK_SIGNAL_FUNC(preview_status_callback),
        table);

    gf4d_fractal_calc(f,1);
    return dialog;
}

#if 0
// how to make a GnomePixmap
    /* make the item's image */
    guchar data[32 * 32 * 3];
    for(unsigned int i = 0; i < sizeof(data) ; ++i)
    {
        data[i] = i % 256;
    }
    GtkWidget *pixmap = gnome_pixmap_new_from_rgb_d(data,NULL,32,32);
#endif

