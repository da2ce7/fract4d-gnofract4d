// helper functions for file I/O

#include "io.h"

bool
read_field(std::istream& is, std::string& name, std::string& val)
{
    std::string line;
    std::getline(is,line);
        
    std::string::size_type eqpos = line.find("=");
    
    if(eqpos == std::string::npos)
    {
        // not a field=value pair
        name = line;
    }
    else
    {
        name = std::string(line,0,eqpos);
        val =  std::string(line,eqpos+1);
    }
    return (bool)is;
}

bool
write_field(std::ostream& os, const std::string& name)
{
    os << name << "=";
    return (bool) os;
}
