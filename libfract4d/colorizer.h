/* Gnofract4D -- a fractal generator-browser program
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

#ifndef _COLORIZER_H_
#define _COLORIZER_H_

#include "colorizer_public.h"

#include <iosfwd>
#include <string>

colorizer_t *
colorizer_read(std::istream& s);

// abstract base class
class colorizer {
 public:
    virtual ~colorizer() {};

    virtual colorizer *clone() const = 0;

    virtual e_colorizer type(void) const = 0;
    virtual rgb_t calc(double dist) const = 0;
    virtual bool operator==(const colorizer&) const = 0;

    virtual std::ostream& put(std::ostream&) const = 0;
    virtual std::istream& get(std::istream&) = 0;
};

std::ostream& operator<<(std::ostream& s, const colorizer& cizer);
std::istream& operator>>(std::istream& s, colorizer& cizer);

// draws fract based on variations of a single {r,g,b} color
class rgb_colorizer : public colorizer{
 public: 
    double r, g, b;
	
 private:
    static const double contrast;
    double cr, cg, cb;
 public:
    rgb_colorizer(void);
    rgb_colorizer(const rgb_colorizer&);
    ~rgb_colorizer();

    colorizer* clone() const { return new rgb_colorizer(*this); }

    e_colorizer type() const;
    rgb_t calc(double dist) const;
    bool operator==(const colorizer&) const;

    friend std::ostream& operator<<(std::ostream&, const rgb_colorizer&);
    friend std::istream& operator>>(std::istream&, rgb_colorizer&);
	std::ostream& put(std::ostream& s) const { return s << *this; };
	std::istream& get(std::istream& s) { return s >> *this; };

    // not shared with colorizer
    void set_colors(double _r, double _g, double _b);
};

class cmap_colorizer : public colorizer {
 public:
    static const int size;
 public:
    rgb_t *cmap;
    std::string name;

    cmap_colorizer();
    ~cmap_colorizer();
    cmap_colorizer(const cmap_colorizer&);
    cmap_colorizer& operator=(const cmap_colorizer&);
    bool operator==(const colorizer& c) const;

    colorizer* clone() const { return new cmap_colorizer(*this); }

    e_colorizer type() const;
    rgb_t calc(double dist) const;

    friend std::ostream& operator<<(std::ostream&, const cmap_colorizer&);
    friend std::istream& operator>>(std::istream&, cmap_colorizer&);
	std::ostream& put(std::ostream& s) const { return s << *this; };
	std::istream& get(std::istream& s) { return s >> *this; };
	
    // not shared with colorizer
    // FIXME: should return a status indication or throw
    void set_cmap_file(const char *filename);
    std::string encode_color_data(void) const;
    void decode_color_data(const std::string& data);

};

#endif /*_COLORIZER_H_*/
