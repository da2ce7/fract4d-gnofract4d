/* example-start gtkdial gtkdial.c */

/* GTK - The GIMP Toolkit
 * Copyright (C) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald
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
#include <math.h>
#include <stdio.h>
#include <gtk/gtkmain.h>
#include <gtk/gtksignal.h>

#include "gf4d_angle.h"

#define SCROLL_DELAY_LENGTH  300
#define DIAL_DEFAULT_SIZE 32

/* Forward declarations */

static void gf4d_angle_class_init               (Gf4dAngleClass    *klass);
static void gf4d_angle_init                     (Gf4dAngle         *dial);
static void gf4d_angle_destroy                  (GtkObject        *object);
static void gf4d_angle_realize                  (GtkWidget        *widget);
static void gf4d_angle_size_request             (GtkWidget      *widget,
						 GtkRequisition *requisition);
static void gf4d_angle_size_allocate            (GtkWidget     *widget,
						 GtkAllocation *allocation);
static gint gf4d_angle_expose                   (GtkWidget        *widget,
						 GdkEventExpose   *event);
static gint gf4d_angle_button_press             (GtkWidget        *widget,
						 GdkEventButton   *event);
static gint gf4d_angle_button_release           (GtkWidget        *widget,
						 GdkEventButton   *event);
static gint gf4d_angle_motion_notify            (GtkWidget        *widget,
						 GdkEventMotion   *event);
static gint gf4d_angle_timer                    (Gf4dAngle         *dial);

static void gf4d_angle_update_mouse             (Gf4dAngle *dial, gint x, gint y);
static void gf4d_angle_update                   (Gf4dAngle *dial);
static void gf4d_angle_adjustment_changed       (GtkAdjustment    *adjustment,
						 gpointer          data);
static void gf4d_angle_adjustment_value_changed (GtkAdjustment    *adjustment,
						 gpointer          data);

/* Local data */

static GtkWidgetClass *parent_class = NULL;
static gfloat min_angle = -M_PI/2.0; // (-1.0 * M_PI/6.0);
static gfloat max_angle = 3 * M_PI/2.0; // ( 7.0 * M_PI/6.0);

guint
gf4d_angle_get_type ()
{
	static guint dial_type = 0;

	if (!dial_type)
	{
		GtkTypeInfo dial_info =
		{
			"Gf4dAngle",
			sizeof (Gf4dAngle),
			sizeof (Gf4dAngleClass),
			(GtkClassInitFunc) gf4d_angle_class_init,
			(GtkObjectInitFunc) gf4d_angle_init,
			(GtkArgSetFunc) NULL,
			(GtkArgGetFunc) NULL,
		};

		dial_type = gtk_type_unique (gtk_widget_get_type (), &dial_info);
	}

	return dial_type;
}

static void
gf4d_angle_class_init (Gf4dAngleClass *class)
{
	GtkObjectClass *object_class;
	GtkWidgetClass *widget_class;

	object_class = (GtkObjectClass*) class;
	widget_class = (GtkWidgetClass*) class;

	parent_class = gtk_type_class (gtk_widget_get_type ());

	object_class->destroy = gf4d_angle_destroy;

	widget_class->realize = gf4d_angle_realize;
	widget_class->expose_event = gf4d_angle_expose;
	widget_class->size_request = gf4d_angle_size_request;
	widget_class->size_allocate = gf4d_angle_size_allocate;
	widget_class->button_press_event = gf4d_angle_button_press;
	widget_class->button_release_event = gf4d_angle_button_release;
	widget_class->motion_notify_event = gf4d_angle_motion_notify;
}

static void
gf4d_angle_init (Gf4dAngle *dial)
{
	dial->button = 0;
	dial->policy = GTK_UPDATE_CONTINUOUS;
	dial->timer = 0;
	dial->radius = 0;
	dial->pointer_width = 0;
	dial->angle = 0.0;
	dial->old_value = 0.0;
	dial->old_lower = 0.0;
	dial->old_upper = 0.0;
	dial->adjustment = NULL;
	dial->text=NULL;
}

GtkWidget*
gf4d_angle_new (GtkAdjustment *adjustment)
{
	Gf4dAngle *dial;

	dial = gtk_type_new (gf4d_angle_get_type ());

	if (!adjustment)
		adjustment = (GtkAdjustment*) gtk_adjustment_new (0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

	gf4d_angle_set_adjustment (dial, adjustment);

	return GTK_WIDGET (dial);
}

static void
gf4d_angle_destroy (GtkObject *object)
{
	Gf4dAngle *dial;

	g_return_if_fail (object != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (object));

	dial = GF4D_ANGLE (object);

	if (dial->adjustment)
		gtk_object_unref (GTK_OBJECT (dial->adjustment));

	if (GTK_OBJECT_CLASS (parent_class)->destroy)
		(* GTK_OBJECT_CLASS (parent_class)->destroy) (object);
}

GtkAdjustment*
gf4d_angle_get_adjustment (Gf4dAngle *dial)
{
	g_return_val_if_fail (dial != NULL, NULL);
	g_return_val_if_fail (GF4D_IS_ANGLE (dial), NULL);

	return dial->adjustment;
}

void
gf4d_angle_set_update_policy (Gf4dAngle      *dial,
			      GtkUpdateType  policy)
{
	g_return_if_fail (dial != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (dial));

	dial->policy = policy;
}

void
gf4d_angle_set_label(Gf4dAngle *dial, gchar *text)
{
	g_return_if_fail(dial != NULL);
	g_return_if_fail(GF4D_IS_ANGLE(dial));
	dial->text = g_strdup(text);
}

void
gf4d_angle_set_adjustment (Gf4dAngle      *dial,
			   GtkAdjustment *adjustment)
{
	g_return_if_fail (dial != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (dial));

	if (dial->adjustment)
	{
		gtk_signal_disconnect_by_data (GTK_OBJECT (dial->adjustment), (gpointer) dial);
		gtk_object_unref (GTK_OBJECT (dial->adjustment));
	}

	dial->adjustment = adjustment;
	gtk_object_ref (GTK_OBJECT (dial->adjustment));

	gtk_signal_connect (GTK_OBJECT (adjustment), "changed",
			    (GtkSignalFunc) gf4d_angle_adjustment_changed,
			    (gpointer) dial);
	gtk_signal_connect (GTK_OBJECT (adjustment), "value_changed",
			    (GtkSignalFunc) gf4d_angle_adjustment_value_changed,
			    (gpointer) dial);

	dial->old_value = adjustment->value;
	dial->old_lower = adjustment->lower;
	dial->old_upper = adjustment->upper;

	gf4d_angle_update (dial);
}

static void
gf4d_angle_realize (GtkWidget *widget)
{
	Gf4dAngle *dial;
	GdkWindowAttr attributes;
	gint attributes_mask;

	g_return_if_fail (widget != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (widget));

	GTK_WIDGET_SET_FLAGS (widget, GTK_REALIZED);
	dial = GF4D_ANGLE (widget);

	attributes.x = widget->allocation.x;
	attributes.y = widget->allocation.y;
	attributes.width = widget->allocation.width;
	attributes.height = widget->allocation.height;
	attributes.wclass = GDK_INPUT_OUTPUT;
	attributes.window_type = GDK_WINDOW_CHILD;
	attributes.event_mask = gtk_widget_get_events (widget) | 
		GDK_EXPOSURE_MASK | GDK_BUTTON_PRESS_MASK | 
		GDK_BUTTON_RELEASE_MASK | GDK_POINTER_MOTION_MASK |
		GDK_POINTER_MOTION_HINT_MASK;
	attributes.visual = gtk_widget_get_visual (widget);
	attributes.colormap = gtk_widget_get_colormap (widget);

	attributes_mask = GDK_WA_X | GDK_WA_Y | GDK_WA_VISUAL | GDK_WA_COLORMAP;
	widget->window = gdk_window_new (widget->parent->window, &attributes, attributes_mask);

	widget->style = gtk_style_attach (widget->style, widget->window);

	gdk_window_set_user_data (widget->window, widget);

	gtk_style_set_background (widget->style, widget->window, GTK_STATE_ACTIVE);
}

static void 
gf4d_angle_size_request (GtkWidget      *widget,
			 GtkRequisition *requisition)
{
	requisition->width = DIAL_DEFAULT_SIZE;
	requisition->height = DIAL_DEFAULT_SIZE;
}

static void
gf4d_angle_size_allocate (GtkWidget     *widget,
			  GtkAllocation *allocation)
{
	Gf4dAngle *dial;

	g_return_if_fail (widget != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (widget));
	g_return_if_fail (allocation != NULL);

	widget->allocation = *allocation;
	dial = GF4D_ANGLE (widget);

	if (GTK_WIDGET_REALIZED (widget))
	{

		gdk_window_move_resize (widget->window,
					allocation->x, allocation->y,
					allocation->width, allocation->height);

	}
	dial->radius = MIN(allocation->width,allocation->height) * 0.5;
	dial->pointer_width = dial->radius / 5;
}

static gint
gf4d_angle_expose (GtkWidget      *widget,
		   GdkEventExpose *event)
{
	Gf4dAngle *dial;
	gdouble s,c;
	gint xc, yc;

	g_return_val_if_fail (widget != NULL, FALSE);
	g_return_val_if_fail (GF4D_IS_ANGLE (widget), FALSE);
	g_return_val_if_fail (event != NULL, FALSE);

	if (event->count > 0)
		return FALSE;
  
	dial = GF4D_ANGLE (widget);

	gdk_window_clear_area (widget->window,
			       0, 0,
			       widget->allocation.width,
			       widget->allocation.height);

	xc = widget->allocation.width/2;
	yc = widget->allocation.height/2;

	/* Draw text (rather badly - should perhaps use label widget) */
	if(dial->text)
	{
		gint l = gdk_string_width(widget->style->font,dial->text);
		gint h = gdk_string_height(widget->style->font, dial->text);
		
		gtk_draw_string(widget->style,
				widget->window,
				GTK_STATE_NORMAL,
				xc - l/2,
				yc - h/2,
				dial->text);
	}

	/* Draw circle */
	gdk_draw_arc(widget->window,
		     widget->style->fg_gc[widget->state],
		     0,
		     xc-dial->radius,
		     yc-dial->radius,
		     dial->radius*2-1,
		     dial->radius*2-1,
		     0,
		     360 * 64);
		     
	/* Draw pointer */

	s = sin(dial->angle);
	c = cos(dial->angle);

	{
		gint pyr = MAX(dial->radius*0.1,4);
		gint pxc = xc + c * (dial->radius-pyr);
		gint pyc = yc - s * (dial->radius-pyr);


		gdk_draw_arc(widget->window,
			     widget->style->fg_gc[widget->state],
			     1,
			     pxc - pyr,
			     pyc - pyr,
			     pyr*2-1,
			     pyr*2-1,
			     0,
			     360 * 64);
	}
  
	return FALSE;
}

static gint
gf4d_angle_button_press (GtkWidget      *widget,
			 GdkEventButton *event)
{
	Gf4dAngle *dial;

	g_return_val_if_fail (widget != NULL, FALSE);
	g_return_val_if_fail (GF4D_IS_ANGLE (widget), FALSE);
	g_return_val_if_fail (event != NULL, FALSE);

	dial = GF4D_ANGLE (widget);
  
	if (!dial->button)
	{
		gtk_grab_add (widget);
		dial->button = event->button;
		gf4d_angle_update_mouse (dial, event->x, event->y);
	}

	return FALSE;
}

static gint
gf4d_angle_button_release (GtkWidget      *widget,
			   GdkEventButton *event)
{
	Gf4dAngle *dial;

	g_return_val_if_fail (widget != NULL, FALSE);
	g_return_val_if_fail (GF4D_IS_ANGLE (widget), FALSE);
	g_return_val_if_fail (event != NULL, FALSE);

	dial = GF4D_ANGLE (widget);

	if (dial->button == event->button)
	{
		gtk_grab_remove (widget);

		dial->button = 0;

		if (dial->policy == GTK_UPDATE_DELAYED)
			gtk_timeout_remove (dial->timer);
      
		if ((dial->policy != GTK_UPDATE_CONTINUOUS) &&
		    (dial->old_value != dial->adjustment->value))
			gtk_signal_emit_by_name (GTK_OBJECT (dial->adjustment), "value_changed");
	}

	return FALSE;
}

static gint
gf4d_angle_motion_notify (GtkWidget      *widget,
			  GdkEventMotion *event)
{
	Gf4dAngle *dial;
	GdkModifierType mods;
	gint x, y, mask;

	g_return_val_if_fail (widget != NULL, FALSE);
	g_return_val_if_fail (GF4D_IS_ANGLE (widget), FALSE);
	g_return_val_if_fail (event != NULL, FALSE);

	dial = GF4D_ANGLE (widget);

	if (dial->button != 0)
	{
		x = event->x;
		y = event->y;

		if (event->is_hint || (event->window != widget->window))
			gdk_window_get_pointer (widget->window, &x, &y, &mods);

		switch (dial->button)
		{
		case 1:
			mask = GDK_BUTTON1_MASK;
			break;
		case 2:
			mask = GDK_BUTTON2_MASK;
			break;
		case 3:
			mask = GDK_BUTTON3_MASK;
			break;
		default:
			mask = 0;
			break;
		}

		if (mods & mask)
			gf4d_angle_update_mouse (dial, x,y);
	}

	return FALSE;
}

static gint
gf4d_angle_timer (Gf4dAngle *dial)
{
	g_return_val_if_fail (dial != NULL, FALSE);
	g_return_val_if_fail (GF4D_IS_ANGLE (dial), FALSE);

	if (dial->policy == GTK_UPDATE_DELAYED)
		gtk_signal_emit_by_name (GTK_OBJECT (dial->adjustment), "value_changed");

	return FALSE;
}

static void
gf4d_angle_update_mouse (Gf4dAngle *dial, gint x, gint y)
{
	gint xc, yc;
	gfloat old_value;
	gfloat min, max;

	g_return_if_fail (dial != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (dial));

	xc = GTK_WIDGET(dial)->allocation.width / 2;
	yc = GTK_WIDGET(dial)->allocation.height / 2;

	old_value = dial->adjustment->value;
	dial->angle = atan2(yc-y, x-xc);

	if (dial->angle < -M_PI/2.)
		dial->angle += 2*M_PI;

	if (dial->angle < min_angle)
		dial->angle = min_angle;

	if (dial->angle > max_angle)
		dial->angle = max_angle;

	min = dial->adjustment->lower;
	max = dial->adjustment->upper;

	dial->adjustment->value = min + 
		(max_angle - dial->angle) *
		(max - min ) / (max_angle - min_angle);

	if (dial->adjustment->value != old_value)
	{
		if (dial->policy == GTK_UPDATE_CONTINUOUS)
		{
			gtk_signal_emit_by_name (GTK_OBJECT (dial->adjustment), "value_changed");
		}
		else
		{
			gtk_widget_draw (GTK_WIDGET(dial), NULL);

			if (dial->policy == GTK_UPDATE_DELAYED)
			{
				if (dial->timer)
					gtk_timeout_remove (dial->timer);

				dial->timer = gtk_timeout_add (SCROLL_DELAY_LENGTH,
							       (GtkFunction) gf4d_angle_timer,
							       (gpointer) dial);
			}
		}
	}
}

static void
gf4d_angle_update (Gf4dAngle *dial)
{
	gfloat new_value;
  
	g_return_if_fail (dial != NULL);
	g_return_if_fail (GF4D_IS_ANGLE (dial));

	new_value = dial->adjustment->value;
  
	if (new_value < dial->adjustment->lower)
		new_value = dial->adjustment->lower;

	if (new_value > dial->adjustment->upper)
		new_value = dial->adjustment->upper;

	if (new_value != dial->adjustment->value)
	{
		dial->adjustment->value = new_value;
		gtk_signal_emit_by_name (GTK_OBJECT (dial->adjustment), "value_changed");
	}

	dial->angle = max_angle - (new_value - dial->adjustment->lower) * (max_angle - min_angle) /
		(dial->adjustment->upper - dial->adjustment->lower);

	gtk_widget_draw (GTK_WIDGET(dial), NULL);
}

static void
gf4d_angle_adjustment_changed (GtkAdjustment *adjustment,
			       gpointer       data)
{
	Gf4dAngle *dial;

	g_return_if_fail (adjustment != NULL);
	g_return_if_fail (data != NULL);

	dial = GF4D_ANGLE (data);

	if ((dial->old_value != adjustment->value) ||
	    (dial->old_lower != adjustment->lower) ||
	    (dial->old_upper != adjustment->upper))
	{
		gf4d_angle_update (dial);

		dial->old_value = adjustment->value;
		dial->old_lower = adjustment->lower;
		dial->old_upper = adjustment->upper;
	}
}

static void
gf4d_angle_adjustment_value_changed (GtkAdjustment *adjustment,
				     gpointer       data)
{
	Gf4dAngle *dial;

	g_return_if_fail (adjustment != NULL);
	g_return_if_fail (data != NULL);

	dial = GF4D_ANGLE (data);

	if (dial->old_value != adjustment->value)
	{
		gf4d_angle_update (dial);

		dial->old_value = adjustment->value;
	}
}
/* example-end */
