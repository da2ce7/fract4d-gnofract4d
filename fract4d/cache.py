# A persistent cache of pre-compiled formulas

import os
import stat
import cPickle

class TimeStampedObject:
    "An object and the last time it was updated"
    def __init__(self,obj,time):
        self.time = time
        self.obj = obj
        
class T:
    def __init__(self,dir="~/.gnofract4d-cache"):
        self.dir = os.path.expanduser(dir)
        self.files = {}
        
    def init(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def clear(self):
        for f in os.listdir(self.dir):
            os.remove(os.path.join(self.dir,f))

    def makefilename(self,name,ext):
        return os.path.join(self.dir, "fract4d_%s%s" % (name, ext))

    def getcontents(self,file,parser):
        mtime = os.stat(file)[stat.ST_MTIME]

        tso = self.files.get(file,None)
        if tso:            
            if tso.time == mtime:
                return tso.obj
        
        val = parser(open(file))
        cPickle.dumps(val,True)
        self.files[file] = TimeStampedObject(val,mtime)
        return val
    
