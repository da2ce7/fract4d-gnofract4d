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

#ifndef _COLORIZER_PUBLIC_H_
#define _COLORIZER_PUBLIC_H_

typedef class colorizer colorizer_t;
typedef struct rgb rgb_t;

struct rgb
{
    unsigned char r;
    unsigned char g;
    unsigned char b;
};

typedef enum {
    COLORIZER_RGB,
    COLORIZER_CMAP
} e_colorizer;

#ifdef __cplusplus
extern "C" {
#endif


colorizer_t *colorizer_new(e_colorizer);
void colorizer_delete(colorizer_t **);

#ifdef __cplusplus
}
#endif

#endif /* _COLORIZER_PUBLIC_H_ */
