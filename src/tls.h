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

#ifndef _TLS_H_
#define _TLS_H_

/* GDK has a lock which has to be owned in order to do GUI stuff.
 * When we kill a slave thread we need to yield this lock before
 * waiting for it, but ONLY IF WE OWN THE LOCK. Sasly there's no way
 * of telling inside GDK/GTK (that I know of). So threads which aren't
 * part of the GUI call this fn to set a thread-specific (aka Thread
 * Local State) variable indicating that we needn't free the lock
 * before waiting for other threads.
 */

#include <pthread.h>

/* call this once at start of program */
void tls_init(void);

/* this thread is not a GUI thread */
void tls_set_not_gtk_thread(void); 

/* is this thread a GUI thread? */
bool tls_is_gtk_thread(void);

/* wait for thread with tid, yielding GUI lock if necessary */
void tls_join_thread(pthread_t tid);

#endif /* _TLS_H_ */
