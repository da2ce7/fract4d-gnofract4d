import os
import sys

from fract4d import fract4dc

# stub class for selecting a suitable readwrite method depending on platform,
# to be used whenever a file desciptor returned from fract4dc.pipe() is used.


class gtkio:
    def read(self, fd, len):
        return os.read(fd, len)
