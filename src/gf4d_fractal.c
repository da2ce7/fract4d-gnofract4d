#include <gtk/gtkmain.h>
#include <gtk/gtksignal.h>

#include "gf4d_fractal.h"
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
	f->f = fract_new();
	f->freeze_depth = 0;
	f->interrupted=FALSE;
	f->change_pending=FALSE;
	f->sensitive=TRUE;
}

GtkObject*
gf4d_fractal_new ()
{
	Gf4dFractal *f;

	f = gtk_type_new (gf4d_fractal_get_type ());

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
	parent_class = gtk_type_class(GTK_TYPE_OBJECT);

	fractal_signals[PARAMETERS_CHANGED] = 
		gtk_signal_new("parameters_changed",
			       GTK_RUN_FIRST | GTK_RUN_NO_RECURSE,
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
	fract_relocate(f->f,x,y,zoom);
}

void gf4d_fractal_flip2julia(Gf4dFractal *f, int x, int y)
{
	fract_flip2julia(f->f,x,y);
}

void gf4d_fractal_calc(Gf4dFractal *f)
{
	g_print("calculating\n");
	fract_calc(f->f, f);
}

void gf4d_fractal_reset(Gf4dFractal *f)
{
	fract_reset(f->f);
	gf4d_fractal_parameters_changed(f);
}

void gf4d_fractal_write_params(Gf4dFractal *f, FILE *fp)
{
	fract_write_params(f->f, fp);
}

void gf4d_fractal_load_params(Gf4dFractal *f, FILE *fp)
{
	fract_load_params(f->f,fp);
}

/* accessor functions */
int gf4d_fractal_get_max_iterations(Gf4dFractal *f)
{
	return fract_get_max_iterations(f->f);
}

double gf4d_fractal_get_r(Gf4dFractal *f)
{
	return fract_get_r(f->f);
}

double gf4d_fractal_get_g(Gf4dFractal *f)
{
	return fract_get_g(f->f);
}

double gf4d_fractal_get_b(Gf4dFractal *f)
{
	return fract_get_b(f->f);
}

int gf4d_fractal_get_aa(Gf4dFractal *f)
{
	return fract_get_aa(f->f);
}

int gf4d_fractal_get_auto(Gf4dFractal *f)
{
	return fract_get_auto(f->f);
}

char *gf4d_fractal_get_param(Gf4dFractal *f, param_t i)
{
	return fract_get_param(f->f,i);
}

/* update functions */
void gf4d_fractal_set_max_iterations(Gf4dFractal *f, int val)
{
	fract_set_max_iterations(f->f,val);
}

void gf4d_fractal_set_param(Gf4dFractal *f, param_t i, char *val)
{
	fract_set_param(f->f,i,val);
}

void gf4d_fractal_set_aa(Gf4dFractal *f, int val)
{
	fract_set_aa(f->f,val);
}

void gf4d_fractal_set_auto(Gf4dFractal *f, int val)
{
	fract_set_auto(f->f,val);
}

int gf4d_fractal_set_precision(Gf4dFractal *f, int digits)
{
	return fract_set_precision(f->f, digits);
}

void gf4d_fractal_set_color(Gf4dFractal *f, double r, double g, double b)
{
	fract_set_color(f->f,r,g,b);
}

/* image-related functions: to be removed */
int gf4d_fractal_get_xres(Gf4dFractal *f)
{
	return fract_get_xres(f->f);
}

int gf4d_fractal_get_yres(Gf4dFractal *f)
{
	return fract_get_yres(f->f);
}

char *gf4d_fractal_get_image(Gf4dFractal *f)
{
	return fract_get_tmp_img(f->f);
}

double gf4d_fractal_get_ratio(Gf4dFractal *f)
{
	return fract_get_ratio(f->f);
}

int  gf4d_fractal_set_resolution(Gf4dFractal *f, int xres, int yres)
{
	int ret = fract_set_resolution(f->f,xres,yres);
	gf4d_fractal_parameters_changed(f);
	return ret;
}

void gf4d_fractal_realloc_image(Gf4dFractal *f)
{
	fract_realloc_image(f->f);
}

void gf4d_fractal_delete_image(Gf4dFractal *f)
{
	fract_delete_image(f->f);
}

void gf4d_fractal_move(Gf4dFractal *f, int data)
{
	fract_move(f->f,data);
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
	fract_finish(f->f);
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
