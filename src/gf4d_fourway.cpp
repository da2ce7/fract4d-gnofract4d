/* GTK - The GIMP Toolkit
 * Copyright (C) 1999-2001 Edwin Young
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

#include "gf4d_fourway.h"

#define FOURWAY_DEFAULT_SIZE 32

/* Forward declarations */

static void gf4d_fourway_class_init               (Gf4dFourwayClass    *klass);
static void gf4d_fourway_init                     (Gf4dFourway         *fourway);
static void gf4d_fourway_destroy                  (GtkObject        *object);
static void gf4d_fourway_realize                  (GtkWidget        *widget);
static void gf4d_fourway_size_request             (GtkWidget      *widget,
						 GtkRequisition *requisition);
static void gf4d_fourway_size_allocate            (GtkWidget     *widget,
						 GtkAllocation *allocation);
static gint gf4d_fourway_expose                   (GtkWidget        *widget,
						 GdkEventExpose   *event);
static gint gf4d_fourway_button_press             (GtkWidget        *widget,
						 GdkEventButton   *event);
static gint gf4d_fourway_button_release           (GtkWidget        *widget,
						 GdkEventButton   *event);
static gint gf4d_fourway_motion_notify            (GtkWidget        *widget,
						 GdkEventMotion   *event);
static void gf4d_fourway_update_mouse             (Gf4dFourway *fourway, gint x, gint y);
static void gf4d_fourway_update                   (Gf4dFourway *fourway);
static void gf4d_fourway_adjustment_changed       (GtkAdjustment    *adjustment,
						 gpointer          data);
static void gf4d_fourway_adjustment_value_changed (GtkAdjustment    *adjustment,
						 gpointer          data);

/* Local data */
enum {
    VALUE_SLIGHTLY_CHANGED,
    VALUE_CHANGED,
    LAST_SIGNAL
};

static guint fourway_signals[LAST_SIGNAL] = {0};

static GtkWidgetClass *parent_klass = NULL;

guint
gf4d_fourway_get_type ()
{
    static guint fourway_type = 0;

    if (!fourway_type)
    {
        GtkTypeInfo fourway_info =
        {
            "Gf4dFourway",
            sizeof (Gf4dFourway),
            sizeof (Gf4dFourwayClass),
            (GtkClassInitFunc) gf4d_fourway_class_init,
            (GtkObjectInitFunc) gf4d_fourway_init,
            (GtkArgSetFunc) NULL,
            (GtkArgGetFunc) NULL,
        };

        fourway_type = gtk_type_unique (gtk_widget_get_type (), &fourway_info);
    }

    return fourway_type;
}

static void
gf4d_fourway_class_init (Gf4dFourwayClass *klass)
{
    GtkObjectClass *object_klass;
    GtkWidgetClass *widget_klass;

    object_klass = (GtkObjectClass*) klass;
    widget_klass = (GtkWidgetClass*) klass;

    parent_klass = GTK_WIDGET_CLASS(gtk_type_class (gtk_widget_get_type ()));

    object_klass->destroy = gf4d_fourway_destroy;

    widget_klass->realize = gf4d_fourway_realize;
    widget_klass->expose_event = gf4d_fourway_expose;
    widget_klass->size_request = gf4d_fourway_size_request;
    widget_klass->size_allocate = gf4d_fourway_size_allocate;
    widget_klass->button_press_event = gf4d_fourway_button_press;
    widget_klass->button_release_event = gf4d_fourway_button_release;
    widget_klass->motion_notify_event = gf4d_fourway_motion_notify;

    fourway_signals[VALUE_SLIGHTLY_CHANGED] = 
        gtk_signal_new("value_slightly_changed",
                       GtkSignalRunType(GTK_RUN_FIRST | GTK_RUN_NO_RECURSE),
                       object_klass->type,
                       GTK_SIGNAL_OFFSET(Gf4dFourwayClass, value_slightly_changed),
                       gtk_marshal_NONE__INT_INT,
                       GTK_TYPE_NONE, 2,
                       GTK_TYPE_INT,
                       GTK_TYPE_INT);

    fourway_signals[VALUE_CHANGED] = 
        gtk_signal_new("value_changed",
                       GtkSignalRunType(GTK_RUN_FIRST | GTK_RUN_NO_RECURSE),
                       object_klass->type,
                       GTK_SIGNAL_OFFSET(Gf4dFourwayClass, value_changed),
                       gtk_marshal_NONE__INT_INT,
                       GTK_TYPE_NONE, 2,
                       GTK_TYPE_INT,
                       GTK_TYPE_INT);
    
    klass->value_slightly_changed = NULL;
    klass->value_changed = NULL;

    gtk_object_class_add_signals(object_klass, fourway_signals, LAST_SIGNAL);

}

static void
gf4d_fourway_init (Gf4dFourway *fourway)
{
    fourway->button = 0;
    fourway->radius = 0;
    fourway->last_x = 0;
    fourway->last_y = 0;
    fourway->text=NULL;
}

GtkWidget*
gf4d_fourway_new (const gchar *label)
{
    Gf4dFourway *fourway;

    fourway = GF4D_FOURWAY(gtk_type_new (gf4d_fourway_get_type ()));

    fourway->text = g_strdup(label);

    return GTK_WIDGET (fourway);
}

static void
gf4d_fourway_destroy (GtkObject *object)
{
    Gf4dFourway *fourway;

    g_return_if_fail (object != NULL);
    g_return_if_fail (GF4D_IS_FOURWAY (object));

    fourway = GF4D_FOURWAY (object);

    if (GTK_OBJECT_CLASS (parent_klass)->destroy)
        (* GTK_OBJECT_CLASS (parent_klass)->destroy) (object);
}

static void
gf4d_fourway_realize (GtkWidget *widget)
{
    Gf4dFourway *fourway;
    GdkWindowAttr attributes;
    gint attributes_mask;

    g_return_if_fail (widget != NULL);
    g_return_if_fail (GF4D_IS_FOURWAY (widget));

    GTK_WIDGET_SET_FLAGS (widget, GTK_REALIZED);
    fourway = GF4D_FOURWAY (widget);

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
gf4d_fourway_size_request (GtkWidget      *widget,
			 GtkRequisition *requisition)
{
    requisition->width = FOURWAY_DEFAULT_SIZE;
    requisition->height = FOURWAY_DEFAULT_SIZE;
}

static void
gf4d_fourway_size_allocate (GtkWidget     *widget,
			  GtkAllocation *allocation)
{
    Gf4dFourway *fourway;

    g_return_if_fail (widget != NULL);
    g_return_if_fail (GF4D_IS_FOURWAY (widget));
    g_return_if_fail (allocation != NULL);

    widget->allocation = *allocation;
    fourway = GF4D_FOURWAY (widget);

    if (GTK_WIDGET_REALIZED (widget))
    {
        gdk_window_move_resize (widget->window,
                                allocation->x, allocation->y,
                                allocation->width, allocation->height);

    }
    fourway->radius = (gint)(MIN(allocation->width,allocation->height) * 0.5);

    fourway->last_x = widget->allocation.width/2;
    fourway->last_y = widget->allocation.height/2;
}

static gint
gf4d_fourway_expose (GtkWidget      *widget,
		   GdkEventExpose *event)
{
    Gf4dFourway *fourway;
    gdouble s,c;
    gint xc, yc;

    g_return_val_if_fail (widget != NULL, FALSE);
    g_return_val_if_fail (GF4D_IS_FOURWAY (widget), FALSE);
    g_return_val_if_fail (event != NULL, FALSE);

    if (event->count > 0)
        return FALSE;
  
    fourway = GF4D_FOURWAY (widget);

    gdk_window_clear_area (widget->window,
                           0, 0,
                           widget->allocation.width,
                           widget->allocation.height);

    xc = widget->allocation.width/2;
    yc = widget->allocation.height/2;

    /* Draw text (rather badly - should perhaps use label widget) */
    if(fourway->text)
    {
        gint l = gdk_string_width(widget->style->font,fourway->text);
        gint h = gdk_string_height(widget->style->font, fourway->text);
		
        gtk_draw_string(widget->style,
                        widget->window,
                        GTK_STATE_NORMAL,
                        xc - l/2,
                        yc,
                        fourway->text);
    }

    /* Draw square */
    gdk_draw_rectangle(widget->window,
                       widget->style->fg_gc[widget->state],
                       FALSE,
                       xc-fourway->radius,
                       yc-fourway->radius,
                       fourway->radius*2-2,
                       fourway->radius*2-2);

    /* draw arrows */
    GdkPoint arrPoints[3];
    
    /* pointing left */
    arrPoints[0].x = xc-fourway->radius+1; arrPoints[0].y = yc;
    arrPoints[1].x = xc-fourway->radius+7; arrPoints[1].y = yc - 5;
    arrPoints[2].x = xc-fourway->radius+7; arrPoints[2].y = yc + 5;

    gdk_draw_polygon(widget->window,
                     widget->style->fg_gc[widget->state],
                     TRUE,
                     arrPoints,
                     3);

    /* pointing right */
    arrPoints[0].x = xc+fourway->radius-2; arrPoints[0].y = yc;
    arrPoints[1].x = xc+fourway->radius-7; arrPoints[1].y = yc - 5;
    arrPoints[2].x = xc+fourway->radius-7; arrPoints[2].y = yc + 5;

    gdk_draw_polygon(widget->window,
                     widget->style->fg_gc[widget->state],
                     TRUE,
                     arrPoints,
                     3);

    /* pointing up */
    arrPoints[0].x = xc;     arrPoints[0].y = yc - fourway->radius + 1;
    arrPoints[1].x = xc - 5; arrPoints[1].y = yc - fourway->radius + 7; 
    arrPoints[2].x = xc + 5; arrPoints[2].y = yc - fourway->radius + 7;

    gdk_draw_polygon(widget->window,
                     widget->style->fg_gc[widget->state],
                     TRUE,
                     arrPoints,
                     3);

    /* pointing down */
    arrPoints[0].x = xc;     arrPoints[0].y = yc + fourway->radius - 2;
    arrPoints[1].x = xc - 5; arrPoints[1].y = yc + fourway->radius - 7; 
    arrPoints[2].x = xc + 5; arrPoints[2].y = yc + fourway->radius - 7;

    gdk_draw_polygon(widget->window,
                     widget->style->fg_gc[widget->state],
                     TRUE,
                     arrPoints,
                     3);

    return FALSE;
}

static gint
gf4d_fourway_button_press (GtkWidget      *widget,
			 GdkEventButton *event)
{
    Gf4dFourway *fourway;

    g_return_val_if_fail (widget != NULL, FALSE);
    g_return_val_if_fail (GF4D_IS_FOURWAY (widget), FALSE);
    g_return_val_if_fail (event != NULL, FALSE);

    fourway = GF4D_FOURWAY (widget);
  
    if (!fourway->button)
    {
        gtk_grab_add (widget);
        fourway->button = event->button;

        fourway->last_x = widget->allocation.width/2;
        fourway->last_y = widget->allocation.height/2;

        gf4d_fourway_update_mouse (fourway, (gint)event->x, (gint)event->y);
    }

    return FALSE;
}

static gint
gf4d_fourway_button_release (GtkWidget      *widget,
                             GdkEventButton *event)
{
    Gf4dFourway *fourway;

    g_return_val_if_fail (widget != NULL, FALSE);
    g_return_val_if_fail (GF4D_IS_FOURWAY (widget), FALSE);
    g_return_val_if_fail (event != NULL, FALSE);

    fourway = GF4D_FOURWAY (widget);

    if (fourway->button == event->button)
    {
        gtk_grab_remove (widget);

        fourway->button = 0;

        GtkAllocation *pAllocation = &(GTK_WIDGET(fourway)->allocation);
        
        gint xc = pAllocation->width / 2;
        gint yc = pAllocation->height / 2;

        gint dx = xc - fourway->last_x;
        gint dy = yc - fourway->last_y;
        if (dx || dy)
        {
            gtk_signal_emit(GTK_OBJECT (fourway), 
                            fourway_signals[VALUE_CHANGED],
                            dx,
                            dy);
        }
    }

    return FALSE;
}

static gint
gf4d_fourway_motion_notify (GtkWidget      *widget,
			  GdkEventMotion *event)
{
    Gf4dFourway *fourway;
    GdkModifierType mods;
    gint x, y, mask;

    g_return_val_if_fail (widget != NULL, FALSE);
    g_return_val_if_fail (GF4D_IS_FOURWAY (widget), FALSE);
    g_return_val_if_fail (event != NULL, FALSE);

    fourway = GF4D_FOURWAY (widget);

    if (fourway->button != 0)
    {
        x = (gint)event->x;
        y = (gint)event->y;

        if (event->is_hint || (event->window != widget->window))
            gdk_window_get_pointer (widget->window, &x, &y, &mods);

        switch (fourway->button)
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
            gf4d_fourway_update_mouse (fourway, x,y);
    }

    return FALSE;
}

static void
gf4d_fourway_update_mouse (Gf4dFourway *fourway, gint x, gint y)
{
    g_return_if_fail (fourway != NULL);
    g_return_if_fail (GF4D_IS_FOURWAY (fourway));

    gint dx = fourway->last_x - x;
    gint dy = fourway->last_y - y;

    g_print("%d,%d\n", dx, dy);

    if (dx || dy)
    {
        gtk_signal_emit (GTK_OBJECT (fourway), 
                         fourway_signals[VALUE_SLIGHTLY_CHANGED],
                         dx,
                         dy); 

        fourway->last_x = x;
        fourway->last_y = y;
    }
}

