/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

/* Thread Pool routines originally pilfered from "Pthreads
   Programming", Nichols, Buttlar & Farrell, O'Reilly 

   I've minimally C++-ized them (added ctors etc), and converted from
   a linked list to to a templated array. This has the advantage that
   we don't need to call new() to introduce new work items.

*/

#ifndef _THREADPOOL_H_
#define _THREADPOOL_H_

#include "pthread.h"

template<class T>
struct tpool_work {
    void (*routine)(T&);
    T arg;
};

template<class T>
class tpool {
 public:
    tpool(int num_worker_threads_, int max_queue_size_)
        {
            num_threads = num_worker_threads_;
            max_queue_size = max_queue_size_;
            
            queue = new tpool_work<T>[max_queue_size];
            threads = new pthread_t[num_threads];
    
            cur_queue_size = 0;
            queue_head = 0;
            queue_tail = 0;
            queue_closed = 0;
            shutdown = 0;

            pthread_mutex_init(&queue_lock, NULL);
            pthread_cond_init(&queue_not_empty, NULL);
            pthread_cond_init(&queue_not_full, NULL);
            pthread_cond_init(&queue_empty, NULL);
            
            /* create low-priority attribute block */
            pthread_attr_t lowprio_attr;
            struct sched_param lowprio_param;
            pthread_attr_init(&lowprio_attr);
            lowprio_param.sched_priority = sched_get_priority_min(SCHED_OTHER);
            pthread_attr_setschedparam(&lowprio_attr, &lowprio_param);

            for(int i = 0; i < num_threads; ++i)
            {
                pthread_create(&threads[i], &lowprio_attr, 
                               (void *(*)(void *))&threadFunc, this);
            }
        }
    
    ~tpool()
        {
            pthread_mutex_lock(&queue_lock);
            queue_closed = 1;

            /* wait for the queue to empty */
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
            delete[] queue;
        }

    static void threadFunc(tpool *p)
        {
            try
                {
                    p->work();
                }
            catch(...)
                {
                    // do nothing - let this thread die peacefully
                }
        }

    int add_work(void (*routine)(T&), const T& arg)
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
            
            /* fill in work structure */
            tpool_work<T> *workp = &queue[queue_head];           
            
            workp->routine = routine;
            workp->arg = arg;

            /* advance queue head to next position */
            queue_head = (queue_head + 1) % max_queue_size;

            /* record keeping */
            cur_queue_size++;
            if(1 == cur_queue_size)
            {
                pthread_cond_signal(&queue_not_empty);
            }
            assert(cur_queue_size <= max_queue_size);
            
            pthread_mutex_unlock(&queue_lock);
            
            return 1;
        }

    void work()
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

            tpool_work<T> *my_workp = &queue[queue_tail];
            cur_queue_size--;
            assert(cur_queue_size >= 0);
            queue_tail = ( queue_tail + 1 ) % max_queue_size;

            if(cur_queue_size == max_queue_size - 1)
            {
                pthread_cond_broadcast(&queue_not_full);
            }

            if(0 == cur_queue_size)
            {
                pthread_cond_signal(&queue_empty);
            }

            void (*my_routine)(T&) = my_workp->routine;
            /* NOT a T& reference because otherwise data could be
               overwritten before we can process it */
            T my_arg = my_workp->arg;
            pthread_mutex_unlock(&queue_lock);

            try
                {
                    /* actually do the work */
                    ((*my_routine))(my_arg);
                }
            catch(...)
                {
                    /* abort this task, but don't do anything else - 
                       main thread will notice soon */
                }
        }
    }

    // block until all currently scheduled work is done
    void flush()
        {
            pthread_mutex_lock(&queue_lock);
            while(cur_queue_size != 0)
            {
                pthread_cond_wait(&queue_empty,&queue_lock);
            }
            pthread_mutex_unlock(&queue_lock);
        }

 private:

    /* pool characteristics */
    int num_threads;
    int max_queue_size;
    
    /* pool state */
    pthread_t *threads;
    int cur_queue_size;
    int queue_head;
    int queue_tail;
    tpool_work<T> *queue;
    pthread_mutex_t queue_lock;
    pthread_cond_t queue_not_empty;
    pthread_cond_t queue_not_full;
    pthread_cond_t queue_empty;

    int queue_closed;
    int shutdown;
};

#endif /* _THREADPOOL_H_ */
