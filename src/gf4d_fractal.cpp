#include <gtk/gtkmain.h>
#include <gtk/gtksignal.h>

#include "gf4d_fractal.h"
#include "image.h"
#include "fract.h"

static void gf4d_fractal_class_init               (Gf4dFractalClass    *klass);
static void gf4d_fractal_init                     (Gf4dFractal         *dial);
static void gf4d_fractal_destroy                  (GtkObject        *object);

enum {
	PARAMETERS_CHANGED,
	IMAGE_CHANGED,
	PROGRESS_CHANGED,
	STATUS_CHANGED,
	LAST_SIGNAL
};

static guint fractal_signals[LAST_SIGNAL] = {0};

static GtkObjectClass *parent_class = NULL;

/* local prototypes */
void marshal_NONE__FLOAT(GtkObject*    object,
			 GtkSignalFunc func,
			 gpointer      func_data,
			 GtkArg*       args);

GtkType
gf4d_fractal_get_type ()
{
	static guint fractal_type = 0;

	if (!fractal_type)
	{
		GtkTypeInfo fractal_info =
		{
			"Gf4dFractal",
			sizeof (Gf4dFractal),
			sizeof (Gf4dFractalClass),
			(GtkClassInitFunc) gf4d_fractal_class_init,
			(GtkObjectInitFunc) gf4d_fractal_init,
			(GtkArgSetFunc) NULL,
			(GtkArgGetFunc) NULL,
			(GtkClassInitFunc) NULL
		};

		fractal_type = gtk_type_unique (gtk_object_get_type (), &fractal_info);
	}

	return fractal_type;
}

static void
gf4d_fractal_init (Gf4dFractal *f)
{
	f->f = new fractal();
	f->im = new image();

	f->freeze_depth = 0;
	f->interrupted=FALSE;
	f->change_pending=FALSE;
	f->sensitive=TRUE;
}

GtkObject*
gf4d_fractal_new ()
{
	Gf4dFractal *f;

	f = GF4D_FRACTAL(gtk_type_new (gf4d_fractal_get_type ()));

	return GTK_OBJECT (f);
}

static void
gf4d_fractal_destroy (GtkObject *object)
{
	Gf4dFractal *f;

	g_return_if_fail (object != NULL);
	g_return_if_fail (GF4D_IS_FRACTAL (object));

	f = GF4D_FRACTAL (object);

	if (GTK_OBJECT_CLASS (parent_class)->destroy)
		(* GTK_OBJECT_CLASS (parent_class)->destroy) (object);
}

typedef int (*GtkSignal_NONE__FLOAT)(GtkObject* object, gfloat, gpointer user_data);

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

static void
gf4d_fractal_class_init (Gf4dFractalClass *klass)
{
	GtkObjectClass *object_class;
	object_class = (GtkObjectClass *)klass;

	object_class->destroy = gf4d_fractal_destroy;
	parent_class = (GtkObjectClass *)(gtk_type_class(GTK_TYPE_OBJECT));

	fractal_signals[PARAMETERS_CHANGED] = 
		gtk_signal_new("parameters_changed",
			       GtkSignalRunType(GTK_RUN_FIRST | GTK_RUN_NO_RECURSE),
			       object_class->type,
			       GTK_SIGNAL_OFFSET(Gf4dFractalClass, parameters_changed),
			       gtk_marshal_NONE__NONE,
			       GTK_TYPE_NONE, 0);

	fractal_signals[IMAGE_CHANGED] = 
		gtk_signal_new("image_changed",
			       GTK_RUN_FIRST,
			       object_class->type,
			       GTK_SIGNAL_OFFSET(Gf4dFractalClass, image_changed),
			       gtk_marshal_NONE__POINTER,
			       GTK_TYPE_NONE, 1,
			       GTK_TYPE_GDK_EVENT);

	fractal_signals[PROGRESS_CHANGED] = 
		gtk_signal_new("progress_changed",
			       GTK_RUN_FIRST,
			       object_class->type,
			       GTK_SIGNAL_OFFSET(Gf4dFractalClass, progress_changed),
			       marshal_NONE__FLOAT,
			       GTK_TYPE_NONE, 1,
			       GTK_TYPE_FLOAT);

	fractal_signals[STATUS_CHANGED] = 
		gtk_signal_new("status_changed",
			       GTK_RUN_FIRST,
			       object_class->type,
			       GTK_SIGNAL_OFFSET(Gf4dFractalClass, status_changed),
			       gtk_marshal_NONE__ENUM,
			       GTK_TYPE_NONE, 1,
			       GTK_TYPE_ENUM);

	/* default signal handlers don't do anything */
	klass->parameters_changed=NULL;
	klass->image_changed=NULL;
	klass->progress_changed=NULL;
	klass->status_changed=NULL;
	
	gtk_object_class_add_signals(object_class, fractal_signals, LAST_SIGNAL);
}

void gf4d_fractal_relocate(Gf4dFractal *f, int x, int y, double zoom)
{
	double dx = ((double)(x - f->im->Xres/2))/f->im->Xres;
	double dy = ((double)(y - f->im->Yres/2))/f->im->Xres;
	f->f->relocate(dx,dy,zoom);
}

void gf4d_fractal_flip2julia(Gf4dFractal *f, int x, int y)
{
	double dx = ((double)(x - f->im->Xres/2))/f->im->Xres;
	double dy = ((double)(y - f->im->Yres/2))/f->im->Xres;
	f->f->flip2julia(dx,dy);
}

void gf4d_fractal_calc(Gf4dFractal *f)
{
	g_print("calculating\n");
	f->f->calc(f,f->im);
}

void gf4d_fractal_reset(Gf4dFractal *f)
{
	f->f->reset();
	gf4d_fractal_parameters_changed(f);
}

gboolean gf4d_fractal_write_params(Gf4dFractal *f, const char *filename)
{
	return (gboolean)f->f->write_params(filename);
}

gboolean gf4d_fractal_load_params(Gf4dFractal *f, const gchar *filename)
{
	return f->f->load_params(filename);
}

/* accessor functions */
int gf4d_fractal_get_max_iterations(Gf4dFractal *f)
{
	return f->f->get_max_iterations();
}

double gf4d_fractal_get_r(Gf4dFractal *f)
{
	return f->f->get_r();
}

double gf4d_fractal_get_g(Gf4dFractal *f)
{
	return f->f->get_g();
}

double gf4d_fractal_get_b(Gf4dFractal *f)
{
	return f->f->get_b();
}

int gf4d_fractal_get_aa(Gf4dFractal *f)
{
	return f->f->get_aa();
}

int gf4d_fractal_get_auto(Gf4dFractal *f)
{
	return f->f->get_auto();
}

char *gf4d_fractal_get_param(Gf4dFractal *f, param_t i)
{
	return f->f->get_param(i);
}

/* update functions */
void gf4d_fractal_set_max_iterations(Gf4dFractal *f, int val)
{
	f->f->set_max_iterations(val);
}

void gf4d_fractal_set_param(Gf4dFractal *f, param_t i, char *val)
{
	f->f->set_param(i,val);
}

void gf4d_fractal_set_aa(Gf4dFractal *f, int val)
{
	f->f->set_aa(val);
}

void gf4d_fractal_set_auto(Gf4dFractal *f, int val)
{
	f->f->set_auto(val);
}

int gf4d_fractal_set_precision(Gf4dFractal *f, int digits)
{
	return f->f->set_precision(digits);
}

void gf4d_fractal_set_color(Gf4dFractal *f, double r, double g, double b)
{
	fract_set_color(f->f,r,g,b);
}

/* image-related functions: to be removed */
int gf4d_fractal_get_xres(Gf4dFractal *f)
{
	return f->im->Xres;
}

int gf4d_fractal_get_yres(Gf4dFractal *f)
{
	return f->im->Yres;
}

char *gf4d_fractal_get_image(Gf4dFractal *f)
{
	return f->im->buffer;
}

double gf4d_fractal_get_ratio(Gf4dFractal *f)
{
	return f->im->ratio();
}

int  gf4d_fractal_set_resolution(Gf4dFractal *f, int xres, int yres)
{
	int ret = f->im->set_resolution(xres,yres);
	gf4d_fractal_parameters_changed(f);
	return ret;
}

void gf4d_fractal_freeze(Gf4dFractal *f)
{

}

void gf4d_fractal_thaw(Gf4dFractal *f)
{

}

/* stop calculating now! */
void gf4d_fractal_interrupt(Gf4dFractal *f)
{
	f->f->finish();
}

void gf4d_fractal_parameters_changed(Gf4dFractal *f)
{
	g_print("parameters changed: emit\n");
	gtk_signal_emit(GTK_OBJECT(f), fractal_signals[PARAMETERS_CHANGED]); 
}

void gf4d_fractal_image_changed(Gf4dFractal *f, int x1, int y1, int x2, int y2)
{
	GdkEventExpose fakeEvent;
	GdkRectangle rect;

	rect.x = x1;
	rect.y = y1;
	rect.width = x2 - x1;
	rect.height = y2 - y1;
	fakeEvent.type = GDK_EXPOSE;
	fakeEvent.window = NULL;
	fakeEvent.send_event = TRUE;
	fakeEvent.area = rect;
	fakeEvent.count = 0;

	gtk_signal_emit(GTK_OBJECT(f), 
			fractal_signals[IMAGE_CHANGED],
			&fakeEvent);
}

void gf4d_fractal_progress_changed(Gf4dFractal *f, float progress)
{
	gtk_signal_emit(GTK_OBJECT(f),
			fractal_signals[PROGRESS_CHANGED], 
			progress);
}

void gf4d_fractal_status_changed(Gf4dFractal *f, int status_val)
{
	gtk_signal_emit(GTK_OBJECT(f),
			fractal_signals[STATUS_CHANGED],
			status_val);
}

int gf4d_fractal_is_interrupted(Gf4dFractal *f)
{
	return f->interrupted;
}
