#!/usr/bin/env python

# Update gnofract4d.pot with all the gettextized strings in the app

# Compile all .po translation files into .mo files

# Additionally contruct a "Pseudo-Localized" .po and .mo for "Xaxian",
# a made-up language with language ID "XX", which I use to check that
# I've found all the strings which need to be marked for translation

# To run this script you need msgfmt.py and pygettext.py, from the Python
# source distribution

import os
import re

def find_files_in_dir(dirname,required_ext):
    "find all the files in 'dirname' ending in ext"
    pyfiles = []
    files = os.listdir(dirname)
    for f in files:
        # skip test files
        if f.startswith("test_"): continue
        
        absfile = os.path.join(dirname,f)
        (name,ext) = os.path.splitext(absfile)
        if ext.lower() == required_ext:
            pyfiles.append(absfile)
    return pyfiles

def find_all_source_files():
    return find_files_in_dir("../fract4d", ".py") + \
           find_files_in_dir("../fract4dgui", ".py") + \
           [ "../gnofract4d"]

def make_pot_file():
    "process all the .py files in the app to make a .pot"
    files = find_all_source_files()
    ret = os.system("pygettext.py -o gnofract4d.pot %s" % " ".join(files))
    if ret:
        raise IOError("Can't run pygettext.py")

def xify_char(inmatch):
    inchar = inmatch.group(0)
    subs = { "" : "x" , "u" : "oo" , "a" : "aa", "e" : "E" }
    return subs.get(inchar, inchar)

def make_pseudoloc_file(infile,outfile):
    '''Construct xx.po, a mechanical 'translation' into Xaxian. This
    charming language is remarkably similar to English, except that:

    1) Every word has x inserted at the front
    2) u => oo
    3) a => aa
    4) e => E
    '''
    re_msgid = re.compile(r'msgid "(.*?)"')    
    re_xify = re.compile(r'((?<!%)\b(?=\w))|([uae])') 
    re_msgstr = re.compile(r'(?<=msgstr ")(?=")')
    english_string = ""
    xified_string = ""
    for line in infile:
        m = re_msgid.match(line)
        if m:
            english_string = m.group(1)
            xified_string = re_xify.sub(xify_char,english_string)
        else:
            line = re_msgstr.sub(xified_string,line)
        print >>outfile, line,

def find_po_files():
    return find_files_in_dir(".",".po")

def make_mo_file(f):
    (name,ext) = os.path.splitext(f)
    outdir = "%s/LC_MESSAGES/" % name
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    ret = os.system("msgfmt.py -o %s/gnofract4d.mo %s" % (outdir,f))
    if ret:
        raise IOError("can't run msgfmt.py")
    
def make_mo_files():
    ''' For each <lang>.po file, create <lang>/LC_MESSAGES/gnofract4d.mo'''
    files = find_po_files()
    for f in files:
        make_mo_file(f)
        
def main():
    make_pot_file()
    make_pseudoloc_file(open("gnofract4d.pot"),open("xx.po","w"))
    make_mo_files()
    
if __name__ == "__main__":
    main()

