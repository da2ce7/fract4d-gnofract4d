
#ifndef _GF4D_UTILS_H_
#define _GF4D_UTILS_H_

#include <gtk/gtkobject.h>
#include <gtk/gtkmarshal.h>

typedef int (*GtkSignal_NONE__FLOAT)(GtkObject* object, gfloat, gpointer user_data);

/* local prototypes */
void marshal_NONE__FLOAT(GtkObject*    object,
			 GtkSignalFunc func,
			 gpointer      func_data,
			 GtkArg*       args);

#endif /* _GF4D_UTILS_H_ */
