#include "gf4d_movie.h"
#include "gf4d_fractal.h"

#include <gtk/gtkmain.h>
#include <gtk/gtksignal.h>
#include "gf4d_utils.h"

static void gf4d_movie_class_init               (Gf4dMovieClass    *klass);
static void gf4d_movie_init                     (Gf4dMovie         *dial);
static void gf4d_movie_destroy                  (GtkObject        *object);

enum {
    LIST_CHANGED,
    PROGRESS_CHANGED,
    STATUS_CHANGED,
    LAST_SIGNAL
};

static guint movie_signals[LAST_SIGNAL] = {0};

static GtkObjectClass *parent_class = NULL;

GtkType
gf4d_movie_get_type ()
{
    static guint movie_type = 0;

    if (!movie_type)
    {
        GtkTypeInfo movie_info =
        {
            "Gf4dMovie",
            sizeof (Gf4dMovie),
            sizeof (Gf4dMovieClass),
            (GtkClassInitFunc) gf4d_movie_class_init,
            (GtkObjectInitFunc) gf4d_movie_init,
            (GtkArgSetFunc) NULL,
            (GtkArgGetFunc) NULL,
            (GtkClassInitFunc) NULL
        };

        movie_type = gtk_type_unique (gtk_object_get_type (), &movie_info);
    }

    return movie_type;
}

static void
gf4d_movie_init (Gf4dMovie *f)
{
    f->keyframes = NULL;

    f->tid=0;
    f->workers_running=0;
    pthread_mutex_init(&f->lock,NULL);
    pthread_mutex_init(&f->cond_lock,NULL);
    pthread_cond_init(&f->running_cond,NULL);

    f->status = GF4D_MOVIE_DONE;
    f->output = NULL;
}

static void
gf4d_movie_cond_lock(Gf4dMovie *f)
{
    pthread_mutex_lock(&f->cond_lock);
}

static void
gf4d_movie_cond_unlock(Gf4dMovie *f)
{
    pthread_mutex_unlock(&f->cond_lock);
}

void 
gf4d_movie_set_output(Gf4dMovie *mov, Gf4dFractal *f)
{
    mov->output = f;
}

GtkObject*
gf4d_movie_new ()
{
    Gf4dMovie *f;

    f = GF4D_MOVIE(gtk_type_new (gf4d_movie_get_type ()));

    return GTK_OBJECT (f);
}

static void 
set_finished_cond(Gf4dMovie *mov)
{
    g_print("interrupt\n");
    mov->workers_running=0;
    gf4d_fractal_interrupt(mov->output);
}

static void
try_finished_cond(Gf4dMovie *f)
{
    // this doesn't do any locking, but is safe:
    // if we miss it this time, we'll catch it next
    // time, and won't do any harm in the meantime

    if(f->workers_running==0) 
    {
        g_print("finished in movie\n");
        // we've been signalled
        throw(1);
    }
}

static void
set_started_cond(Gf4dMovie *f)
{
    gf4d_movie_cond_lock(f);
    f->workers_running=1;
    pthread_cond_signal(&f->running_cond);
    gf4d_movie_cond_unlock(f);
}

static void
kill_slave_threads(Gf4dMovie *f)
{
    if(f->tid)
    {
        set_finished_cond(f);

        // wait until worker has stopped running
        // gdk_threads_leave();
        pthread_join(f->tid,NULL);
        //gdk_threads_enter();
    }

    f->tid = 0;
}

static void
gf4d_movie_destroy (GtkObject *object)
{
    Gf4dMovie *f;

    g_return_if_fail (object != NULL);
    g_return_if_fail (GF4D_IS_MOVIE (object));

    f = GF4D_MOVIE (object);

    kill_slave_threads(f);

    if (GTK_OBJECT_CLASS (parent_class)->destroy)
        (* GTK_OBJECT_CLASS (parent_class)->destroy) (object);
}

static void
gf4d_movie_class_init (Gf4dMovieClass *klass)
{
    GtkObjectClass *object_class;
    object_class = (GtkObjectClass *)klass;

    object_class->destroy = gf4d_movie_destroy;
    parent_class = (GtkObjectClass *)(gtk_type_class(GTK_TYPE_OBJECT));

    movie_signals[LIST_CHANGED] = 
        gtk_signal_new("list_changed",
                       GtkSignalRunType(GTK_RUN_FIRST | GTK_RUN_NO_RECURSE),
                       object_class->type,
                       GTK_SIGNAL_OFFSET(Gf4dMovieClass, list_changed),
                       gtk_marshal_NONE__NONE,
                       GTK_TYPE_NONE, 0);

    movie_signals[PROGRESS_CHANGED] = 
        gtk_signal_new("progress_changed",
                       GTK_RUN_FIRST,
                       object_class->type,
                       GTK_SIGNAL_OFFSET(Gf4dMovieClass, progress_changed),
                       marshal_NONE__FLOAT,
                       GTK_TYPE_NONE, 1,
                       GTK_TYPE_FLOAT);

    movie_signals[STATUS_CHANGED] = 
        gtk_signal_new("status_changed",
                       GTK_RUN_FIRST,
                       object_class->type,
                       GTK_SIGNAL_OFFSET(Gf4dMovieClass, status_changed),
                       gtk_marshal_NONE__ENUM,
                       GTK_TYPE_NONE, 1,
                       GTK_TYPE_ENUM);

    /* default signal handlers don't do anything */
    klass->list_changed=NULL;
    klass->progress_changed=NULL;
    klass->status_changed=NULL;
	
    gtk_object_class_add_signals(object_class, movie_signals, LAST_SIGNAL);
}


void await_slave_start(Gf4dMovie *f)
{
    gf4d_movie_cond_lock(f);
    while(f->workers_running==0)
    {
        pthread_cond_wait(&f->running_cond,&f->cond_lock);
    }
    gf4d_movie_cond_unlock(f);
}


/* stop calculating now! */
void gf4d_movie_interrupt(Gf4dMovie *f)
{
    kill_slave_threads(f);
}

void 
gf4d_movie_list_changed(Gf4dMovie *f)
{
    gtk_signal_emit(GTK_OBJECT(f), movie_signals[LIST_CHANGED]); 
}

static void
gf4d_movie_enter_callback(Gf4dMovie *f)
{
    try_finished_cond(f);
    gdk_threads_enter();
    g_print("movie on %x owns lock\n", pthread_self());
}

static void
gf4d_movie_leave_callback(Gf4dMovie *f)
{
    g_print("movie on %x freeing lock\n",pthread_self());
    gdk_threads_leave();
}

void gf4d_movie_progress_changed(Gf4dMovie *f, float progress)
{
    gf4d_movie_enter_callback(f);

    gtk_signal_emit(GTK_OBJECT(f),
                    movie_signals[PROGRESS_CHANGED], 
                    progress);
    gf4d_movie_leave_callback(f);
}

void gf4d_movie_status_changed(Gf4dMovie *f, int status_val)
{
    f->status = status_val;
    gf4d_movie_enter_callback(f);

    gtk_signal_emit(GTK_OBJECT(f),
                    movie_signals[STATUS_CHANGED],
                    status_val);
    gf4d_movie_leave_callback(f);
}

static void *
calculation_thread(void *vdata) 
{
    Gf4dMovie *mov = (Gf4dMovie *)vdata;

    set_started_cond(mov);

    int nFrames = g_list_length(mov->keyframes) - 1;
    int key =0;

    try {

        GList *keyframes = mov->keyframes;

        if(!keyframes)
        {
            // warn;
            return NULL;
        }
    
        Gf4dFractal *last_fractal = GF4D_FRACTAL(keyframes->data);
        keyframes = keyframes->next;

        while(keyframes)
        {
            Gf4dFractal *current_fractal = GF4D_FRACTAL(keyframes->data);

            for(int i = 0; i < 10; ++i)
            {
                double pos = (10.0 - i)/9.0;

                gf4d_fractal_set_mixed(
                    mov->output,last_fractal,current_fractal, pos);

                gf4d_fractal_calc(mov->output, 0);
                
                try_finished_cond(mov);
                float progress = (key * 10.0 + i +1)/(nFrames * 10.0);

                gf4d_movie_progress_changed(mov,progress);
            }
            last_fractal = current_fractal;
            keyframes = keyframes->next;
            key++;
        }
        gf4d_movie_progress_changed(mov,0.0);
    }
    catch(...)
    {
        
    }

    return NULL;
}

void gf4d_movie_calc(Gf4dMovie *f, int nThreads)
{
    kill_slave_threads(f);

    if(pthread_create(&f->tid,NULL,calculation_thread,(void *)f))
    {
        g_warning("Error, couldn't start thread\n");
        return;
    }
	
    // check that it really has started (and set workers) before returning
    await_slave_start(f);
}

void gf4d_movie_add(Gf4dMovie *mov, Gf4dFractal *f, Gf4dFractal *f_after)
{
    Gf4dFractal *fcopy = gf4d_fractal_copy(f);
    kill_slave_threads(mov);

    int i=0;
    if(f_after)
    {
        GList *after_list = mov->keyframes;
        while(after_list && after_list->data != f_after)
        {
            i++;
            after_list = after_list->next;
        }
        mov->keyframes = g_list_insert(mov->keyframes, fcopy, i+1);
    }
    else
    {
        mov->keyframes = g_list_append(mov->keyframes, fcopy);
    }

    gf4d_movie_list_changed(mov);
}

void gf4d_movie_remove(Gf4dMovie *mov, Gf4dFractal *f)
{
    GList *list = mov->keyframes;

    g_print("trying to remove %x\n",f);
    while(list)
    {
        if(list->data == f)
        {
            g_print("found %x\n",f);
            mov->keyframes = g_list_remove_link(mov->keyframes,list);
            gf4d_movie_list_changed(mov);
            break;
        }
        list = list->next;
    }
}







