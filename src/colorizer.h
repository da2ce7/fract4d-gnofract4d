#ifndef _COLORIZER_H_
#define _COLORIZER_H_

#include "colorizer_public.h"
#include "calc.h"
#include "pointFunc.h"

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
    virtual rgb_t operator()(int iter, double *scratch, bool potential) const = 0;
#ifdef HAVE_GMP
    virtual rgb_t operator()(int iter, gmp::f *scratch, bool potential) const = 0;
#endif
    virtual std::ostream& put(std::ostream&) const = 0;
    virtual std::istream& get(std::istream&) = 0;
    virtual bool operator==(const colorizer&) const = 0;
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
    rgb_t operator()(int iter, double *scratch, bool potential) const;
#ifdef HAVE_GMP
    rgb_t operator()(int iter, gmp::f *scratch, bool potential) const;
#endif
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
    rgb_t operator()(int iter, double *scratch, bool potential) const;
#ifdef HAVE_GMP
    rgb_t operator()(int iter, gmp::f *scratch, bool potential) const;
#endif
    friend std::ostream& operator<<(std::ostream&, const cmap_colorizer&);
    friend std::istream& operator>>(std::istream&, cmap_colorizer&);
	std::ostream& put(std::ostream& s) const { return s << *this; };
	std::istream& get(std::istream& s) { return s >> *this; };
	
    // not shared with colorizer
    // FIXME: should return a status indication or throw
    void set_cmap_file(const char *filename);
};

#endif _COLORIZER_H_
