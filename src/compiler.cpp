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

/* We use the C compiler at runtime to produce a new shared library containing
 * code which calculates this fractal - this file contains our interface to the
 * compiler */

#include "compiler.h"

#include <cstdio>

// TODO: replace all this with a fork/exec thingy so I can get exit status etc
compiler::compiler()
{
    flags = "-O3 -ffast-math";
    in = "compiler_template.cpp";
    out = "fract.so";
}

std::string
compiler::Dstring(std::string iter, std::string decl, std::string ret)
{
    return "-DITER=\"" + iter + "\" -DDECL=\"" + decl + "\" -DRET=\"" + ret + "\"";
}

int 
compiler::run(std::string iter, std::string decl, std::string ret)
{
    char buf[1000];

    std::string dflags = Dstring(iter, decl, ret);
    std::string commandLine = 
        "g++ -shared " + flags + " " + dflags + " " + in + " -o " + out + " 2>&1";

    FILE *compiler_output = popen(commandLine.c_str(),"r");
    if(NULL == compiler_output)
    {
        return 1;
    }
    else
    {
        while(fgets(buf,sizeof(buf),compiler_output))
        {
            printf(buf);
        }
        pclose(compiler_output);
    }
    return 0;
}

