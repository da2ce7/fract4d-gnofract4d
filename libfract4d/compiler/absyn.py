# Abstract Syntax Tree produced by parser

#from __future__ import generators
import types
import string
import fracttypes

class Node:
    def __init__(self,type,children=None,leaf=None,datatype=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf
         self.datatype = datatype
         
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
            str += " " * depth + "]" 
        else:
            str += "]"
        return str
    
    def __iter__(self):
        return NodeIter(self)

    def DeepCmp(self,other):
        if self.type < other.type: return -1
        if self.type > other.type: return 1

        if self.leaf < other.leaf: return -1
        if self.leaf > other.leaf: return 1
        
        #if len(self.children) < len(other.children): return -1
        #if len(self.children) > len(other.children): return 1

        if not self.children and not other.children: return 0
        
        for (child, otherchild) in zip(self.children,other.children):
            eql = child.DeepCmp(otherchild)
            if eql: return eql
        return eql

# def preorder(t):
#     if t:
#         print "pre",t
#         yield t
#         for child in t.children:
#             print "prechild", child
#             preorder(child)

class NodeIter:
    def __init__(self,node):
        self.nodestack = [(node,-1)]
        
    def __iter__(self):
        return self

    def getNode(self,node,child):
        if child == -1:
            return node
        else:
            return node.children[child]
        
    def next(self):
        #print map(lambda (n,x) :"%s %s" % (n,x), self.nodestack)
        if self.nodestack == []:
            raise StopIteration

        (node,child) = self.nodestack.pop()
        ret = self.getNode(node,child)
        child+= 1
        while len(node.children) <= child:
            if self.nodestack == []:
                return ret
            (node,child) = self.nodestack.pop()
            
        self.nodestack.append((node,child+1))
        self.nodestack.append((node.children[child],-1))                
        
        return ret
    
def CheckTree(tree, nullOK=0):
    if nullOK and tree == None:
        return 1
    if not isinstance(tree,Node):
        raise Exception, "bad node type %s" % tree
    if tree.children:
        if not isinstance(tree.children, types.ListType):
            raise Exception, ("children not a list: %s instead" % tree.children)
        for child in tree.children:
            CheckTree(child,0)
    return 1

# shorthand named ctors for specific node types
def Formlist(list):
    return Node("formlist", list, "")

def Set(id,s):
    return Node("set",s,id)

def Number(n):
    return Node("const", None, n)

def Const(n):
    return Node("const", None, n=="true")

def Complex(left,right):
    return Node("complex",[left, right], "")

def Binop(op, left, right):
    return Node("binop", [left, right], op)

def ID(id):
    return Node("id", None, id)

def Mag(exp):
    return Node("unop", [exp], "mag")

def String(s,list):
    return Node("string", list, s)

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
    return Node("decl", l , id, fracttypes.typeOfStr(type))

def Stmlist(id, list):
    return Node("stmlist", list, id)

def Setlist(id, list):
    return Node("setlist", list, id)

def Empty():
    return Node("empty", None, "")

def Formula(id, stmlist):
    return Node("formula", stmlist, id)

def Param(id,settinglist,type):
    return Node("param", settinglist, id, fracttypes.typeOfStr(type))

def Func(id,settinglist,type):
    return Node("func", settinglist, id, fracttypes.typeOfStr(type))

def Heading(settinglist):
    return Node("heading", settinglist)

def Repeat(body,test):
    return Node("repeat", [test, Stmlist("",body)], "")

def While(test,body):
    return Node("while", [test, Stmlist("", body)], "")

def If(test, left, right):
    return Node("if",
                [test, Stmlist("",left), Stmlist("",right)], "")

def InternalError():
    return Node("parser error", None, "oops")

def Error2(str, lineno):
    if str == "$":
        return Node("error", None,
                "Syntax error: $ifdef/$define not supported on line %d" % lineno)
    return Node("error", None,
                "Syntax error: unexpected '%s' on line %d" % (str,lineno))

def Error(type, value, lineno):
    # get complaints about NEWLINE tokens on right line
    if type == "NEWLINE":
        lineno -= 1
        return Node("error", None,
                    "Syntax error: unexpected newline on line %d" % lineno)

    if type == "LARRAY" or type == "RARRAY":
        return Node("error", None,
                    "Syntax error: arrays are not supported (line %d)" % lineno)
    
    return Node("error", None, "Syntax error: unexpected %s '%s' on line %d" %
                (string.lower(type), value, lineno))


