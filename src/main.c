/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
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

#include "model.h"
#include "callbacks.h"
#include "interface.h"
#include "support.h"
#include "gf4d_fractal.h"

int
main (int argc, char *argv[])
{
  GtkWidget *app;
  GnomeClient *client;
  model_t *m;

  bindtextdomain (PACKAGE, PACKAGE_LOCALE_DIR);
  textdomain (PACKAGE);

  gnome_init (PACKAGE, VERSION, argc, argv);

  m = model_new();
  
  client = gnome_master_client();
  gtk_signal_connect(GTK_OBJECT (client), "save_yourself",
		     GTK_SIGNAL_FUNC( save_session_cb ), m);
  gtk_signal_connect(GTK_OBJECT (client), "die",
		     GTK_SIGNAL_FUNC( quit_session_cb ), m);
  app = create_app (m);
  gtk_widget_show (app);

  gtk_main ();

  model_save(m);
  return 0;
}

