#include "gf4d_utils.h"

void marshal_NONE__FLOAT(GtkObject*    object,
			 GtkSignalFunc func,
			 gpointer      func_data,
			 GtkArg*       args)
{
    GtkSignal_NONE__FLOAT rfunc;
    rfunc = (GtkSignal_NONE__FLOAT)func;
    (*rfunc)(object,
             GTK_VALUE_FLOAT(args[0]),
             func_data);
}

