import ConfigParser
import os
import sys

class T(ConfigParser.ConfigParser):    
    "Holds preference data"
    def __init__(self, file):
        _defaults = {
            "compiler" : {
              "name" : "gcc",
              "options" : "-fPIC -DPIC -D_REENTRANT -O2 -shared -ffast-math"
            },
            "display" : {
              "width" : "640",
              "height" : "480",
              "antialias" : "1",
              "autodeepen" : "1"
            },
            "helpers" : {
              "editor" : "emacs",
              "mailer" : self.get_default_mailer(),
              "browser" : self.get_default_browser()
            },
            "general" : {
              "threads" : "1",
              "compress_fct" : "1",
            },
            "user_info" : {
              "name" : "",
              "flickr_token" : "",
              "nsid" : ""
            },
            "blogs" : {
            },
            "formula_path" : {
              "0" : "formulas",
              "1" : os.path.join(sys.exec_prefix, "share/gnofract4d/formulas"),
              "2" : os.path.expandvars("${HOME}/formulas")
            },
            "map_path" : {
              "0" : "maps",
              "1" : os.path.join(sys.exec_prefix, "share/gnofract4d/maps"),
              "2" : os.path.expandvars("${HOME}/maps")
            },
            "recent_files" : {
            },
            "ignored" : {
            },
            "director" : {
              "fct_enabled": "0",
              "fct_dir" : "/tmp",
              "png_dir" : "/tmp"
            }
        }

        self.image_changed_sections = {
            "display" : True,
            "compiler" : True
            }

        ConfigParser.ConfigParser.__init__(self)

        self.file = os.path.expanduser(file)
        self.read(self.file)

        # we don't use the normal ConfigParser default stuff because
        # we want sectionized defaults

        for (section,entries) in _defaults.items():
            if not self.has_section(section):
                self.add_section(section)
            for (key,val) in entries.items():
                if not self.has_option(section,key):
                    self.set(section,key,val)

    def get_default_mailer(self):
        return "evolution %s"

    def get_default_browser(self):
        return "mozilla %s"
    
    def set(self,section,key,val):
        if self.has_section(section) and \
           self.has_option(section,key) and \
           self.get(section,key) == val:
            return

        ConfigParser.ConfigParser.set(self,section,key,val)
        self.changed(section)

    def set_size(self,width,height):
        if self.getint("display","height") == height and \
           self.getint("display","width") == width:
            return
        
        ConfigParser.ConfigParser.set(self,"display","height",str(height))
        ConfigParser.ConfigParser.set(self,"display","width",str(width))
        self.changed("display")

    def get_list(self, name):
        i = 0
        list = []
        while(True):
            try:
                key = "%d" % i
                val = self.get(name,key)
                list.append(val)
                i += 1
            except ConfigParser.NoOptionError:
                return list

    def remove_all_in_list_section(self,name):
        i = 0
        items_left = True
        while items_left:            
            items_left = self.remove_option(name,"%d" % i)
            i += 1
        
    def set_list(self, name, list):
        self.remove_all_in_list_section(name)

        i = 0        
        for item in list:
            ConfigParser.ConfigParser.set(self, name,"%d" % i, item)
            i += 1

        self.changed(name)

    def update_list(self,name,new_entry,maxsize):
        list = self.get_list(name)
        if list.count(new_entry) == 0:
            list.insert(0,new_entry)
            list = list[:maxsize]
            self.set_list(name,list)

        return list
    
    def changed(self, section):
        pass
            
    def save(self):
        self.write(open(self.file,"w"))

instance = T("~/.gnofract4d")