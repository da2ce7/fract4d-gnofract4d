# A persistent cache of pre-compiled formulas

import os
import stat
import cPickle
import md5

class TimeStampedObject:
    "An object and the last time it was updated"
    def __init__(self,obj,time,file=None):
        self.time = time
        self.obj = obj
        self.cache_file = file
        
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

    def hashcode(self,s,*extras):
        hash = md5.new(s)
        for x in extras:
            hash.update(x)

        return hash.hexdigest()

    def makePickleName(self,s,*extras):
        name = self.hashcode(s,*extras) +".pkl"
        fullname = os.path.join(self.dir, name)
        return fullname
    
    def createPickledFile(self,file,contents):
        f = open(file,"wb")
        try:
            cPickle.dump(contents,f,True)
        finally:
            f.close()
        
    def getcontents(self,file,parser):
        mtime = os.stat(file)[stat.ST_MTIME]

        tso = self.files.get(file,None)
        if tso:            
            if tso.time == mtime:
                return tso.obj
        
        val = parser(open(file))

        hashname = self.makePickleName(file)
        self.createPickledFile(hashname,val)
        self.files[file] = TimeStampedObject(val,mtime,hashname)
        
        return val
    
