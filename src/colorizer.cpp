#include "colorizer.h"
#include "iterFunc.h"
#include "io.h"

#include <cstdlib>
#include <string>
#include <fstream>
#include <strstream>

#include <cmath>

#define FIELD_COLORIZER "colorizer"

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

    std::string name, value;

    while(is)
    {
        read_field(is,name,value);

        std::istrstream vs(value.c_str());

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
rgb_colorizer::operator()(int n, double *scratch, bool potential) const
{
    struct rgb pixel={0,0,0};
    double dn;
    
    if (n != -1){
        if(potential) 
            dn = (double)n + scratch[EJECT]/scratch[EJECT_VAL];
        else
            dn = (double)n;

        pixel.r = (char)(dn * cr);
        pixel.g = (char)(dn * cg);
        pixel.b = (char)(dn * cb);
    }
    return pixel;
}

#define FIELD_RED "red"
#define FIELD_GREEN "green"
#define FIELD_BLUE "blue"

std::ostream& 
operator<<(std::ostream& s, const rgb_colorizer& cizer)
{
    s << "colorizer=" << cizer.type() << "\n"
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
        std::istrstream vs(value.c_str());

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
    delete[] cmap;
    cmap = new rgb_t[size];
    for(int i =0; i < size; i++)
    {
        cmap[i] = c.cmap[i];
    }
    name = c.name;

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
    const cmap_colorizer *cmap = dynamic_cast<const cmap_colorizer *>(&c);
    if(!cmap) return false;
    return cmap->name == name;
}

rgb_t
cmap_colorizer::operator()(int n, double *scratch, bool potential) const
{
    if(n == -1)
    {
        return cmap[0];
    }
    rgb_t mix;
    
    n %= 255;
    double pos = potential ? scratch[EJECT]/scratch[EJECT_VAL] : 0.0;
    mix.r = (unsigned char)(cmap[n].r * (1.0 - pos) + cmap[n+1].r * pos);
    mix.g = (unsigned char)(cmap[n].g * (1.0 - pos) + cmap[n+1].g * pos);
    mix.b = (unsigned char)(cmap[n].b * (1.0 - pos) + cmap[n+1].b * pos);
    return mix;
}

#define FIELD_FILENAME "file"

std::ostream& 
operator<<(std::ostream& s, const cmap_colorizer& cizer)
{
    s << FIELD_COLORIZER << "=" << cizer.type()<< "\n";
    s << FIELD_FILENAME << "=" << cizer.name << "\n";
    s << SECTION_STOP << "\n";
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
        std::getline(cmapfile,line);
		
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
    while(is)
    {
        std::string name, value;
        read_field(is,name,value);

        if(FIELD_FILENAME==name)
            cizer.set_cmap_file(value.c_str());
        else if(SECTION_STOP==name)
            break;
    }
    return is;
}
