#!/usr/bin/env python

# rudimentary read-only support for Fractint PAR files
import string

def decode_val(c):
    if c >= '0' and c <= '9':
        return 4 *(ord(c) - ord('0'))
    elif c >= 'A' and c <= 'Z':
        return 4 * (ord(c) - ord('A') + 10)
    elif c == '_':
        return 4 * 36
    elif c == '`':
        return 4 * 37
    elif c >= 'a' and c <= 'z':
        return 4 * (ord(c) - ord('A') + 38)
    else:
        raise RuntimeError, "Invalid character %s in colors" % c
    
def colorRange(s):
    '''From help4.src:

    The colors= parameter in a PAR entry is a set of triplets.  Each
    triplet represents a color in the saved palette.  The triplet is
    made from the red green and blue components of the color in the
    palette entry.  The current limitations of fractint\'s palette
    handling capabilities restrict the palette to 256 colors.  Each
    triplet rgb component is a 6 bit value from 0 to 63.  These values
    are encoded using the following scheme:

     rgb value  =>  encoded value
      0  -   9  =>  0  -  9
     10  -  35  =>  A  -  Z
     36  -  37  =>  _  -  `
     38  -  63  =>  a  -  z
   
    In addition, Pieter Branderhorst has incorporated a way to
    compress the encoding when the image has smooth-shaded ranges.
    These ranges are written as <nn> with the nn representing the
    number of entries between the preceeding triplet and the following
    triplet.'''

    colors = []
    i = 0
    runlength = 0
    while i < len(s):
        c = s[i]
        if c == '<':
            j = string.find(s,">", i)
            if j == -1:
                raise RuntimeError, "No > after < in colors"
            runlength = string.atoi(s[i+1:j])
            if runlength == 0:
                raise RuntimeError, "Zero runlength"
            i = j+1
        else:
            if len(s) < i+3:
                raise RuntimeError, "invalid color string"
            rgb = map(decode_val, list(s[i:i+3]))
            if runlength > 0:
                if len(colors) == 0:
                    raise RuntimeError, "run with no preceding color"
                pairs = zip(colors[-1],rgb)
                for k in range(0,runlength):
                    ratio = (k+1.0) / runlength
                    nratio = 1.0 - ratio
                    col = map(lambda (x,y) : int(x * nratio + y * ratio), pairs)
                    colors.append(col)
                    
            colors.append(rgb)
            i += 3
            runlength = 0
            
    return colors
     

        
