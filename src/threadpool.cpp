
#include "threadpool.h"

void tpool_thread(tpool *p)
{
    p->work();
}

tpool::tpool(int num_worker_threads_, int max_queue_size_)
{
    num_threads = num_worker_threads_;
    max_queue_size = max_queue_size_;

    threads = new pthread_t[num_threads];
    
    cur_queue_size = 0;
    queue_head = NULL;
    queue_tail = NULL;
    queue_closed = 0;
    shutdown = 0;

    pthread_mutex_init(&queue_lock, NULL);
    pthread_cond_init(&queue_not_empty, NULL);
    pthread_cond_init(&queue_not_full, NULL);
    pthread_cond_init(&queue_empty, NULL);

    for(int i = 0; i < num_threads; ++i)
    {
        pthread_create(&threads[i], NULL, 
                       (void *(*)(void *))tpool_thread, this);
    }
}

tpool::~tpool()
{
    pthread_mutex_lock(&queue_lock);
    queue_closed = 1;
    while(cur_queue_size != 0)
    {
        pthread_cond_wait(&queue_empty,&queue_lock);
    }

    shutdown = 1;
    
    pthread_mutex_unlock(&queue_lock);

    /* wake up any sleeping workers */
    pthread_cond_broadcast(&queue_not_empty);
    pthread_cond_broadcast(&queue_not_full);
        
    for(int i = 0; i < num_threads; ++i)
    {
        pthread_join(threads[i],NULL);
    }

    delete[] threads;
    while(queue_head != NULL)
    {
        tpool_work_t *nodep = queue_head->next;
        queue_head = queue_head->next;
        delete nodep;
    }
}

int
tpool::add_work(void (*routine)(void *), void *arg)
{
    pthread_mutex_lock(&queue_lock);
    
    while((cur_queue_size == max_queue_size) &&
          (!(shutdown || queue_closed)))
    {
        pthread_cond_wait(&queue_not_full, &queue_lock);
    }

    if(shutdown || queue_closed) 
    {
        pthread_mutex_unlock(&queue_lock);
        return 0;
    }

    /* allocate work structure */
    tpool_work_t *workp = new tpool_work_t;

    workp->routine = routine;
    workp->arg = arg;
    workp->next = NULL;
    if(0 == cur_queue_size)
    {
        queue_tail = queue_head = workp;
        pthread_cond_signal(&queue_not_empty);
    }
    else
    {
        queue_tail->next = workp;
        queue_tail = workp;
    }
    cur_queue_size++;

    pthread_mutex_unlock(&queue_lock);

    return 1;
}

void
tpool::flush()
{
    pthread_mutex_lock(&queue_lock);
    while(cur_queue_size != 0)
    {
        pthread_cond_wait(&queue_empty,&queue_lock);
    }
    pthread_mutex_unlock(&queue_lock);
}

void
tpool::work()
{
    while(1)
    {
        pthread_mutex_lock(&queue_lock);
        while( cur_queue_size == 0 && !(shutdown))
        {
            pthread_cond_wait(&queue_not_empty,&queue_lock);
        }
        
        if(shutdown)
        {
            pthread_mutex_unlock(&queue_lock);
            pthread_exit(NULL);
        }

        tpool_work_t *my_workp = queue_head;
        cur_queue_size--;
        if(0 == cur_queue_size)
        {
            queue_head = queue_tail = NULL;
        }
        else
        {
            queue_head = my_workp->next;
        }

        if(cur_queue_size == max_queue_size - 1)
        {
            pthread_cond_broadcast(&queue_not_full);
        }

        if(0 == cur_queue_size)
        {
            pthread_cond_signal(&queue_empty);
        }

        pthread_mutex_unlock(&queue_lock);

        try
        {
            /* actually do the work */
            ((*my_workp->routine))(my_workp->arg);
        }
        catch(...)
        {
            /* abort this task, but don't do anything else - 
               main thread will notice soon */
        }
        delete my_workp;
    }
}

