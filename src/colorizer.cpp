#include "colorizer.h"

#include <cstdlib>
#include <string>
#include <fstream>
#include <strstream>

/* factory functions */
colorizer_t *
colorizer_new(e_colorizer type)
{
	switch(type) {
	case COLORIZER_RGB:
		return new rgb_colorizer();
	case COLORIZER_CMAP:
		return new cmap_colorizer();
	default:
		return NULL;
	}
}

colorizer_t *
colorizer_read(std::istream& is)
{
	colorizer *cizer;
	std::string type;

	is >> type;

	// construct different colorizer type based on stream contents
	if(type == "colorizer=RGB")
	{
		cizer = colorizer_new(COLORIZER_RGB);
	}
	else if(type == "colorizer=CMAP") 
	{
		cizer = colorizer_new(COLORIZER_CMAP);
	}
	else
	{
		return NULL;
	}
	is >> *cizer;
	return cizer;
}

void
colorizer_delete(colorizer_t ** pcizer)
{
	delete *pcizer;
	*pcizer=NULL;
}

/* output needs to be virtual on *2nd* parameter. this function
 * forwards it (cf Stroustrup p613) 
 */

std::ostream& 
operator<<(std::ostream& s, const colorizer& cizer)
{
	return cizer.put(s);
}

std::istream&
operator>>(std::istream& s, colorizer& cizer)
{
	return cizer.get(s);
}

/* RGB subtype */

e_colorizer
rgb_colorizer::type() const
{
	return COLORIZER_RGB;
}

rgb_colorizer::rgb_colorizer()
{
	set_colors(1.0,0.0,0.0);
}

void
rgb_colorizer::set_colors(double _r, double _g, double _b)
{
	r = _r; g = _g; b = _b;
	/* cr et al are optimizations so operator() doesn't have to do so much */
	cr = 1.0 + contrast * r;
	cg = 1.0 + contrast * g;
	cb = 1.0 + contrast * b;
}

rgb_t
rgb_colorizer::operator()(int n) const
{
	struct rgb pixel={0,0,0};

	if (n != -1){
		double dn = (double)n;
		pixel.r = (char)(dn * cr);
		pixel.g = (char)(dn * cg);
		pixel.b = (char)(dn * cb);
	}
	return pixel;
}


std::ostream& 
operator<<(std::ostream& s, const rgb_colorizer& cizer)
{
	s << "colorizer=RGB\n" <<
		cizer.r << "\n" << 
		cizer.g << "\n" <<
		cizer.b << "\n";

	return s;
}

std::istream&
operator>>(std::istream& is, rgb_colorizer& cizer)
{
	
	is >> cizer.r;
	is >> cizer.g;
	is >> cizer.b;
	return is;
}

/* Color map subtype */

cmap_colorizer::cmap_colorizer()
{
	/* build default cmap: same effect as default color */
	const int size = 256;
	cmap = new rgb_t[size];

	for(int i =0; i < size; i++)
	{
		cmap[i].r = i;
		cmap[i].g = i;
		cmap[i].b = 4*i;		
	}
	name = "Default";
}

cmap_colorizer::~cmap_colorizer()
{
	delete[] cmap;
}

e_colorizer
cmap_colorizer::type() const 
{
	return COLORIZER_CMAP;
}

rgb_t
cmap_colorizer::operator()(int n) const
{
	return cmap[n % 256];
}

std::ostream& 
operator<<(std::ostream& s, const cmap_colorizer& cizer)
{
	s << "colorizer=CMAP\n" <<
		cizer.name << "\n";

	return s;
}

void
cmap_colorizer::set_cmap_file(const char *filename)
{
	std::ifstream cmapfile(filename);
	
	if(!cmapfile) return;
	
	name = filename;

	for(int i = 0; i < 256; i++)
	{
		// the "line at a time" approach is used rather than
		// the standard "is >>" because there may be junk at the
		// end of lines
		std::string line;
		getline(cmapfile,line);
		
		// use old class 'cos g++ *still* doesn't have <sstream>
		std::istrstream ss(line.c_str());

                // the 'val' int is so that the val is read as an int,
		// rather than a char
		int val;
		ss >> val; cmap[i].r = val; 
		ss >> val; cmap[i].g = val;
		ss >> val; cmap[i].b = val;		
	}
}

std::istream&
operator>>(std::istream& is, cmap_colorizer& cizer)
{
	std::string s;
	is >> s;

	cizer.set_cmap_file(s.c_str());
	return is;
}
