/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 * 
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

/* this is the widget which displays a square thing with 4 arrows
 * which is used to pan around. */

#ifndef __GF4D_FOURWAY_H__
#define __GF4D_FOURWAY_H__

#include <gdk/gdk.h>
#include <gtk/gtkadjustment.h>
#include <gtk/gtkwidget.h>

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#define GF4D_FOURWAY(obj)          GTK_CHECK_CAST (obj, gf4d_fourway_get_type (), Gf4dFourway)
#define GF4D_FOURWAY_CLASS(klass)  GTK_CHECK_CLASS_CAST (klass, gf4d_fourway_get_type (), Gf4dFourwayClass)
#define GF4D_IS_FOURWAY(obj)       GTK_CHECK_TYPE (obj, gf4d_fourway_get_type ())

    typedef struct _Gf4dFourway        Gf4dFourway;
    typedef struct _Gf4dFourwayClass   Gf4dFourwayClass;

    struct _Gf4dFourway
    {
        GtkWidget widget;

        /* Button currently pressed or 0 if none */
        guint8 button;

        /* Dimensions of dial components */
        gint radius;

        /* label text */
	gchar *text;

        /* last mouse position */
        gint last_x, last_y;
    };

    struct _Gf4dFourwayClass
    {
        GtkWidgetClass parent_klass;
        void (* value_slightly_changed)(Gf4dFourway *fourway); 
        void (* value_changed)(Gf4dFourway *fourway);
    };

    GtkWidget* gf4d_fourway_new (const gchar *label);
    guint gf4d_fourway_get_type (void);
    
#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __GF4D_FOURWAY_H__ */

