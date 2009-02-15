import fract4dc
import struct

def parse(type,buffer):
    if type == fract4dc.MESSAGE_TYPE_ITERS:
        return Iters(buffer)
    if type == fract4dc.MESSAGE_TYPE_IMAGE:
        return Image(buffer)
    if type == fract4dc.MESSAGE_TYPE_PROGRESS:
        return Progress(buffer)
    if type == fract4dc.MESSAGE_TYPE_STATUS:
        return Status(buffer)
    if type == fract4dc.MESSAGE_TYPE_TOLERANCE:
        return Tolerance(buffer)
    if type == fract4dc.MESSAGE_TYPE_STATS:
        return Stats(buffer)

class T:
    pass

class Iters(T):
    def __init__(self,buffer):
        (self.iterations,) = struct.unpack("i",buffer)

    def get_name(self):
        return "Iters"
    name = property(get_name)

    def show(self):
        return "Iters: %d" % self.iterations
        
class Image(T):
    def __init__(self,buffer):
        (self.x, self.y, self.w, self.h) = struct.unpack("4i",buffer)

    def get_name(self):
        return "Image"
    name = property(get_name)

    def show(self):
        return "Image: (%d,%d) (%d,%d)" % (self.x, self.y, self.w, self.h)
 
class Progress(T):
    def __init__(self,buffer):
        (p,) = struct.unpack("i",buffer)
        self.progress = float(p)

    def show(self):
        return "Progress: %s" % self.progress

    def get_name(self):
        return "Progress"
    name = property(get_name)


class Status(T):
    def __init__(self,buffer):
        (self.status,) = struct.unpack("i",buffer)

    def show(self):
        return "Status: %d" % self.status

    def get_name(self):
        return "Status"
    name = property(get_name)

class Tolerance(T):
    def __init__(self,buffer):
        (self.tolerance,) = struct.unpack("d",buffer)

    def get_name(self):
        return "Tolerance"
    name = property(get_name)

class Stats(T):
    def fromList(list):        
        instance = Stats()
        instance.iterations = list[0]
        instance.pixels = list[1]
        instance.pixels_calculated = list[2]
        instance.pixels_skipped = list[3]
        instance.pixels_inside = list[4]
        instance.pixels_outside = list[5]
        instance.pixels_periodic = list[6]
        return instance
    fromList = staticmethod(fromList)

    def __init__(self,buffer=None):
        if buffer:
            (self.iterations, 
             self.pixels, 
             self.pixels_calculated, 
             self.pixels_skipped,
             self.pixels_inside,
             self.pixels_outside,
             self.pixels_periodic,
             dummy,
             dummy,
             dummy,
             dummy) = struct.unpack("11L",buffer)        

    def get_name(self):
        return "Stats"
    name = property(get_name)

    def show(self):
        return (
            "Stats\n" +
            "iterations:\t%d\n" % self.iterations +
            "pixels: \t%d\n" % self.pixels +
            "in/out/per:\t%d\t%d\t%d\n" % \
                (self.pixels_inside, self.pixels_outside, self.pixels_periodic) +
            "calc/skip:\t%d\t%d\n" % (self.pixels_calculated, self.pixels_skipped))
