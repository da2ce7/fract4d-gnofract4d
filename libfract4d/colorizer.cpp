#include "colorizer.h"
#include "iterFunc.h"
#include "io.h"

#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include <sstream>
#include <cassert>
#include <cmath>

#define FIELD_COLORIZER "colorizer"
#define FIELD_COLORDATA "colordata"

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
    colorizer *cizer = NULL;

    std::string name, value;

    while(is)
    {
        read_field(is,name,value);

        std::istringstream vs(value.c_str());

        if(FIELD_COLORIZER == name)
        {
            e_colorizer ctype;
            vs >> (int &)ctype;
            cizer = colorizer_new(ctype);
            if(cizer)
            {
                is >> *cizer;
            }
            break;
        }
    }
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
const double rgb_colorizer::contrast = 10.0;

e_colorizer
rgb_colorizer::type() const
{
    return COLORIZER_RGB;
}

rgb_colorizer::rgb_colorizer()
{
    set_colors(1.0,0.0,0.0);
}

rgb_colorizer::rgb_colorizer(const rgb_colorizer& c)
{
    set_colors(c.r,c.g,c.b);
}

rgb_colorizer::~rgb_colorizer()
{

}

bool 
rgb_colorizer::operator==(const colorizer& c) const
{
    const rgb_colorizer *rgb = dynamic_cast<const rgb_colorizer *>(&c);
    if(!rgb) return false;
    return rgb->r == r && rgb->g == g && rgb->b == b;
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
rgb_colorizer::calc(double dist) const
{
    struct rgb pixel;
    pixel.r = (char)(dist * cr);
    pixel.g = (char)(dist * cg);
    pixel.b = (char)(dist * cb);

    return pixel;
}

#define FIELD_RED "red"
#define FIELD_GREEN "green"
#define FIELD_BLUE "blue"

std::ostream& 
operator<<(std::ostream& s, const rgb_colorizer& cizer)
{
    s << "colorizer=" << (int) cizer.type() << "\n"
      << FIELD_RED << "=" << cizer.r << "\n" 
      << FIELD_GREEN << "=" << cizer.g << "\n" 
      << FIELD_BLUE << "=" << cizer.b << "\n" 
      << SECTION_STOP << "\n";
            
    return s;
}

std::istream&
operator>>(std::istream& is, rgb_colorizer& cizer)
{
    double r=1.0,g=0.0,b=0.0;

    while(is)
    {
        std::string name, value;

        read_field(is,name,value);
        std::istringstream vs(value.c_str());

        if(FIELD_RED == name)
            vs >> r;
        else if(FIELD_GREEN == name)
            vs >> g;
        else if(FIELD_BLUE == name)
            vs >> b;
        else if(SECTION_STOP == name)
            break;
    }
    cizer.set_colors(r,g,b);
    return is;
}

/* Color map subtype */
const int cmap_colorizer::size = 256;

cmap_colorizer::cmap_colorizer()
{
    /* build default cmap: same effect as default color */
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

cmap_colorizer::cmap_colorizer(const cmap_colorizer& c)
{
    cmap = new rgb_t[size];
    for(int i =0; i < size; i++)
    {
        cmap[i] = c.cmap[i];
    }
    name = c.name;
}

cmap_colorizer&
cmap_colorizer::operator=(const cmap_colorizer& c)
{
    if(this != &c)
    {
	//std::cout << "update " << this << " from " << c;
	delete[] cmap;
	cmap = new rgb_t[size];
	for(int i =0; i < size; i++)
	{
	    cmap[i] = c.cmap[i];
	}
	name = c.name;
    }


    return *this;
}

e_colorizer
cmap_colorizer::type() const 
{
    return COLORIZER_CMAP;
}

bool 
cmap_colorizer::operator==(const colorizer& c) const
{
    const cmap_colorizer *other_cmap = dynamic_cast<const cmap_colorizer *>(&c);
    if(!other_cmap) return false;
    if(other_cmap->name != name) return false;
    for(int i = 0; i < 256; ++i)
    {
	if(other_cmap->cmap[i].r != cmap[i].r) return false;
	if(other_cmap->cmap[i].g != cmap[i].g) return false;
	if(other_cmap->cmap[i].b != cmap[i].b) return false;
    }
    return true;
}

rgb_t
cmap_colorizer::calc(double dist) const
{
    // only exact zeroes count as color 0
    if(dist == 0.0)
    {
        return cmap[0];
    }
    rgb_t mix;

    /* a number in [1,255] - don't want to include color zero */
    int n = (int)dist;
    assert(n >= 0);
    n %= 255; n++;
    int n2 = (n == 255 ? 1 : n+1);
    double pos = fmod(dist,1.0);
    assert(n != 0 && n2 != 0);
    mix.r = (unsigned char)(cmap[n].r * (1.0 - pos) + cmap[n2].r * pos);
    mix.g = (unsigned char)(cmap[n].g * (1.0 - pos) + cmap[n2].g * pos);
    mix.b = (unsigned char)(cmap[n].b * (1.0 - pos) + cmap[n2].b * pos);

    return mix;
}

#define FIELD_FILENAME "file"

std::ostream& 
operator<<(std::ostream& s, const cmap_colorizer& cizer)
{
    s << FIELD_COLORIZER << "=" << (int) cizer.type()<< "\n";
    //s << FIELD_FILENAME << "=" << cizer.name << "\n";
    s << FIELD_COLORDATA << "=" << cizer.encode_color_data() << "\n";
    s << SECTION_STOP << "\n";
    return s;
}

std::string 
cmap_colorizer::encode_color_data(void) const
{
    std::ostringstream os;

    os << std::hex << std::setfill('0');
    for(int i = 0; i < 256; ++i)
    {
	os << std::setw(2) << (int)cmap[i].r;
	os << std::setw(2) << (int)cmap[i].g;
	os << std::setw(2) << (int)cmap[i].b;
    }
    return os.str();
}

void
cmap_colorizer::decode_color_data(const std::string& data)
{
    for(int i = 0; i < 256; ++i)
    {
	std::string s = data.substr(i*6,6);
	std::istringstream is(s);
	is >> std::hex;
	int val;
	is >> val;
	cmap[i].r = val >> 16;
	cmap[i].g = val >> 8 & 0xFF;
	cmap[i].b = val & 0xFF;
    }
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
        std::getline(cmapfile,line);
		
        std::istringstream ss(line.c_str());

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
    while(is)
    {
        std::string name, value;
        read_field(is,name,value);

        if(FIELD_FILENAME==name)
            cizer.set_cmap_file(value.c_str());
	else if(FIELD_COLORDATA==name)
	    cizer.decode_color_data(value);
        else if(SECTION_STOP==name)
            break;
    }
    return is;
}
