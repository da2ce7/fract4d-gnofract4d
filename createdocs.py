#!/usr/bin/env python

# run this to update some tables in the documentation

# making this a separate cmd (not part of setup.py) because importing
# gtk was causing "setup.py build" to crash - inexplicable...

# also the other python versions don't have gtk as a module,
# so were reporting errors.

import sys

def create_stdlib_docs():
    'Autogenerate docs'
    try:
        # create list of stdlib functions
        from fract4d import createdocs as cd1
        cd1.main("doc/gnofract4d-manual/C/stdlib.xml")

        # create list of mouse and GUI commands
        import fract4dgui.createdocs
        fract4dgui.createdocs.main("doc/gnofract4d-manual/C/commands.xml")
        
    except Exception, err:
        print >>sys.stderr,\
              "Problem creating docs. Online help will be incomplete."
        print >>sys.stderr, err

create_stdlib_docs()
