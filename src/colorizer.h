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
    virtual rgb_t operator()(int iter, scratch_space scratch, bool potential) const = 0;

    virtual ostream& put(ostream&) const = 0;
    virtual istream& get(istream&) = 0;
    virtual bool operator==(const colorizer&) const = 0;
};

std::ostream& operator<<(std::ostream& s, const colorizer& cizer);
std::istream& operator>>(std::istream& s, colorizer& cizer);

// draws fract based on variations of a single {r,g,b} color
class rgb_colorizer : public colorizer{
 public: 
    double r, g, b;
	
 private:
    static const double contrast = 10.0;
    double cr, cg, cb;
 public:
    rgb_colorizer(void);
    rgb_colorizer(const rgb_colorizer&);
    ~rgb_colorizer();

    colorizer* clone() const { return new rgb_colorizer(*this); }

    e_colorizer type() const;
    rgb_t operator()(int iter, scratch_space scratch, bool potential) const;
    bool operator==(const colorizer&) const;

    friend ostream& operator<<(ostream&, const rgb_colorizer&);
    friend istream& operator>>(istream&, rgb_colorizer&);
    ostream& put(ostream& s) const { return s << *this; };
    istream& get(istream& s) { return s >> *this; };


    // not shared with colorizer
    void set_colors(double _r, double _g, double _b);
};

class cmap_colorizer : public colorizer {
 public:
    static const int size = 256;
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
    rgb_t operator()(int iter, scratch_space scratch, bool potential) const;
    friend ostream& operator<<(ostream&, const cmap_colorizer&);
    friend istream& operator>>(istream&, cmap_colorizer&);
    ostream& put(ostream& s) const { return s << *this; };
    istream& get(istream& s) { return s >> *this; };
	
    // not shared with colorizer
    void set_cmap_file(const char *filename);
};

#endif _COLORIZER_H_
