/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2001 Edwin Young
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

#include "tls.h"
#include <gdk/gdk.h>

#include <stdio.h>

static pthread_key_t gdk_key;

/* call this once at start of program */
void tls_init(void)
{
    pthread_key_create(&gdk_key, NULL);
}

/* this thread is not a GUI thread */
void tls_set_not_gtk_thread(void)
{
    /* doesn't matter what we point to, so long as it's not NULL -
       it's the *presence* of the key, not its value, which we're
       interested in */
    pthread_setspecific(gdk_key, (void *)&gdk_key);
}

/* is this thread a GUI thread? */
bool tls_is_gtk_thread(void)
{
    void *key = pthread_getspecific(gdk_key);
 
    /* if no such key, we are a GTK thread */
    return key == NULL;
}

void tls_join_thread(pthread_t tid)
{
    if(tls_is_gtk_thread())
    {
        gdk_threads_leave();
    }

    printf("joining thread %d\n",tid);
    pthread_join(tid,NULL);
    
    if(tls_is_gtk_thread())
    {
        gdk_threads_enter();
    }
}



