# generally useful funcs for reading in .fct files

import string

class T:
    def __init__(self,parent=None):
        self.endsect = "[endsection]"
        self.tr = string.maketrans("[] ","___")
        self.parent = parent
        
    def warn(self,msg):
        if self.parent:
            self.parent.warn(msg)
            
    def parseVal(self,name,val,f,sect=""):
        # when reading in a name/value pair, we try to find a method
        # somewhere in the hierarchy of current class called parse_name
        # then call that
        methname = "parse_" + sect + name.translate(self.tr)
        meth = None

        klass = self.__class__
        while True:
            meth = klass.__dict__.get(methname)
            if meth != None:
                break
            bases = klass.__bases__
            if len(bases) > 0:                    
                klass = bases[0]
            else:
                break
            
        if meth:
            return meth(self,val,f)
        else:
            self.warn("ignoring unknown attribute %s" % methname)
            
    def nameval(self,line):
        x = line.rstrip().split("=",1)
        if len(x) == 0: return (None,None)
        if len(x) < 2:
            val = None
        else:
            val = x[1]
        return (x[0],val)

class ParamBag(T):
    "A class for reading in and holding a bag of name-value pairs"
    def __init__(self):
        T.__init__(self)
        self.dict = {}

    def parseVal(self,name,val,f,sect=""):
        self.dict[sect + name] = val

    def load(self,f):
        encoded = False
        line = f.readline()
        while line != "":
            if line[:2]=="::":
                # start of an encoded block
                line = line[2:]
                
            (name,val) = self.nameval(line)
            if name != None:
                if name == self.endsect:
                    break
                
                if val == "[":
                    # start of a multi-line parameter
                    line = f.readline()
                    vals = []
                    while line != "" and line.rstrip() != "]":
                        vals.append(line)
                        line = f.readline()
                    val = "".join(vals)

                self.parseVal(name,val,f)

            line = f.readline()

