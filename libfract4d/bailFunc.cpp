/* Gnofract4D -- a little fractal generator-browser program
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

#include "bailFunc.h"
#include "iterFunc.h"
#include "io.h"

#include <cstddef>
#include <cmath>
#include <iostream>

#define FIELD_FUNCTION "function"

inline double MIN(double x, double y) { return x < y ? x : y; }
inline double MAX(double x, double y) { return x > y ? x : y; }

class bailFuncImpl : public bailFunc
{
public:
    virtual ~bailFuncImpl() {};

    friend std::ostream& operator<< (std::ostream& s, const bailFuncImpl& m);
    friend std::istream& operator>> (std::istream& s, bailFuncImpl& m);
    std::ostream& put(std::ostream& s) const { return s << *this; } 
    std::istream& get(std::istream& s) { return s >> *this;  } 

    bool operator==(const bailFunc& a) const
	{
	    return type() == a.type();
	}
};


std::ostream& 
operator<<(std::ostream& s, const bailFuncImpl& m) 
{ 
    write_field(s,FIELD_FUNCTION);
    s << m.type() << "\n";
    s << SECTION_STOP << "\n"; 
    return s; 
} 

std::istream& 
operator>>(std::istream& s, bailFuncImpl& m) 
{ 
    while(s)
    {
        std::string name,val;
        
        if(!read_field(s,name,val))
        {
            break;
        }
        if(SECTION_STOP == name) break;
    }
    return s; 
}

class mag_bailout : public bailFuncImpl {
public:
    std::string bail_code(int flags) const 
        {
            std::string bail("");
            
            /* produces weird results, but I don't understand why...
            if(flags & USE_COMPLEX)
            {
                return "p[EJECT_VAL] = norm(z)";
            }
            */
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "p[X2] = XPOS * XPOS;"
                    "p[Y2] = YPOS * YPOS;";
            }

            bail += "p[EJECT_VAL] = p[X2] + p[Y2];";
            return bail;
        } 
    bool iter8_ok() const { return true; };
    bool period_ok() const { return true; };
    e_bailFunc type() const { return BAILOUT_MAG ; };
};

/* eject if difference between this point and last iteration is < epsilon */
class diff_bailout : public bailFuncImpl {
public:
    std::string bail_code(int flags) const
        {
            return 
                "double epsilon = pfo->m_period_tolerance;"
                "double diffx = XPOS - p[LASTX];"
                "double diffy = YPOS - p[LASTY];"

                "double diff = diffx * diffx + diffy * diffy;"

                "p[LASTX] = XPOS; p[LASTY] = YPOS;"
                // FIXME: continuous potential doesn't work well with this
                "p[EJECT_VAL] = p[EJECT] + epsilon - diff;";
        }
    bool iter8_ok() const { return false; };
    bool period_ok() const { return false; };
    e_bailFunc type() const { return BAILOUT_DIFF ; };
};


class real_bailout : public bailFuncImpl {
public:
    virtual std::string bail_code(int flags) const     
        {
            std::string bail("");
            if(!(flags & (HAS_X2)))
            {
                bail = "p[X2] = XPOS * XPOS;";
            }            
            
            bail += 
                "p[EJECT_VAL] = p[X2];";
            return bail;
        };
    bool iter8_ok() const { return false; };
    bool period_ok() const { return true; };
    e_bailFunc type() const { return BAILOUT_REAL ; };
};

class imag_bailout : public bailFuncImpl {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            if(!(flags & (HAS_Y2)))
            {
                bail = "p[Y2] = YPOS * YPOS;";
            }            
            bail += "p[EJECT_VAL] = p[Y2];";
            return bail;
        };
    bool iter8_ok() const { return false; };
    bool period_ok() const { return true; };
    e_bailFunc type() const { return BAILOUT_IMAG ; };
};

class and_bailout : public bailFuncImpl {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "p[X2] = XPOS * XPOS;"
                    "p[Y2] = YPOS * YPOS;";
            }            
            bail += "p[EJECT_VAL] = std::min(p[X2],p[Y2]);";
            return bail;
        };
    bool iter8_ok() const { return true; };
    bool period_ok() const { return true; };
    e_bailFunc type() const { return BAILOUT_AND ; };
};

class or_bailout : public bailFuncImpl {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");            
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "p[X2] = XPOS * XPOS;"
                    "p[Y2] = YPOS * YPOS;";
            }       
            bail += "p[EJECT_VAL] = std::max(p[X2],p[Y2]);";
            return bail;
        }
    bool iter8_ok() const { return true; }
    bool period_ok() const { return true; };
    e_bailFunc type() const { return BAILOUT_OR ; };
};

class manhattan2_bailout : public bailFuncImpl {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "p[X2] = XPOS * XPOS;"
                    "p[Y2] = YPOS * YPOS;";
            }            
            bail += "{double t = fabs(p[X2]) + fabs(p[Y2]); p[EJECT_VAL] = t*t;}";
            return bail;
        }
    bool iter8_ok() const { return false; }
    bool period_ok() const { return true; };
    e_bailFunc type() const { return BAILOUT_MANH2 ; };
};

class manhattan_bailout : public bailFuncImpl {
public:
    virtual std::string bail_code(int flags) const 
        {
            return "p[EJECT_VAL] = XPOS + YPOS;";
        }
    bool iter8_ok() const { return false; }
    bool period_ok() const { return true; }

    e_bailFunc type() const { return BAILOUT_MANH ; }
    static const char *name() { return "Manhattan"; }
    static bailFunc *create() { return new manhattan_bailout(); } 
};

/*
typedef struct 
{
    const char *name;
    bailFunc *(*ctor)();
} bailFunc_data;

static bailFunc_data infoTable[] = {
    { manhattan_bailout::name(), manhattan_bailout::create },
    { NULL, NULL }
};

static const char **createNameTable()
{
    int nNames = sizeof(infoTable)/sizeof(infoTable[0]);
    const char **names = new const char *[ nNames + 1 ];

    for(int i = 0; i < nNames; ++i)
    {
	names[i] = infoTable[i].name;
    }
    return names;
}

const char **bailFunc::names()
{ 
    static const char **nameTable = createNameTable();

    return nameTable;
}
*/

bailFunc *bailFunc::create(e_bailFunc e)
{
    bailFunc *pbf=NULL;
    switch(e){
    case BAILOUT_MAG:
        pbf = new mag_bailout;
        break;
    case BAILOUT_MANH:
        pbf = new manhattan_bailout;
        break;
    case BAILOUT_MANH2:
        pbf = new manhattan2_bailout;
        break;
    case BAILOUT_OR:
        pbf = new or_bailout;
        break;
    case BAILOUT_AND:
        pbf = new and_bailout;
        break;
    case BAILOUT_REAL:
        pbf = new real_bailout;
        break;
    case BAILOUT_IMAG:
        pbf = new imag_bailout;
        break;
    case BAILOUT_DIFF:
        pbf = new diff_bailout;
        break;
    default:
        std::cerr << "Warning: unknown bailFunc value" << (int)e << "\n";
    }
     
    return pbf;
}

bailFunc *bailFunc::read(std::istream& s)
{
    std::string name, value;
/*
  FIXME
    while(s)
    {
        read_field(s,name,value);
    
        if(FIELD_FUNCTION == name)
        {
            bailFunc *f = bailFunc::create(value.c_str());
            if(f)
            {
                s >> *f;
            }
            return f;
        }
    }
*/
    return NULL;

}
