import os
import sys

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
    
