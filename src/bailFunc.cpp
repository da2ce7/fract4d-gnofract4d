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

#include <cstddef>
#include <cmath>
#include <iostream>

inline double MIN(double x, double y) { return x < y ? x : y; }
inline double MAX(double x, double y) { return x > y ? x : y; }

class mag_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            
            /* produces weird results, but I don't understand why...
            if(flags & USE_COMPLEX)
            {
                return "pTemp[EJECT_VAL] = norm(z)";
            }
            */
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "pTemp[X2] = XPOS * XPOS;"
                    "pTemp[Y2] = YPOS * YPOS;";
            }

            bail += "pTemp[EJECT_VAL] = pTemp[X2] + pTemp[Y2];";
            return bail;
        } 
    void init(void) {};
    bool iter8_ok() const { return true; };
};

/* eject if difference between this point and last iteration is < epsilon */
class diff_bailout : public bailFunc {
public:
    std::string bail_code(int flags) const
        {
            return 
                "double epsilon = 0.01;"
                "double diffx = XPOS - pTemp[LASTX];"
                "double diffy = YPOS - pTemp[LASTY];"

                "double diff = diffx * diffx + diffy * diffy;"

                "pTemp[LASTX] = XPOS; pTemp[LASTY] = YPOS;"
                // FIXME: continuous potential doesn't work well with this
                "pTemp[EJECT_VAL] = pInput[EJECT] + epsilon - diff;";
        }
    bool iter8_ok() const { return false; };
};


class real_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const     
        {
            std::string bail("");
            if(!(flags & (HAS_X2)))
            {
                bail = "pTemp[X2] = XPOS * XPOS;";
            }            
            
            bail += 
                "pTemp[EJECT_VAL] = pTemp[X2];";
            return bail;
        };
    bool iter8_ok() const { return false; };
};

class imag_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            if(!(flags & (HAS_Y2)))
            {
                bail = "pTemp[Y2] = YPOS * YPOS;";
            }            
            bail += "pTemp[EJECT_VAL] = pTemp[Y2];";
            return bail;
        };
    bool iter8_ok() const { return false; };
};

class and_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "pTemp[X2] = XPOS * XPOS;"
                    "pTemp[Y2] = YPOS * YPOS;";
            }            
            bail += "pTemp[EJECT_VAL] = std::min(pTemp[X2],pTemp[Y2]);";
            return bail;
        };
    bool iter8_ok() const { return true; };

};

class or_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");            
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "pTemp[X2] = XPOS * XPOS;"
                    "pTemp[Y2] = YPOS * YPOS;";
            }       
            bail += "pTemp[EJECT_VAL] = std::max(pTemp[X2],pTemp[Y2]);";
            return bail;
        }
    bool iter8_ok() const { return true; }

};

class manhattan2_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const 
        {
            std::string bail("");
            if(!(flags & (HAS_X2 | HAS_Y2)))
            {
                bail = 
                    "pTemp[X2] = XPOS * XPOS;"
                    "pTemp[Y2] = YPOS * YPOS;";
            }            
            bail += "{double t = fabs(pTemp[X2]) + fabs(pTemp[Y2]); pTemp[EJECT_VAL] = t*t;}";
            return bail;
        }
    bool iter8_ok() const { return false; }
};

class manhattan_bailout : public bailFunc {
public:
    virtual std::string bail_code(int flags) const 
        {
            return "pTemp[EJECT_VAL] = XPOS + YPOS;";
        }
    bool iter8_ok() const { return false; }
};

bailFunc *bailFunc_new(e_bailFunc e)
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
