# Abstract Syntax Tree produced by parser

class Node:
    def __init__(self,type,children=None,leaf=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf
         
    def __str__(self):
        return "[%s : %s]" % (self.type , self.leaf)
    
    def pretty(self,depth=0):
        str = " " * depth + "[%s : %s" % (self.type , self.leaf)
        if self.children:
            str += "\n"
            for child in self.children:
                if isinstance(child,Node):
                    str += child.pretty(depth+1) + "\n"
                else:
                    str += " " * (depth+1) + ("<<%s>>\n" % child)
            str += " " * depth + "]\n"
        else:
            str += "]"
        return str

# shorthand named ctors for specific node types
def Number(n):
    return Node("const", None, n)

def Binop(op, left, right):
    return Node("binop", [left, right], op)

def ID(id):
    return Node("id", None, id)

def Mag(exp):
    return Node("unop", [exp], "mag")

def Neg(exp):
    return Node("unop", [exp], "neg")

def Funcall(id,arglist):
    return Node("funcall", arglist, id)

def Assign(id,exp):
    return Node("assign", [exp], id)

def Decl(type, id, exp=None):
    if exp == None:
        l = None
    else:
        l = [exp]
    return Node("decl", l , (id,type))

def Stmlist(id, list):
    return Node("stmlist", list, id)

def Empty():
    return Node("empty", None, "")

def Formula(id, stmlist):
    return Node("formula", stmlist, id)

def Param(id,settinglist,type):
    return Node("param", settinglist, (id,type))

def Error():
    return Node("parser error", None, "oops")
