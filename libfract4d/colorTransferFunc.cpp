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

#include "colorTransferFunc.h"
#include "iterFunc.h"

#include <cstddef>
#include <cmath>
#include <iostream>

// no-op
class linear_colorTransferFunc : public colorTransferFunc {
public:
    double calc(double in) const
        {
            return in;
        }
    static colorTransferFunc *create() { 
	return new linear_colorTransferFunc(); 
    }
};

// psuedo-log function
class log_colorTransferFunc : public colorTransferFunc {
public:
    double calc(double in) const
        {
	    double val = in;
	    while(val > 256.0)
	    {
		val /= 2.0;
	    }
            return val;
        }
    static colorTransferFunc *create() { 
	return new log_colorTransferFunc(); 
    }
};
  

// sqrt
class sqrt_colorTransferFunc : public colorTransferFunc {
public:
    double calc(double in) const
        {
	    return sqrt(in);
        }
    static colorTransferFunc *create() { 
	return new sqrt_colorTransferFunc(); 
    }
};


typedef struct 
{
    const char *name; 
    colorTransferFunc *(*ctor)();
} ctorInfo;

static ctorInfo infoTable[] = {
    { "Linear", linear_colorTransferFunc::create },
    { "Log", log_colorTransferFunc::create },
    { "Square Root",sqrt_colorTransferFunc::create },
    { NULL, NULL}
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

const char **colorTransferFunc::names()
{
    static const char **nameTable = createNameTable();

    return nameTable;    
};

colorTransferFunc *colorTransferFunc::create(const char *name)
{
    ctorInfo *cinfo = infoTable;
    colorTransferFunc *pctf=NULL;
    while(cinfo->name != NULL)
    {
	if(0 == strcmp(name,cinfo->name))
	{
	    pctf = (*cinfo->ctor)();
	    break;
	}
	cinfo++;
    }
    if(NULL == pctf)
    {
        std::cerr << "Warning: unknown colorTransferFunc '" << name << "'\n";
    }
     
    return pctf;
}

colorTransferFunc *colorTransferFunc::read(std::istream& a)
{
    // FIXME
    return NULL;
}
