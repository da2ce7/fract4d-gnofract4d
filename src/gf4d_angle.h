/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2000 Aurelien Alleaume, Edwin Young
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

/* this is the widget which displays a round rotatable thing - 
 * based heavily on gtkdial */

#ifndef __GF4D_ANGLE_H__
#define __GF4D_ANGLE_H__



#include <gdk/gdk.h>
#include <gtk/gtkadjustment.h>
#include <gtk/gtkwidget.h>


#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


#define GF4D_ANGLE(obj)          GTK_CHECK_CAST (obj, gf4d_angle_get_type (), Gf4dAngle)
#define GF4D_ANGLE_CLASS(klass)  GTK_CHECK_CLASS_CAST (klass, gf4d_angle_get_type (), Gf4dAngleClass)
#define GF4D_IS_ANGLE(obj)       GTK_CHECK_TYPE (obj, gf4d_angle_get_type ())


    typedef struct _Gf4dAngle        Gf4dAngle;
    typedef struct _Gf4dAngleClass   Gf4dAngleClass;

    struct _Gf4dAngle
    {
        GtkWidget widget;

        /* update policy (GTK_UPDATE_[CONTINUOUS/DELAYED/DISCONTINUOUS]) */
        guint policy : 2;

        /* Button currently pressed or 0 if none */
        guint8 button;

        /* Dimensions of dial components */
        gint radius;
        gint pointer_width;

        /* ID of update timer, or 0 if none */
        guint32 timer;

        /* Current angle */
        gfloat angle;

        /* Old values from adjustment stored so we know when something changes */
        gfloat old_value;
        gfloat old_lower;
        gfloat old_upper;

        /* The adjustment object that stores the data for this dial */
        GtkAdjustment *adjustment;

	gchar *text;
    };

    struct _Gf4dAngleClass
    {
        GtkWidgetClass parent_klass;
    };


    GtkWidget*     gf4d_angle_new                    (GtkAdjustment *adjustment);
    guint          gf4d_angle_get_type               (void);
    GtkAdjustment* gf4d_angle_get_adjustment         (Gf4dAngle      *dial);
    void           gf4d_angle_set_update_policy      (Gf4dAngle      *dial,
                                                      GtkUpdateType  policy);

    void           gf4d_angle_set_adjustment         (Gf4dAngle      *dial,
                                                      GtkAdjustment *adjustment);
    void           gf4d_angle_set_label              (Gf4dAngle      *dial,
                                                      gchar          *text);

#ifdef __cplusplus
}
#endif /* __cplusplus */


#endif /* __GF4D_ANGLE_H__ */

