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

#include <gnome.h>

#include "callbacks.h"
#include "menus.h"

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
    model_t *m = (model_t *)client_data;

    model_write_autosave_file(m);
    return TRUE;
}

gint
quit_cb(GtkWidget *widget, GdkEventAny *event, gpointer user_data)
{
    return menu_quit_cb(widget,user_data);
}






