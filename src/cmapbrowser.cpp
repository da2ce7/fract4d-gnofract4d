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

/* The colormap browser is a toplevel window which renders a small preview
 * of the current fractal view using each available colormap. This works by
 * copying the current fractal into a private one whenever "update" is called, 
 * then calling recolor() for each map and putting the results into a drawable
 */

/* TODO
   would gnome_pixmaps be more efficient/simpler? 
   use continuous potential
*/

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "cmapbrowser.h"
#include "drawingareas.h"
#include "colorizer.h"
#include "preview.h"

#include <dirent.h>

#define BYTE_SIZE ((PREVIEW_SIZE) * (PREVIEW_SIZE) * 3)

void
update_preview_image(Gf4dFractal *f, GtkWidget *drawable)
{
    g_assert(drawable);

    // fractal takes ownership of new cizer
    colorizer_t *cizer = (colorizer_t *)gtk_object_get_data(
        GTK_OBJECT(drawable), "colorizer"); 
    g_assert(cizer);
    
    gf4d_fractal_set_colorizer(f,cizer);
    gf4d_fractal_recolor(f);
    
    // copy contents of image to drawable's backing store
    guchar *img = (guchar *)gtk_object_get_data(GTK_OBJECT(drawable),"image");
    g_assert(img);
    memcpy(img,gf4d_fractal_get_image(f), BYTE_SIZE);
    
    // update currently displayed image
    redraw_image_rect(drawable, img, 0, 0, PREVIEW_SIZE, PREVIEW_SIZE, PREVIEW_SIZE);
}

/* called back by the private fractal as it renders */
void
preview_status_callback(Gf4dFractal *f, gint val, void *user_data)
{
    if(val != GF4D_FRACTAL_DONE) return;
    
    // finished: start filling in drawing areas
    GtkWidget *table = GTK_WIDGET(user_data);
    g_assert(table);

    // for each preview item
    GList *children = gtk_container_children(GTK_CONTAINER(table));
    while(children)
    {
        if(GTK_IS_BUTTON(children->data))
        {
            GtkWidget *button = GTK_WIDGET(children->data);
            GtkWidget *drawable = GTK_BIN(button)->child;
            if(drawable && GTK_IS_DRAWING_AREA(drawable))
            {
                update_preview_image(f, drawable);
            }
        }
        children = children->next;
    }

    // FIXME: update rgb preview too
}

/* update the drawables whenever they're shown */
gint 
preview_expose_event (GtkWidget *widget, GdkEventExpose *event, gpointer user_data)
{
    guchar *image = (guchar *)gtk_object_get_data(GTK_OBJECT(widget), "image");

    if(image)
    {
        redraw_image_rect(
            widget, image, 
            event->area.x, event->area.y, 
            event->area.width, event->area.height,
            PREVIEW_SIZE);
    }
    return FALSE;
}

/* called when you click a preview button, surprisingly.
   updates the main fractal with the selected colormap
*/

void
preview_button_clicked(GtkWidget *button, gpointer user_data)
{
    GtkWidget *drawable = GTK_BIN(button)->child;
    model_t *m = (model_t *)user_data;

    colorizer_t *cizer = (colorizer_t *)gtk_object_get_data(GTK_OBJECT(drawable), "colorizer");
    g_assert(cizer);

    if(model_cmd_start(m, "preview"))
    {
        Gf4dFractal *f = model_get_fract(m);
        gf4d_fractal_set_colorizer(f, cizer);
        model_cmd_finish(m, "preview");
    }
}

/* create a single button in the browser */
GtkWidget *
create_cmap_browser_item(
    model_t *m, 
    GtkTooltips *tips,
    colorizer_t *cizer, 
    gchar *name)
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

    gtk_object_set_data(GTK_OBJECT(drawing_area), "colorizer", cizer);

    // get drawable to redraw itself properly
    gtk_signal_connect (
        GTK_OBJECT(drawing_area), "expose_event", 
        (GtkSignalFunc) preview_expose_event, NULL);
    
    gtk_widget_show(drawing_area);

    // set tip to filename
    gtk_tooltips_set_tip(tips, button, name, NULL);

    gtk_container_add(GTK_CONTAINER(button), drawing_area);
 
    // button callback
    gtk_signal_connect (
        GTK_OBJECT(button), "clicked",
        (GtkSignalFunc) preview_button_clicked, m);

    return button;
}

void
add_to_table(GtkWidget *table, GtkWidget *button, int x, int y)
{
    gtk_table_attach(
        GTK_TABLE(table), 
        button,
        x,x+1,y,y+1, 
        (enum GtkAttachOptions)0, (enum GtkAttachOptions)0, 
        0, 0);
}

/* update the fractal from the main image and recalculate the local copy,
   the preview images are updated by a callback from the fractal calculation */

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

/* don't destroy the dialog when it's closed, just hide it */
static GtkWidget *dialog = NULL;


/* add a directory full of map-files to the browser */
void
add_map_directory(GtkWidget *table, model_t *m, char *mapdir, GtkTooltips *tips)
{
    DIR *dir = opendir(mapdir);
    struct dirent *dirEntry;

    int i = 0;
    while(dir && (dirEntry = readdir (dir)))
    {
        const char *ext = g_extension_pointer(dirEntry->d_name);
        if(ext && strcmp(ext,"map")==0)
        {
            // get full filename of .map file & create a colorizer from it
            char *full_name = g_concat_dir_and_file(mapdir, dirEntry->d_name);
            cmap_colorizer *cizer = new cmap_colorizer();
            cizer->set_cmap_file(full_name);
            g_free(full_name);

            // add it to table
            GtkWidget *item = create_cmap_browser_item(m, tips, cizer, dirEntry->d_name);
            add_to_table(table, item, i % 8, i / 8);

            ++i;
        }

    }    
    if(dir) closedir(dir);
}

GtkWidget *
create_current_maps_page(GtkWidget *notebook, model_t *m)
{
    /* make a scrolling window w. viewport for list to live in */
    GtkWidget *scrolledwindow = gtk_scrolled_window_new(NULL, NULL);

    gtk_widget_show(scrolledwindow);

    /* add table of previews */
    GtkWidget *table = gtk_table_new(1,1, TRUE); // will expand as we add items
    gtk_widget_show(table);

    gtk_scrolled_window_add_with_viewport(
        GTK_SCROLLED_WINDOW(scrolledwindow),table);

    /* create tooltip group */
    GtkTooltips *tips = gtk_tooltips_new();
    gtk_tooltips_enable(tips);

    gchar *mapdir = gnome_datadir_file("maps/" PACKAGE  "/");

    add_map_directory(table, m, mapdir, tips);

    /* add the chooser page to the notebook */
    gtk_notebook_append_page(
        GTK_NOTEBOOK(notebook), 
        scrolledwindow, 
        gtk_label_new(_("Color Maps")));

    return table;
}

void
color_change_callback(GtkWidget *colorsel, gpointer user_data)
{
    gdouble colors[8];
    gtk_color_selection_get_color(GTK_COLOR_SELECTION(colorsel), colors);

    GtkWidget *button = GTK_WIDGET(user_data);  
    GtkWidget *drawable = GTK_BIN(button)->child;
    rgb_colorizer *rgb_cizer = (rgb_colorizer *)
        gtk_object_get_data(GTK_OBJECT(drawable), "colorizer");

    Gf4dFractal *f = GF4D_FRACTAL(gtk_object_get_data(GTK_OBJECT(dialog), "fractal"));

    rgb_cizer->set_colors(colors[0],colors[1],colors[2]);

    update_preview_image(f, drawable);
}

GtkWidget *
create_new_color_page(GtkWidget *notebook, model_t *m)
{
    GtkWidget *table = gtk_table_new(2,2,FALSE);
    gtk_widget_show(table);

    GtkTooltips *tips = gtk_tooltips_new();
    gtk_tooltips_enable(tips);

    GtkWidget *colorsel = gtk_color_selection_new();
    gtk_widget_show(colorsel);
    gtk_table_attach(GTK_TABLE(table), colorsel, 0, 2, 0, 1, 
                     (GtkAttachOptions) 0, (GtkAttachOptions) 0, 0, 0);

    gtk_notebook_append_page(
        GTK_NOTEBOOK(notebook),
        table,
        gtk_label_new(_("Color Range")));

    GtkWidget * label = gtk_label_new(_("Click to apply to main fractal >>"));
    gtk_widget_show(label);
    gtk_table_attach(GTK_TABLE(table), label , 0, 1, 1, 2, 
                     (GtkAttachOptions) 0, (GtkAttachOptions) 0, 0, 0);

    rgb_colorizer *cizer = new rgb_colorizer();
    GtkWidget *rgb_preview = create_cmap_browser_item(m, tips, cizer, "fred");
    gtk_table_attach(GTK_TABLE(table), rgb_preview, 1, 2, 1, 2, 
                     (GtkAttachOptions) 0, (GtkAttachOptions) 0, 0, 0);

    /* connect up color selector callbacks */
    gtk_signal_connect(
        GTK_OBJECT(colorsel), "color-changed",
        (GtkSignalFunc) color_change_callback,
        (gpointer) rgb_preview);

    return table;
}

/* create or show the colormap browser */
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
        _("Refresh"), GNOME_STOCK_BUTTON_CLOSE, NULL);

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
    gtk_widget_show(dialog);

    /* retrieve vbox */
    GtkWidget *vbox = GNOME_DIALOG(dialog)->vbox;

    /* copy the main fractal and make a mini version */
    Gf4dFractal *f = gf4d_fractal_copy(model_get_fract(m));
    gf4d_fractal_set_resolution(f,PREVIEW_SIZE,PREVIEW_SIZE);
    gf4d_fractal_set_aa(f, (e_antialias)0);
 
    // store a pointer to the fract
    gtk_object_set_data(GTK_OBJECT(dialog), "fractal", f);

 
    /* make notebook */
    GtkWidget *notebook = gtk_notebook_new();
    gtk_widget_show(notebook);
    gtk_box_pack_start(GTK_BOX(vbox), notebook, TRUE, TRUE, 0);

    /* make pages */
    GtkWidget *table = create_current_maps_page(notebook, m);
    GtkWidget *table2 = create_new_color_page(notebook, m);

    // setup callbacks from fract's calculations

    gtk_signal_connect(
        GTK_OBJECT(f), "status_changed", 
        GTK_SIGNAL_FUNC(preview_status_callback),
        table);

    gtk_signal_connect(
        GTK_OBJECT(f), "status_changed", 
        GTK_SIGNAL_FUNC(preview_status_callback),
        table2);

    /* kick off async update */
    gf4d_fractal_calc(f,1);

    return dialog;
}


