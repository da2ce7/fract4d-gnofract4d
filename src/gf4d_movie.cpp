#include "gf4d_movie.h"
#include "gf4d_fractal.h"

#include <gtk/gtkmain.h>
#include <gtk/gtksignal.h>
#include "gf4d_utils.h"
#include "tls.h"

static void gf4d_movie_class_init               (Gf4dMovieClass    *klass);
static void gf4d_movie_init                     (Gf4dMovie         *dial);
static void gf4d_movie_destroy                  (GtkObject        *object);

enum {
    LIST_CHANGED,
    PROGRESS_CHANGED,
    IMAGE_COMPLETE,
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
            NULL,
            NULL,
            (GtkClassInitFunc) NULL
        };

        movie_type = gtk_type_unique (gtk_object_get_type (), &movie_info);
    }

    return movie_type;
}

static void
gf4d_movie_init (Gf4dMovie *mov)
{
    mov->keyframes = NULL;

    mov->tid=0;
    mov->workers_running=0;
    pthread_mutex_init(&mov->lock,NULL);
    pthread_mutex_init(&mov->cond_lock,NULL);
    pthread_cond_init(&mov->running_cond,NULL);

    mov->status = GF4D_MOVIE_DONE;
    mov->output = NULL;
}

static void
gf4d_movie_cond_lock(Gf4dMovie *mov)
{
    pthread_mutex_lock(&mov->cond_lock);
}

static void
gf4d_movie_cond_unlock(Gf4dMovie *mov)
{
    pthread_mutex_unlock(&mov->cond_lock);
}

void 
gf4d_movie_set_output(Gf4dMovie *mov, Gf4dFractal *f)
{
    mov->output = f;
}

GtkObject*
gf4d_movie_new ()
{
    Gf4dMovie *mov;

    mov = GF4D_MOVIE(gtk_type_new (gf4d_movie_get_type ()));

    return GTK_OBJECT (mov);
}

static void 
set_finished_cond(Gf4dMovie *mov)
{
    mov->workers_running=0;
    gf4d_fractal_interrupt(mov->output);
}

static bool
try_finished_cond(Gf4dMovie *mov)
{
    // this doesn't do any locking, but is safe:
    // if we miss it this time, we'll catch it next
    // time, and won't do any harm in the meantime

    if(mov->workers_running==0) 
    {
        return true;
    }
    return false;
}

gboolean gf4d_movie_is_calculating(Gf4dMovie *mov)
{
    return !try_finished_cond(mov);
}

static void
set_started_cond(Gf4dMovie *mov)
{
    gf4d_movie_cond_lock(mov);
    mov->workers_running=1;
    pthread_cond_signal(&mov->running_cond);
    gf4d_movie_cond_unlock(mov);
}

static void
kill_slave_threads(Gf4dMovie *mov)
{
    if(mov->tid)
    {
        set_finished_cond(mov);

        // wait until worker has stopped running
        tls_join_thread(mov->tid);
    }

    mov->tid = 0;
}

static void
gf4d_movie_destroy (GtkObject *object)
{
    Gf4dMovie *mov;

    g_return_if_fail (object != NULL);
    g_return_if_fail (GF4D_IS_MOVIE (object));

    mov = GF4D_MOVIE (object);

    kill_slave_threads(mov);

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

    movie_signals[IMAGE_COMPLETE] =
	gtk_signal_new("image_complete",
		       GTK_RUN_FIRST,
		       object_class->type,
		       GTK_SIGNAL_OFFSET(Gf4dMovieClass, image_complete),
		       marshal_NONE__INT,
		       GTK_TYPE_NONE, 1,
		       GTK_TYPE_INT);

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
    klass->image_complete=NULL;

    gtk_object_class_add_signals(object_class, movie_signals, LAST_SIGNAL);
}


void await_slave_start(Gf4dMovie *mov)
{
    gf4d_movie_cond_lock(mov);
    while(mov->workers_running==0)
    {
        pthread_cond_wait(&mov->running_cond,&mov->cond_lock);
    }
    gf4d_movie_cond_unlock(mov);
}


/* stop calculating now! */
void gf4d_movie_interrupt(Gf4dMovie *mov)
{
    kill_slave_threads(mov);
}

void 
gf4d_movie_list_changed(Gf4dMovie *mov)
{
    gtk_signal_emit(GTK_OBJECT(mov), movie_signals[LIST_CHANGED]); 
}

static void
gf4d_movie_enter_callback(Gf4dMovie *mov)
{
    gdk_threads_enter();
}

static void
gf4d_movie_leave_callback(Gf4dMovie *mov)
{
    gdk_threads_leave();
}

void gf4d_movie_progress_changed(Gf4dMovie *mov, float progress)
{
    gf4d_movie_enter_callback(mov);

    gtk_signal_emit(GTK_OBJECT(mov),
                    movie_signals[PROGRESS_CHANGED], 
                    progress);
    gf4d_movie_leave_callback(mov);
}

void gf4d_movie_status_changed(Gf4dMovie *mov, int status_val)
{
    mov->status = status_val;
    gf4d_movie_enter_callback(mov);

    gtk_signal_emit(GTK_OBJECT(mov),
                    movie_signals[STATUS_CHANGED],
                    status_val);
    gf4d_movie_leave_callback(mov);
}

void gf4d_movie_image_complete(Gf4dMovie *mov, int frame)
{
    gf4d_movie_enter_callback(mov);

    gtk_signal_emit(GTK_OBJECT(mov),
                    movie_signals[IMAGE_COMPLETE],
                    frame);
    gf4d_movie_leave_callback(mov);
}

static void *
calculation_thread(void *vdata) 
{
    Gf4dMovie *mov = (Gf4dMovie *)vdata;

    tls_set_not_gtk_thread();

    set_started_cond(mov);

    int nKeyFrames = g_list_length(mov->keyframes) - 1;
    int key =0;

    GList *keyframes = mov->keyframes;

    if(!keyframes)
    {
        // warn;
        return NULL;
    }
    
    gf4d_movie_status_changed(mov,GF4D_MOVIE_CALCULATING);

    Gf4dMovieFrame *last_frame = (Gf4dMovieFrame *)(keyframes->data);
    Gf4dFractal *last_fractal = GF4D_FRACTAL(last_frame->f);
    keyframes = keyframes->next;

    while(keyframes)
    {
        Gf4dMovieFrame *current_frame = (Gf4dMovieFrame *)(keyframes->data);
        Gf4dFractal *current_fractal = GF4D_FRACTAL(current_frame->f);

        int nFrames = 10;

        double factor = 1.0;
        if(!keyframes->next)
        {
            /* sections up to the last one include the 1st endpoint,
               but not the last one. The last section includes both */
            factor = (double)nFrames/(nFrames - 1);
        }
        for(int i = 0; i < nFrames; ++i)
        {
            // all sections:
            // when i = 0, pos = 1.0
            // most sections: 
            // when i = nFrames-1, pos = 1.0 -(nFrames-1)/nFrames
            // last section:
            // when i = nFrames-1, pos = 0.0

            double pos = (nFrames - i * factor)/nFrames;

            gf4d_fractal_set_mixed(
                mov->output,last_fractal,current_fractal, pos);

            gf4d_fractal_set_auto(mov->output, FALSE);
            gf4d_fractal_calc(mov->output, 0);

	    gf4d_movie_image_complete(mov,key*10+i);

            if(try_finished_cond(mov))
            {
                break;
            }
            float progress = (key * nFrames + i +1)/(nKeyFrames * nFrames);

            gf4d_movie_progress_changed(mov,progress);
        }
        last_fractal = current_fractal;
        keyframes = keyframes->next;
        key++;
    }
    gf4d_movie_progress_changed(mov,0.0);

    gf4d_movie_status_changed(mov,GF4D_MOVIE_DONE);

    return NULL;
}

void gf4d_movie_calc(Gf4dMovie *mov, int nThreads)
{
    kill_slave_threads(mov);

    if(pthread_create(&mov->tid,NULL,calculation_thread,(void *)mov))
    {
        g_warning("Error, couldn't start thread\n");
        return;
    }
	
    // check that it really has started (and set workers) before returning
    await_slave_start(mov);
}

void gf4d_movie_add(Gf4dMovie *mov, 
                    Gf4dMovieFrame *fr, 
                    Gf4dMovieFrame *fr_after)
{
    kill_slave_threads(mov);

    int i=0;
    if(fr_after)
    {
        GList *after_list = mov->keyframes;
        while(after_list && after_list->data != fr_after)
        {
            i++;
            after_list = after_list->next;
        }
        mov->keyframes = g_list_insert(mov->keyframes, fr, i+1);
    }
    else
    {
        mov->keyframes = g_list_append(mov->keyframes, fr);
    }

    gf4d_movie_list_changed(mov);
}

void gf4d_movie_remove(Gf4dMovie *mov, Gf4dMovieFrame *fr)
{
    GList *list = mov->keyframes;

    g_print("trying to remove %p\n",fr);
    while(list)
    {
        if(list->data == fr)
        {
            g_print("found %p\n",fr);
            mov->keyframes = g_list_remove_link(mov->keyframes,list);
            gf4d_movie_list_changed(mov);
            break;
        }
        list = list->next;
    }
}

Gf4dMovieFrame *gf4d_movie_frame_new(Gf4dFractal *f, int nFrames)
{
    Gf4dMovieFrame *fr = new Gf4dMovieFrame;
    fr->f = gf4d_fractal_copy(f);
    fr->nFrames = nFrames;

    return fr;
}

void gf4d_movie_frame_set_frames(Gf4dMovieFrame *fr, int nFrames)
{
    fr->nFrames = nFrames;
}
