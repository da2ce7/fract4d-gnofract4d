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
	virtual rgb_t operator()(int iter) const = 0;
	virtual ostream& put(ostream& s) const = 0;
	virtual istream& get(istream& s) = 0;
	virtual e_colorizer type(void) const = 0;
};

std::ostream& operator<<(std::ostream& s, const colorizer& cizer);
std::istream& operator>>(std::istream& s, colorizer& cizer);

// draws fract based on variations of a single {r,g,b} color
class rgb_colorizer : public colorizer{
 public: 
	double r, g, b;
	
 private:
	static const double contrast = 3.0;
	double cr, cg, cb;
 public:
	e_colorizer type() const;
	rgb_colorizer(void);
	rgb_t operator()(int iter) const;
	friend ostream& operator<<(ostream&, const rgb_colorizer&);
	friend istream& operator>>(istream&, rgb_colorizer&);
	ostream& put(ostream& s) const { return s << *this; };
	istream& get(istream& s) { return s >> *this; };

	// not shared with colorizer
	void set_colors(double _r, double _g, double _b);
};

class cmap_colorizer : public colorizer {
 public:
	rgb_t *cmap;
	std::string name;

	e_colorizer type() const;
	cmap_colorizer(void);
	~cmap_colorizer(void);
	rgb_t operator()(int iter) const;
	friend ostream& operator<<(ostream&, const cmap_colorizer&);
	friend istream& operator>>(istream&, cmap_colorizer&);
	ostream& put(ostream& s) const { return s << *this; };
	istream& get(istream& s) { return s >> *this; };

	// not shared with colorizer
	void set_cmap_file(const char *filename);
};

#endif _COLORIZER_H_
