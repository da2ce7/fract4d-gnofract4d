/* Thread Pool routines shamelessly pilfered from "Pthreads
   Programming", Nichols, Buttlar & Farrell, O'Reilly 

   I've minimally C++-ized them (added ctors etc)

*/

#include "pthread.h"

typedef struct tpool_work {
    void (*routine)(void *);
    void *arg;
    struct tpool_work *next;
} tpool_work_t;

class tpool {
 public:
    tpool(int num_worker_threads, int max_queue_size);
    ~tpool();
    int add_work(void (*routine)(void *), void *arg);
    void work();

 private:
    worker();
    /* pool characteristics */
    int num_threads;
    int max_queue_size;
    
    /* pool state */
    pthread_t *threads;
    int cur_queue_size;
    tpool_work_t *queue_head;
    tpool_work_t *queue_tail;
    pthread_mutex_t queue_lock;
    pthread_cond_t queue_not_empty;
    pthread_cond_t queue_not_full;
    pthread_cond_t queue_empty;

    int queue_closed;
    int shutdown;
};



