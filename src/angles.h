
#ifndef _ANGLES_H_
#define _ANGLES_H_

#include <gnome.h>
#include <gtk/gtk.h>

#include "model.h"

GtkWidget* create_angle_button(
    char *label_text, 
    param_t data, 
    model_t *m, 
    GtkWidget *appbar,
    Gf4dFractal *preview);

#endif
