#include "gf4d_fractal.h"
#include "image.h"
#include "fract.h"
#include <gtk/gtkmain.h>
#include <gtk/gtksignal.h>
#include "gf4d_utils.h"
#include "tls.h"

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
            NULL,
            NULL,
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

    f->tid=0;
    f->workers_running=0;
    pthread_mutex_init(&f->lock,NULL);
    pthread_mutex_init(&f->cond_lock,NULL);
    pthread_mutex_init(&f->pause_lock,NULL);
    pthread_cond_init(&f->running_cond,NULL);
    f->status = GF4D_FRACTAL_DONE;
    f->paused = FALSE;
    f->fOnGTKThread = TRUE;
}

GtkObject*
gf4d_fractal_new ()
{
    Gf4dFractal *f;

    f = GF4D_FRACTAL(gtk_type_new (gf4d_fractal_get_type ()));

    return GTK_OBJECT (f);
}

static void
gf4d_fractal_cond_lock(Gf4dFractal *f)
{
    pthread_mutex_lock(&f->cond_lock);
}

static void
gf4d_fractal_cond_unlock(Gf4dFractal *f)
{
    pthread_mutex_unlock(&f->cond_lock);
}

static void 
set_finished_cond(Gf4dFractal *f)
{
    f->workers_running=0;
    printf("set_finished_cond\n");
}

bool
gf4d_fractal_try_finished_cond(Gf4dFractal *f)
{
    // this doesn't do any locking, but is safe:
    // if we miss it this time, we'll catch it next
    // time, and won't do any harm in the meantime

    if(f->workers_running==0) 
    {
        // we've been signalled
        return true;
    }
    return false;
}

static void
try_paused_cond(Gf4dFractal *f)
{
    // if we've been paused, we'll end up waiting here until 
    // the main thread releases the mutex again
    pthread_mutex_lock(&f->pause_lock);

    pthread_mutex_unlock(&f->pause_lock);
}

static void
set_started_cond(Gf4dFractal *f)
{
    gf4d_fractal_cond_lock(f);
    f->workers_running=1;
    pthread_cond_signal(&f->running_cond);
    gf4d_fractal_cond_unlock(f);
}

static void await_slave_death(Gf4dFractal *f)
{
    // wait until worker has stopped running
    tls_join_thread(f->tid);
}

static void
kill_slave_threads(Gf4dFractal *f)
{
    gboolean wasPaused = gf4d_fractal_pause(f, FALSE);
    if(f->tid)
    {
        set_finished_cond(f);

        await_slave_death(f);
    }

    /* if we changed some parameters while paused, the user
       presumably wants to change some more before explicitly
       starting the calculation */
    if(wasPaused)
    {
        f->paused = TRUE;
    }
    f->tid = 0;
}

static void
gf4d_fractal_destroy (GtkObject *object)
{
    Gf4dFractal *f;

    g_return_if_fail (object != NULL);
    g_return_if_fail (GF4D_IS_FRACTAL (object));

    f = GF4D_FRACTAL (object);

    kill_slave_threads(f);

    if (GTK_OBJECT_CLASS (parent_class)->destroy)
        (* GTK_OBJECT_CLASS (parent_class)->destroy) (object);
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
    kill_slave_threads(f);

    double dx = ((double)(x - f->im->Xres()/2))/f->im->Xres();
    double dy = ((double)(y - f->im->Yres()/2))/f->im->Xres();
    f->f->relocate(dx,dy,zoom);
}

void gf4d_fractal_flip2julia(Gf4dFractal *f, int x, int y)
{
    kill_slave_threads(f);

    double dx = ((double)(x - f->im->Xres()/2))/f->im->Xres();
    double dy = ((double)(y - f->im->Yres()/2))/f->im->Xres();
    f->f->flip2julia(dx,dy);
}

void gf4d_fractal_move(Gf4dFractal *f, param_t i, double direction)
{
    kill_slave_threads(f);

    f->f->move(i,direction);
}

fractal_t *gf4d_fractal_copy_fract(Gf4dFractal *f)
{
    kill_slave_threads(f);
    return new fractal(*f->f);
}

void gf4d_fractal_set_fract(Gf4dFractal *gf, fractal_t * f)
{
    kill_slave_threads(gf);
    *(gf->f) = *f;
}

void gf4d_fractal_update_fract(Gf4dFractal *gf, Gf4dFractal *gf2)
{
    kill_slave_threads(gf);
    *(gf->f) = *(gf2->f);
}

void gf4d_fractal_set_bailout_type(Gf4dFractal *gf, e_bailFunc bailType)
{
    kill_slave_threads(gf);
    gf->f->bailout_type = bailType;
}

e_bailFunc gf4d_fractal_get_bailout_type(Gf4dFractal *gf)
{
    return gf->f->bailout_type;
}

static void *
calculation_thread(void *vdata) 
{
    Gf4dFractal *f = (Gf4dFractal *)vdata;

    set_started_cond(f);

    try {
        f->f->calc(f,f->im);	
    }
    catch(...)
    {
        
    }

    return NULL;
}

void gf4d_fractal_calc(Gf4dFractal *f, int nThreads, e_antialias effective_aa)
{
    kill_slave_threads(f);

    /* if we're paused, lock the pause mutex before starting the 
       calculation thread
    */
    if(f->paused)
    {
        gf4d_fractal_pause(f,TRUE);
    }

    f->f->eaa = effective_aa;
    f->f->nThreads = nThreads;

    if(nThreads)
    {
        /* calculate asynchronously in another thread */
        if(pthread_create(&f->tid,NULL,calculation_thread,(void *)f))
        {
            g_warning("Error, couldn't start thread\n");
            return;
        }
	
        // check that it really has started (and set workers) before returning
        gf4d_fractal_cond_lock(f);
        while(f->workers_running==0)
        {
            pthread_cond_wait(&f->running_cond,&f->cond_lock);
        }
        gf4d_fractal_cond_unlock(f);
    }
    else
    {
        /* blocking calculation in current thread */
        calculation_thread((void *)f);
    }
}

void gf4d_fractal_recolor(Gf4dFractal *f)
{
    kill_slave_threads(f);
    f->f->recolor(f->im);
}

void gf4d_fractal_reset(Gf4dFractal *f)
{
    kill_slave_threads(f);
    f->f->reset();
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

e_antialias gf4d_fractal_get_aa(Gf4dFractal *f)
{
    return f->f->get_aa();
}

gboolean gf4d_fractal_get_auto(Gf4dFractal *f)
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
    kill_slave_threads(f);

    f->f->set_max_iterations(val);
}

void gf4d_fractal_set_param(Gf4dFractal *f, param_t i, char *val)
{
    kill_slave_threads(f);

    f->f->set_param(i,val);
}

void gf4d_fractal_set_aa(Gf4dFractal *f, e_antialias val)
{
    kill_slave_threads(f);

    f->f->set_aa(val);
}

void gf4d_fractal_set_auto(Gf4dFractal *f, gboolean val)
{
    kill_slave_threads(f);

    f->f->set_auto(val);
}

int gf4d_fractal_set_precision(Gf4dFractal *f, int digits)
{
    kill_slave_threads(f);

    return f->f->set_precision(digits);
}

/* image-related functions: to be removed */
int gf4d_fractal_get_xres(Gf4dFractal *f)
{
    return f->im->Xres();
}

int gf4d_fractal_get_yres(Gf4dFractal *f)
{
    return f->im->Yres();
}

guchar *gf4d_fractal_get_image(Gf4dFractal *f)
{
    return (guchar *)f->im->getBuffer();
}

double gf4d_fractal_get_ratio(Gf4dFractal *f)
{
    return f->im->ratio();
}

int  gf4d_fractal_set_resolution(Gf4dFractal *f, int xres, int yres)
{
    kill_slave_threads(f);
    f->im->set_resolution(xres,yres);
    return 1;
}

colorizer_t *gf4d_fractal_get_colorizer(Gf4dFractal *f)
{
    return f->f->get_colorizer();
}

void gf4d_fractal_set_colorizer(Gf4dFractal *f, colorizer_t *cizer)
{
    kill_slave_threads(f);
    f->f->set_colorizer(cizer);
}

/* stop calculating now! */
void gf4d_fractal_interrupt(Gf4dFractal *f)
{
    kill_slave_threads(f);
}

/* returns previous pause status */
gboolean gf4d_fractal_pause(Gf4dFractal *f, gboolean pause)
{
    gboolean previous_pause_state = f->paused;
    if(pause)
    {
        gtk_signal_emit(
            GTK_OBJECT(f), 
            fractal_signals[STATUS_CHANGED],
            GF4D_FRACTAL_PAUSED);

        pthread_mutex_lock(&f->pause_lock);
        f->paused = TRUE;
    }
    else
    {
        if(previous_pause_state)
        {
            // restore previous status
            gtk_signal_emit(
                GTK_OBJECT(f),
                fractal_signals[STATUS_CHANGED],
                f->status);
            pthread_mutex_unlock(&f->pause_lock);
            f->paused = FALSE;
        }
    }
    return previous_pause_state;
}

void 
gf4d_fractal_parameters_changed(Gf4dFractal *f)
{
    gtk_signal_emit(GTK_OBJECT(f), fractal_signals[PARAMETERS_CHANGED]); 
}

gboolean gf4d_fractal_is_equal(Gf4dFractal *f, Gf4dFractal *f2)
{
    return (gboolean)(*(f->f) == *(f2->f));
}

static void
gf4d_fractal_enter_callback(Gf4dFractal *f)
{
    try_paused_cond(f);
    gdk_threads_enter();
}

static void
gf4d_fractal_leave_callback(Gf4dFractal *f)
{
    gdk_threads_leave();    
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

    gf4d_fractal_enter_callback(f);

    gtk_signal_emit(GTK_OBJECT(f), 
                    fractal_signals[IMAGE_CHANGED],
                    &fakeEvent);
    gf4d_fractal_leave_callback(f);
}

void gf4d_fractal_progress_changed(Gf4dFractal *f, float progress)
{
    gf4d_fractal_enter_callback(f);

    gtk_signal_emit(GTK_OBJECT(f),
                    fractal_signals[PROGRESS_CHANGED], 
                    progress);
    gf4d_fractal_leave_callback(f);
}

void gf4d_fractal_status_changed(Gf4dFractal *f, int status_val)
{
    f->status = status_val;
    gf4d_fractal_enter_callback(f);

    gtk_signal_emit(GTK_OBJECT(f),
                    fractal_signals[STATUS_CHANGED],
                    status_val);
    gf4d_fractal_leave_callback(f);
}

Gf4dFractal *gf4d_fractal_copy(Gf4dFractal *f)
{
    /* not a full copy : doesn't get image buffer */
    Gf4dFractal *fnew = GF4D_FRACTAL(gf4d_fractal_new());
    fnew->f = new fractal(*(f->f));
	
    fnew->im = new image();
    /*
    fnew->im->Xres = f->im->Xres;
    fnew->im->Yres = f->im->Yres;
    */
    return fnew;
}

gboolean gf4d_fractal_get_potential(Gf4dFractal *f)
{
    return f->f->get_potential();
}

void gf4d_fractal_set_potential(Gf4dFractal *f, gboolean potential)
{
    kill_slave_threads(f);
    f->f->set_potential(potential);
}

void gf4d_fractal_set_mixed(
    Gf4dFractal *f_dst, 
    Gf4dFractal *f_src1, 
    Gf4dFractal *f_src2, 
    double lambda)
{
    kill_slave_threads(f_dst);
    f_dst->f->set_mixed(*f_src1->f, *f_src2->f, lambda);
}

void gf4d_fractal_set_inexact(Gf4dFractal *gf_dst, Gf4dFractal *gf_src, double weirdness)
{
    kill_slave_threads(gf_dst);
    gf_dst->f->set_inexact(*gf_src->f,weirdness);
}

iterFunc *gf4d_fractal_get_func(Gf4dFractal *f)
{
    return f->f->pIterFunc;
}

void gf4d_fractal_set_func(Gf4dFractal *f, const char *type)
{
    kill_slave_threads(f);
    f->f->set_fractal_type(type);
}

void gf4d_fractal_set_on_gui_thread(Gf4dFractal *f, gboolean fOnThread)
{
    f->fOnGTKThread = fOnThread;
}

gboolean gf4d_fractal_is_on_gui_thread(Gf4dFractal *f)
{
    return f->fOnGTKThread;
}
