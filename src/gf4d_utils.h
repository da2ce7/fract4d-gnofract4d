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

/* utility functions which fill gaps in GTK+ etc */

#ifndef _GF4D_UTILS_H_
#define _GF4D_UTILS_H_

#include <gtk/gtkobject.h>
#include <gtk/gtkmarshal.h>

typedef int (*GtkSignal_NONE__FLOAT)(GtkObject* object, gfloat, gpointer user_data);
typedef int (*GtkSignal_NONE__INT)(GtkObject* object, gint, gpointer user_data);

/* local prototypes */
void marshal_NONE__FLOAT(GtkObject*    object,
			 GtkSignalFunc func,
			 gpointer      func_data,
			 GtkArg*       args);

void marshal_NONE__INT(GtkObject*    object,
		       GtkSignalFunc func,
		       gpointer      func_data,
		       GtkArg*       args);

#endif /* _GF4D_UTILS_H_ */
