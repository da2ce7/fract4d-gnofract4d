import os
import sys
import inspect

import gtk

def find_resource(name, local_dir, installed_dir):
    'try and find a file either locally or installed'
    local_name = os.path.join(local_dir,name)
    if os.path.exists(local_name):
        return local_name

    return os.path.join(sys.exec_prefix, installed_dir, name)

def find_in_path(exe):
    # find an executable along PATH env var
    pathstring = os.environ["PATH"]
    if pathstring == None or pathstring == "":
        return None
    paths = pathstring.split(":")
    for path in paths:
        full_path = os.path.join(path,exe)
        if os.path.exists(full_path):
            return full_path
    return None
    
def stack_trace():
    stack = inspect.stack()
    str = ""
    for frame in stack[1:]:
        (frame_obj, filename, line, funcname, context, context_index) = frame
        try:
            args = inspect.formatargvalues(*inspect.getargvalues(frame_obj))
        except Exception:
            args = "<unavailable>"
        
        frame_desc = "%s(%s)\t\t%s(%s)\n" % (filename, line, funcname, args)
        str += frame_desc
    return str
    
def get_rgb_colormap():
    # work around a difference between pygtk versions
    if hasattr(gtk.gdk,'rgb_get_colormap'):
        c = gtk.gdk.rgb_get_colormap()
    else:
        c = gtk.gdk.rgb_get_cmap()
    return c
