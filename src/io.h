// Helper functions for file I/O

#include <fstream>
#include <strstream>
#include <string>

bool read_field(std::istream& is, std::string& name, std::string& val);
bool write_field(std::ostream& os, const std::string& name);
