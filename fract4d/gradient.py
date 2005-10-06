#!/usr/bin/env python

import math
import re
import StringIO
import copy
import random
import types

#Class definition for Gradients
#These use the format defined by the GIMP

#The file format is:
# GIMP Gradient ; literal identifier
# Name: <utf8-name> ; optional, else get from filename
# 3 ; number of points N
# ; N  lines like this
# 0.000000 0.166667 0.333333 0.000000 0.000000 1.000000 1.000000 0.000000 0.000000 1.000000 1.000000 0 0
# The format is
# start middle end [range 0...1]
# R G B A left endpoint
# R G B A right endpoint
# segment_type coloring_type

# segment-type is 
#   GIMP_GRADIENT_SEGMENT_LINEAR,
#   GIMP_GRADIENT_SEGMENT_CURVED,
#   GIMP_GRADIENT_SEGMENT_SINE,
#   GIMP_GRADIENT_SEGMENT_SPHERE_INCREASING,
#   GIMP_GRADIENT_SEGMENT_SPHERE_DECREASING

# color type is
#   GIMP_GRADIENT_SEGMENT_RGB,      /* normal RGB           */
#   GIMP_GRADIENT_SEGMENT_HSV_CCW,  /* counterclockwise hue */
#   GIMP_GRADIENT_SEGMENT_HSV_CW    /* clockwise hue        */


#gradientfile_re = re.compile(r'\s*(RGB|HSV)\s+(Linear|Sinusoidal|CurvedI|CurvedD)\s+(\d+\.?\d+)\s+(\d+)\s+(\d+)\s+(\d+\.?\d+)\s+(\d+)\s+(\d+)')

class Blend:
    LINEAR, CURVED, SINE, SPHERE_INCREASING, SPHERE_DECREASING = range(5)

class ColorMode:
    RGB, HSV_CCW, HSV_CW = range(3)

class Error(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class HsvError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class Segment:
    EPSILON=1.0E-7
    def __init__(self, left, left_color, right, right_color, mid=None,
                 blend_mode=Blend.LINEAR,
                 color_mode=ColorMode.RGB):
        
        self.cmode = color_mode
        self.bmode = blend_mode
        self.left = left
        self.left_color = left_color
        self.right = right
        self.right_color = right_color
        if mid == None:
            self.center()
        else:
            self.mid = mid

    def __copy__(self):
        return Segment(
            self.left, self.left_color[:],
            self.right, self.right_color[:], self.mid,
            self.blend_mode, self.color_mode)
    
    def __eq__(self,other):
        return self.cmode == other.cmode and \
               self.bmode == other.bmode and \
               self.close(self.left, other.left) and \
               self.close(self.right, other.right) and \
               self.close(self.mid, other.mid) and \
               self.close(self.left_color, other.left_color) and \
               self.close(self.right_color, other.right_color)

    def __ne__(self, other):
        return not self.__eq__(other)

    def close(self, a, b):
        # True if a is nearly == b
        if isinstance(a, types.ListType):
            for (ax,bx) in zip(a,b):
                if abs(ax-bx) > 1.0E-5:
                    return False
            return True
        else:
            return abs(a-b) < 1.0E-5
    
    def center(self):
        self.mid = (self.left + self.right) / 2.0
        
    def get_linear_factor(self, pos, middle):
        if pos <= middle:
            if middle < Segment.EPSILON:
                return 0.0
            else:
                return 0.5 * pos / middle
        else:
            pos -= middle;
            middle = 1.0 - middle
            if middle < Segment.EPSILON:
                return 1.0
            else:
                return 0.5 + 0.5 * pos / middle

    def get_curved_factor(self, pos, middle):
        if middle < Segment.EPSILON:
            middle = Segment.EPSILON

        try:
            return math.pow(pos, ( math.log(0.5) / math.log(middle) ))
        except ZeroDivisionError:
            # 0^negative number is NaN
            return 0.0
        
    def get_sine_factor(self, pos, middle):
        pos = self.get_linear_factor(pos, middle)
        return (math.sin ((-math.pi / 2.0) + math.pi * pos) + 1.0) / 2.0
    def get_sphere_increasing_factor(self, pos, middle):
        pos = self.get_linear_factor(pos, middle) - 1.0
        return math.sqrt (1.0 - pos * pos)
    def get_sphere_decreasing_factor(self, pos, middle):
        pos = self.get_linear_factor(pos, middle)
        return 1.0 - math.sqrt (1.0 - pos * pos)

    def get_color_at(self, pos):
        'compute the color value for a point in this segment'
        
        lcol = self.left_color
        rcol = self.right_color
        if self.cmode == ColorMode.HSV_CCW or self.cmode == ColorMode.HSV_CW:
            # fixme, distinguish between these cases
            lcol = RGBtoHSV(lcol)
            rcol = RGBtoHSV(rcol)
            
        len = self.right-self.left
        if len < Segment.EPSILON:
            # avoid division by zero
            mpos = 0.5
            pos = 0.5
        else:
            mpos = (self.mid - self.left) / len
            pos  = (pos- self.left) / len
        
        if self.bmode == Blend.LINEAR:
            factor = self.get_linear_factor(pos, mpos)
        elif self.bmode == Blend.CURVED:
            factor = self.get_curved_factor(pos, mpos)
        elif self.bmode == Blend.SINE:
            factor = self.get_sine_factor(pos, mpos)
        elif self.bmode == Blend.SPHERE_INCREASING:
            factor = self.get_sphere_increasing_factor(pos, mpos)
        elif self.bmode == Blend.SPHERE_DECREASING:
            factor = self.get_sphere_decreasing_factor(pos, mpos)
        
        #Assume RGB mode, for the moment
        RH = lcol[0] + (rcol[0] - lcol[0]) * factor
        GS = lcol[1] + (rcol[1] - lcol[1]) * factor
        BV = lcol[2] + (rcol[2] - lcol[2]) * factor
        A  = lcol[3] + (rcol[3] - lcol[3]) * factor
        
        if self.cmode == ColorMode.RGB:
            return [RH, GS, BV, A]
        else:
            return HSVtoRGB([RH,GS,BV,A])

    def save(self,f):
        print >>f, "%6f %6f %6f" % (self.left, self.mid, self.right),
        for x in self.left_color + self.right_color:
            print >>f, "%6f" % x,
        print >>f, "%d %d" % (self.bmode, self.cmode)
            
class Gradient:
    def __init__(self):
        self.segments=[
            Segment(0,[0,0,0,1.0], 1.0, [1.0,1.0,1.0,1.0])]

        # a prettier default
        # Segment(0, [255, 255,0],  .5,  [255, 0, 0]),
        # Segment(.5, [255, 0, 0],  .55, [0, 0, 255]),
        # Segment(.55,[0, 0, 255],  .7,  [0, 128, 0]),
        # Segment(.7, [0, 128, 0], 1.0,  [255, 255, 0])]

        self.name=None
        self.alternate=0
        self.offset=0
        self.cobject=None
        
    def __copy__(self):
        c = Gradient()
        c.name = self.name
        c.alternate = self.alternate
        c.offset = self.offset
        c.segments = copy.deepcopy(self.segments)
        return c

    def __eq__(self, other):
        if not isinstance(other, Gradient): return False
        if self.name != other.name: return False
        if self.segments != other.segments: return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def serialize(self):
        s = StringIO.StringIO()
        self.save(s)
        return s.getvalue()

    def save(self,f):
        print >>f, "GIMP Gradient"
        if self.name:
            print >>f, "Name:", self.name
        print >>f, len(self.segments)
        for seg in self.segments:
            seg.save(f)

    def load(self,f):
        new_segments = []
        name = None
        line = f.readline()
        if line != "GIMP Gradient\n":
            raise Error("Invalid gradient file: no header found")
        
        try:
            line = f.readline()
            if line.startswith("Name:"):
                name = line[5:].strip()
                line = f.readline()
            num_vals = int(line)
            for i in xrange(num_vals):
                line = f.readline()
                [left, mid, right,
                 lr, lg, lb, la,
                 rr, rg, rb, ra,
                 bmode, cmode] = line.split()

                if int(cmode) != ColorMode.RGB:
                    raise HsvError("This gradient file requires HSV support, which is not yet implemented")
                seg = Segment(
                    float(left), [float(lr), float(lg), float(lb), float(la)],
                    float(right),[float(rr), float(rg), float(rb), float(ra)],
                    float(mid),
                    int(bmode), int(cmode))
                new_segments.append(seg)
        except Exception, err:
            raise err
        
        self.segments = new_segments
        self.name = name

    def compare_colors(self, c1, c2, maxdiff=0):
        # return true if floating-point colors c1 and c2 are close
        # enough that they would be equal when truncated to 8 bits
        for (a,b) in zip(c1, c2):
            a8 = int(a * 255.0)
            b8 = int(b * 255.0)
            if abs(a8 - b8) > maxdiff:
                return False
        return True
    
    def load_list(self,l, maxdiff=0):
        # a colorlist is a simplified gradient, of the form
        # (index, r, g, b, a) (colors are 0-255 ints)
        # each index is the left-hand end of the segment
        
        # each colorlist entry is mapped to a segment endpoint

        if len(l) == 0:
            raise Error("No colors found")
        
        new_segments = []
        last_index = 0.0
        last_color = [0.0,0.0,0.0,1.0]
        before_last_color = [-1000.0, -1000.0 , -1000.0, -1000.0] # meaningless color
        before_last_index = -1.0
        
        for (index,r,g,b,a) in l:
            color = [r/255.0, g/255.0, b/255.0, a/255.0]
            if index != last_index:
                test_segment = Segment(
                    before_last_index,
                    before_last_color,
                    index,
                    color)
                if self.compare_colors(
                    test_segment.get_color_at(last_index), last_color, maxdiff):
                    # can compress, update in place
                    new_segments[-1].right_color = color
                    new_segments[-1].right = index
                    new_segments[-1].center()
                else:
                    new_segments.append(
                        Segment(last_index, last_color, index, color))

                    before_last_index = last_index
                    before_last_color = last_color
            last_color = color
            last_index = index
            
        # fix gradient by adding extra flat section if last index not 1.0
        if new_segments[-1].right != 1.0:
            new_segments.append(
                Segment(new_segments[-1].right, last_color, 1.0, last_color))
            
        self.segments = new_segments

    def complementaries(self, base_color):
        # return some other colors that "go" with this one
        hsv = RGBtoHSV(base_color)

        (h,s,v,a) = hsv
        
        # take 2 colors which are almost opposite
        h = hsv[0]
        h2 = math.fmod(h + 2.6, 6.0)
        h3 = math.fmod(h + 3.4, 6.0)

        # take darker and lighter versions
        v = hsv[2]
        vlight = self.clamp(v * 1.5, 0.0, 1.0)
        vdark = v * 0.5

        colors = [
            [h, s, vdark, a],
            [h, s, v, a],
            [h, s, vlight, a],
            [h2, s, vlight, a],
            [h2, s, v, a],
            [h2, s, vdark, a],
            [h3, s, vdark, a],
            [h3, s, v, a],
            [h3, s, vlight, a]]

        colors = [ HSVtoRGB(x) for x in colors]
        return colors

    def randomize(self, length):
        base = [random.random(), random.random(), random.random(), 1.0]
        colors = self.complementaries(base)
        self.segments = []
        prev_index = 0.0
        prev_color = colors[0]
        first_color = prev_color
        for i in xrange(9-1):
            index = float(i+1)/length
            color = colors[i]
            self.segments.append(
                Segment(prev_index, prev_color, index, color))
            prev_color = color
            prev_index = index
        
        self.segments.append(
            Segment(prev_index, prev_color, 1.0, first_color)) # make it wrap
        
    def old_randomize(self, length):
        self.segments = []
        prev_index = 0.0
        prev_color = [random.random(), random.random(), random.random(), 1.0]
        first_color = prev_color
        for i in xrange(length-1):
            index = float(i+1)/length
            if i % 2 == 1:                
                color = [random.random(), random.random(), random.random(), 1.0]
            else:
                color = [0.0, 0.0, 0.0, 1.0]
            self.segments.append(
                Segment(prev_index, prev_color, index, color))
            prev_color = color
            prev_index = index
        
        self.segments.append(
            Segment(prev_index, prev_color, 1.0, first_color)) # make it wrap

    def get_color_at(self, pos):
        # returns the color at position x (0 <= x <= 1.0) 
        seg = self.get_segment_at(pos)
        return seg.get_color_at(pos)
        
    def get_segment_at(self, pos):
        #Returns the segment in which pos resides.
        if pos < 0.0:
            raise IndexError("Must be between 0 and 1")
        for seg in self.segments:
            if pos <= seg.right:
                return seg
        
        # not found - must be > 1.0
        raise IndexError("Must be between 0 and 1")

    def get_index_at(self, pos):
        # returns the index of the segment in which pos resides
        if pos < 0.0:
            raise IndexError("Must be between 0 and 1")
        length = len(self.segments)
        for i in xrange(length):
            if pos <= self.segments[i].right:
                return i
        
        # not found - must be > 1.0
        raise IndexError("Must be between 0 and 1")

    def add(self, segindex):
        # split the segment which contains point x in half
        seg = self.segments[segindex]
        
        if segindex+1 < len(self.segments):
            # copy info from next segment to right
            segright = self.segments[segindex+1]
            right_index = segright.left
            right_color = segright.left_color
        else:
            # adding at right-hand end
            right_index = 1.0
            right_color = seg.right_color
        
        s_len = (seg.right-seg.left)
        s_mid = seg.left + s_len*0.5
        newcol= self.get_color_at(s_mid)

        # update existing segment to occupy left half
        seg.right = s_mid
        seg.right_color = newcol
        seg.center()
        
        # add new segment to fill right half
        self.segments.insert(
            segindex+1,
            Segment(s_mid, newcol,
                    right_index, right_color,
                    None, 
                    seg.bmode, seg.cmode))

    def remove(self, segindex, smooth=False):
        # remove the segment which contains point x
        # extend each of our neighbors so they get half our space each
        if len(self.segments) < 2:
            raise Error("Can't remove last segment")
        
        seg = self.segments[segindex]

        if segindex > 0:
            # we have a previous segment
            if segindex+1 < len(self.segments):
                # and we have a next. Move them both to touch in the middle
                self.segments[segindex-1].right=seg.mid                
                self.segments[segindex+1].left=seg.mid
                self.segments[segindex-1].center()
                self.segments[segindex+1].center()
                if smooth:
                    midcolor = seg.get_color_at(seg.mid)
                    self.segments[segindex-1].right_color = copy.copy(midcolor)
                    self.segments[segindex+1].left_color = copy.copy(midcolor)
            else:
                # just a left-hand neighbor, let that take over
                self.segments[segindex-1].right = 1.0
                if smooth:
                    self.segments[segindex-1].right_color = \
                        copy.copy(self.segments[segindex].right_color)
                    
                self.segments[segindex-1].center()
        else:
            # we must have a later segment
            self.segments[segindex+1].left=0.0
            if smooth:
                self.segments[segindex+1].left_color = \
                    copy.copy(self.segments[segindex].left_color)
            self.segments[segindex+1].center()
            
        self.segments.pop(segindex)
        
    def clamp(self,a,min,max):
        if a > max:
            return max
        elif a < min:
            return min
        else:
            return a
        
    def set_left(self,i,pos):
        # set left end of segment i to pos, if possible
        if i < 0 or i >= len(self.segments):
            raise IndexError("No such segment")

        if i == 0:
            # can't move left-hand end of entire gradient
            return 0.0
        else:
            pos = self.clamp(pos,
                             self.segments[i-1].mid + Segment.EPSILON,
                             self.segments[i].mid - Segment.EPSILON)
            self.segments[i-1].right = self.segments[i].left = pos
            return pos

    def set_right(self,i,pos):
        # set left end of segment i to pos, if possible
        if i < 0 or i >= len(self.segments):
            raise IndexError("No such segment")

        max = len(self.segments)-1
        if i == max:
            # can't move right-hand end of entire gradient
            return 1.0
        else:
            pos = self.clamp(pos,
                             self.segments[i].mid + Segment.EPSILON,
                             self.segments[i+1].mid - Segment.EPSILON)
                             
            self.segments[i+1].left = self.segments[i].right = pos
            return pos

    def set_middle(self,i,pos):
        # set middle of segment i to pos, if possible
        if i < 0 or i >= len(self.segments):
            raise IndexError("No such segment")

        pos = self.clamp(pos,
                         self.segments[i].left + Segment.EPSILON,
                         self.segments[i].right - Segment.EPSILON)
                             
        self.segments[i].mid = pos
        return pos
        
    def broken_move(self, handle, move):
        seg, side = self.getSegFromHandle(handle)
        segindex = self.segments.index(seg)
        
        if (segindex > 0 or side == 'right') and (segindex < len(self.segments)-1 or side == 'left'):
            if side == 'left':
                self.segments[segindex-1].right.pos+=move
                if self.segments[segindex-1].right.pos > 1:
                    self.segments[segindex-1].right.pos = 1
                elif self.segments[segindex-1].right.pos < 0:
                    self.segments[segindex-1].right.pos = 0
                        
                seg.left.pos+=move
                if seg.left.pos > 1:
                    seg.left.pos =1
                elif seg.left.pos < 0:
                    seg.left.pos =0
                    
                if seg.left.pos > seg.right.pos:
                    seg.left.pos = seg.right.pos
                    self.segments[segindex-1].right.pos=seg.right.pos
                elif self.segments[segindex-1].right.pos < self.segments[segindex-1].left.pos:
                    self.segments[segindex-1].right.pos=self.segments[segindex-1].left.pos
                    seg.left.pos=self.segments[segindex-1].left.pos
            else:
                self.segments[segindex+1].left.pos+=move
                if self.segments[segindex+1].left.pos > 1:
                    self.segments[segindex+1].left.pos = 1
                elif self.segments[segindex+1].left.pos < 0:
                    self.segments[segindex+1].left.pos = 0
                    
                seg.right.pos+=move
                if seg.right.pos > 1:
                    seg.right.pos =1
                elif seg.right.pos < 0:
                    seg.right.pos =0
                    
                if seg.left.pos > seg.right.pos:
                    seg.right.pos=seg.left.pos
                    self.segments[segindex+1].left.pos=seg.left.pos
                elif self.segments[segindex+1].right.pos < self.segments[segindex+1].left.pos:
                    self.segments[segindex+1].left.pos=self.segments[segindex+1].right.pos
                    seg.right.pos=self.segments[segindex+1].right.pos

# These two are adapted from the algorithms at
# http://www.cs.rit.edu/~ncs/color/t_convert.html
def RGBtoHSV(rgb):
    hsv = [0,0,0,rgb[3]]
    trgb = rgb[0:3]
    trgb.sort()
    
    min = trgb[0]
    max = trgb[2]

    delta = float(max - min)
    hsv[2] = max

    if delta == 0:
        # r = g = b = 0        # s = 0, v is undefined
        hsv[1] = 0
        hsv[0] = -1
    else:
        hsv[1]=delta / max
        
        if rgb[0] == max:
            hsv[0] = (rgb[1] - rgb[2]) / delta        # between yellow & magenta
        elif rgb[1] == max:
            hsv[0] = 2 + (rgb[2] - rgb[0] ) / delta    # between cyan & yellow
        else:
            hsv[0] = 4 + (rgb[0] - rgb[1] ) / delta    # between magenta & cyan

    hsv[0] *= 60                # degrees
    if hsv[0] < 0:
        hsv[0] += 360
        
    return hsv

def HSVtoRGB(hsv):
    rgb=[0,0,0,hsv[3]] # pass through alpha channel
    
    hsv[0]/=60
    
    if hsv[1] == 0:
        return [hsv[2],hsv[2],hsv[2]]
    
    i = int(hsv[0])
    f = hsv[0] - i                            #Decimal bit of hue
    p = hsv[2] * (1 - hsv[1])
    q = hsv[2] * (1 - hsv[1] * f)
    t = hsv[2] * (1 - hsv[1] * (1 - f))
    
    if i == 0:
        rgb[0] = hsv[2]
        rgb[1] = t
        rgb[2] = p
    elif i == 1:
        rgb[0] = q
        rgb[1] = hsv[2]
        rgb[2] = p
    elif i == 2:
        rgb[0] = p
        rgb[1] = hsv[2]
        rgb[2] = t
    elif i == 3:
        rgb[0] = p
        rgb[1] = q
        rgb[2] = hsv[2]
    elif i == 4:
        rgb[0] = t
        rgb[1] = p
        rgb[2] = hsv[2]
    elif i == 5:
        rgb[0] = hsv[2]
        rgb[1] = p
        rgb[2] = q
    
    return rgb        
