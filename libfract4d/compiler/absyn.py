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
               str += child.pretty(depth+1) + "\n"
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
