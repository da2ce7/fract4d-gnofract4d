#!/usr/bin/env python

# Translate an abstract syntax tree into tree-structured intermediate
# code, performing type checking as a side effect
from absyn import *
import symbol
import fractparser
import fractlexer
import ir
import canon
import stdlib

from fracttypes import *
    
class T:
    def __init__(self,f,dump=None):
        self.symbols = symbol.T()
        self.canon = canon.T(self.symbols,dump)
        self.errors = []
        self.warnings = []
        self.sections = {}
        self.canon_sections = {}
        self.output_sections = {}
        self.fakeNode = Empty(-1) # node used for code not written by user
        
        self.dumpCanon = 0
        self.dumpDecorated = 0
        self.dumpProbs = 0
        self.dumpTranslation = 0
        self.dumpVars = 0
        self.dumpPreCanon = 0
        
        if dump != None:
            for k in dump.keys():
                self.__dict__[k]=1

        try:
            self.formula(f)
            if self.dumpPreCanon:
                self.dumpSections(f,self.sections)
            self.canonicalize()
        except TranslationError, e:
            self.errors.append(e.msg)

        if self.dumpProbs:
            print self.errors
            print self.warnings
            
        if self.dumpDecorated:
            print f.pretty()

        if self.dumpVars:
            for (name,sym) in self.symbols.items():
                if self.symbols.is_user(name):
                    try:
                        print name,": ",sym
                    except Exception, err:
                        print "Error \"%s\" dumping %s" %(err,name)

        if self.dumpTranslation:
            print self.dumpSections(f,self.canon_sections)

    def dumpSections(self,f,dict):
        print f.leaf + "{"
        for (name,tree) in dict.items():
            if isinstance(tree,ir.T):
                print " " + name + "("
                print tree.pretty(2) + " )"
            elif isinstance(tree,types.ListType):
                print " " + name + "("
                for t in tree:
                    print t.pretty(2)
                print " )"
            elif tree == None:
                pass
            else:
                print "Unknown tree %s in section %s" % (tree, name)
        print "}\n"

    def pretty(self):
        if self.errors:
            return string.join(self.errors,"\n")
        out = []
        for (name,tree) in self.sections.items():
            if isinstance(tree,ir.T):
                out.append( " " + name + "(")
                out.append(tree.pretty(2) + " )")
            elif isinstance(tree,types.ListType):
                out.append(" " + name + "(")
                for t in tree:
                    out.append(t.pretty(2))
                out.append(" )")
            elif tree == None:
                pass
            else:
                out.append("Unknown tree %s in section %s" % (tree, name))
        return string.join(out,"\n")
    
    def error(self,msg):
        self.errors.append(msg)
    def warning(self,msg):
        self.warnings.append(msg)
    
    def formula(self, f):
        self.symbols.reset()
        if f.children[0].type == "error":
            self.error(f.children[0].leaf)
            return

        self.canonicalizeSections(f)
        
        # lookup sections in order
        s = f.childByName("default")
        if s: self.default(s)
        s = f.childByName("global")
        if s: self.global_(s)
        s = f.childByName("init")
        if s: self.init(s)
        s = f.childByName("loop")
        if s: self.loop(s)
        s = f.childByName("bailout")
        if s: self.bailout(s)
        #  ignore switch and builtin for now

    def canonicalize(self):
        for (k,tree) in self.sections.items():
            startLabel = "t__start_" + k
            endLabel = "t__end_" + k
            self.canon_sections[k] = self.canon.canonicalize(tree,startLabel,endLabel)

    def dupSectionWarning(self,sect):
        self.warning(
                    "formula contains a fractint-style implicit %s section\
                    and an explicit UltraFractal %s section. \
                    Using explicit section." % (sect,sect))
        
    def canonicalizeSections(self,f):        
        '''a nameless section (started by ':') is the same as a loop
           section with the last stm as a bailout section - make this
           change'''

        # a "nameless" section is really an init section
        s = f.childByName("nameless")
        if s:
            oldinit = f.childByName("init")
            if oldinit:
                self.dupSectionWarning("init")
            else:
                s.leaf = "init"
        
        s = f.childByName("")
        if not s or s.children == []:
            return
        elif len(s.children) == 1:
            self.warning("No bailout condition specified")
            bailout = []
            loop = s.children
        else:
            bailout = [s.children[-1]]
            loop = s.children[:-1]
            
        oldbailout = f.childByName("bailout")
        if oldbailout:
            self.dupSectionWarning("bailout")
        else:
            f.children.append(Stmlist("bailout",bailout, -1))
        
        oldloop = f.childByName("loop")
        if oldloop:
            self.dupSectionWarning("loop")
        else:
            f.children.append(Stmlist("loop",loop,loop[0].pos))

        f.children.remove(s)

        if self.dumpCanon:
            print f.pretty()

    def sectionOrNone(self,sectname):
        if self.sections.has_key(sectname):
            return self.sections[sectname]
        return None
    
    def default(self,node):
        self.sections["default"] = 1

    def global_(self,node):
        self.sections["global"] = self.stmlist(node)

    def stmlist(self, node):
        children = filter(lambda c : c.type != "empty", node.children)
        seq = ir.Seq(map(lambda c: self.stm(c), children), node)
        return seq

    def stmlist_with_label(self, node, label):        
        seq = self.stmlist(node)
        seq.children.insert(0, label)
        return seq
    
    def stm(self,node):
        if node.type == "decl":
            r = self.decl(node)
        elif node.type == "assign":
            r = self.assign(node)
        elif node.type == "if":
            r = self.if_(node)
        else:
            r = self.exp(node)
        return r

    def isCompare(self,node):
        op = node.leaf
        return node.type == "binop" and \
               (op == ">" or op == ">=" or op == "<" or op == "<=" or \
                op == "==" or op == "!=")

    def isShortcut(self,node):
        op = node.leaf
        return node.type == "binop" and (op == '&&' or op == '||')

    def newLabel(self,node):
        return ir.Label(self.symbols.newLabel(),node)

    def newTemp(self, node):
        return ir.Var(self.symbols.newTemp(node.datatype),node, node.datatype)
    
    def makeCompare(self,node):
        'convert a node into a comparison op'
        if not self.isCompare(node):
            # insert a "fake" comparison to zero
            node = Binop('!=', node, Const(0,node.pos), node.pos)
        return node
    
    def if_(self,node):
        '''the result of an if is:
        seq(
            cjump(test,falseDest,trueDest)
            seq(label(trueDest), trueCode, jump end)
            seq(label(falseDest), falseCode)
            label(end)
        )'''
        
        trueDest = self.newLabel(node)
        falseDest = self.newLabel(node)
        doneDest = self.newLabel(node)

        node.children[0] = self.makeCompare(node.children[0])
        
        # convert boolean operation
        children = map(lambda n : self.exp(n) , node.children[0].children)
        op = self.findOp(node.children[0],children)
        convertedChildren = self.coerceList(op.args,children)

        # convert blocks of code we jump to
        trueBlock = self.stmlist_with_label(node.children[1],trueDest)
        trueBlock.children.append(ir.Jump(doneDest.name, node))

        falseBlock = self.stmlist_with_label(node.children[2], falseDest)
        
        # construct actual if operation
        test = ir.CJump(node.children[0].leaf,
                         convertedChildren[0],
                         convertedChildren[1],
                         trueDest.name, falseDest.name, node)

        # overall code
        ifstm = ir.Seq([test,trueBlock,falseBlock,doneDest],node)
        return ifstm
        
    def assign(self, node):
        '''assign a new value to a variable, creating it if required'''
        lvalue = node.children[0]
        lhs = expectedType = None
        if lvalue.type == "id":
            name = lvalue.leaf
            if not self.symbols.has_key(name):
                # implicitly create a new var - a warning?
                self.symbols[name] = \
                    Var(Complex,default_value(Complex),lvalue.pos)

            expectedType = self.symbols[name].type
            lhs = ir.Var(name, node, expectedType)
            
        elif lvalue.type == "funcall":
            lhs = self.funcall(lvalue)
            expectedType = lhs.datatype
        else:
            self.error("Internal Compiler Error: bad lvalue %s for assign on %d:"\
                       % (lvalue.type, node.pos))
        rhs = self.exp(node.children[1])

        return ir.Move(lhs,self.coerce(rhs,expectedType),node,expectedType)

    def findOp(self, opnode, list):
        ' find the most appropriate overload for this op'
        try:
            overloadList = self.symbols[opnode.leaf]
        except KeyError:
            if opnode.leaf[0] == "@":
                # an attempt to call an undeclared parameter function,
                # create it now. Point to ident by default
                overloadList = self.symbols[opnode.leaf] = [
                    Func([Complex],Complex,stdlib,"ident")]
            else:
                raise
        
        typelist = map(lambda ir : ir.datatype , list)
        for ol in overloadList:
            if ol.matchesArgs(typelist):
                return ol
        raise TranslationError(
            "Invalid argument types %s for %s on line %s" % \
            (typelist, opnode.leaf, opnode.pos))
            
    def decl(self,node):
        if node.children:
            exp = self.stm(node.children[0])
        else:
            # default initializer
            exp = ir.Const(fracttypes.default_value(node.datatype),
                           node, node.datatype)

        try:
            self.symbols[node.leaf] = Var(node.datatype,
                                          default_value(node.datatype), node.pos)
            return ir.Move(
                ir.Var(node.leaf, node, node.datatype),                
                self.coerce(exp, node.datatype),
                node, node.datatype)
        
        except KeyError, e:
            self.error("Invalid declaration on line %d: %s" % (node.pos,e))

    def exp(self,node):
        if node.type == "const":
            r = self.const(node)
        elif node.type == "id":
            r = self.id(node)
        elif node.type == "binop":
            r = self.binop(node)
        elif node.type == "unop":
            r = self.unop(node)
        elif node.type == "funcall":
            r = self.funcall(node)
        elif node.type == "assign":
            r = self.assign(node)
        else:
            self.badNode(node,"exp")

        return r

    def seq_with_label(self,stm,label, node):
        return ir.Seq([label, stm], node)

    def unop(self, node):
        children = map(lambda n: self.exp(n) , node.children)
        op = self.findOp(node,children)
        children = self.coerceList(op.args,children)
        return ir.Unop(node.leaf, children, node, op.ret)

    def funcall(self, node):
        children = map(lambda n: self.exp(n) , node.children)
        try:
            op = self.findOp(node, children)
        except KeyError, err:
            raise TranslationError(
                "Unknown function %s on line %d" % (node.leaf,node.pos))
                       
        children = self.coerceList(op.args,children)
        return ir.Call(node.leaf, children, node, op.ret)
    
    def shortcut(self, node):
        # convert into an if-expression
        trueDest = self.newLabel(node)
        falseDest = self.newLabel(node)
        doneDest = self.newLabel(node)
        
        node.children[0] = self.makeCompare(node.children[0])

        children = map(lambda n : self.exp(n) , node.children)        
        op = self.findOp(node,children)
        children = self.coerceList(op.args,children)

        temp = ir.Var(self.symbols.newTemp(Bool),node, Bool)
        
        # a && b = eseq(if(a) then t = (bool)b else t = false; t)
        #        = eseq(cjump(==,a,0,td,fd),
        #               lab(td),move(t,b),jmp(end),
        #               lab(fd),move(t,0),jmp(end),
        #               lab(end), t)
        if node.leaf == "&&":
            # code to calc B and store in temp
            trueBlock = ir.Seq(
                [trueDest, ir.Move(temp, children[1],node, children[1].datatype),
                 ir.Jump(doneDest.name, node)], node)
            
            # code to set temp to false
            falseBlock = ir.Seq(
                [falseDest,
                 ir.Move(temp, ir.Const(0,node,Bool),node, Bool),
                 ir.Jump(doneDest.name, node)], node)
            
        else:
            # a || b = eseq(if(a) then t = true else t = (bool)b; t)

            # code to set temp to true
            trueBlock = ir.Seq(
                [trueDest,
                 ir.Move(temp, ir.Const(1,node,Bool),node, Bool),
                 ir.Jump(doneDest.name, node)], node)

            # set temp to (bool)b
            falseBlock = ir.Seq(
                [falseDest,
                 ir.Move(temp, children[1],node, children[1].datatype),
                 ir.Jump(doneDest.name, node)], node)
            
        # construct actual if operation
        test = ir.CJump(children[0].op,
                        children[0].children[0],
                        children[0].children[1],
                        trueDest.name, falseDest.name, node)
        
        r = ir.ESeq([test, trueBlock, falseBlock, doneDest],
                    temp, node, op.ret)
        return r
        
    def binop(self, node):
        if self.isShortcut(node):
            return self.shortcut(node)
        else:
            children = map(lambda n : self.exp(n) , node.children)        
            op = self.findOp(node,children)
            children = self.coerceList(op.args,children)

            return ir.Binop(node.leaf,
                            children,
                            node,op.ret)
    
    def id(self, node):
        try:
            node.datatype = self.symbols[node.leaf].type
        except KeyError, e:
            self.warning(
                "Uninitialized variable %s referenced on line %d" % \
                (node.leaf, node.pos))
            self.symbols[node.leaf] = Var(
                fracttypes.Complex, default_value(Complex), node.pos)
            node.datatype = fracttypes.Complex

        return ir.Var(node.leaf, node, node.datatype)
        
    def const(self,node):
        return ir.Const(node.leaf, node, node.datatype)        

    def coerceList(self,expList,typeList):
        return map( lambda (exp,ty) : self.coerce(exp,ty) ,
                    zip(typeList, expList))
    
    def coerce(self, exp, expectedType):
        '''insert code to cast exp to expectedType 
           or produce an error if conversion is not permitted'''

        #if exp.datatype == None or expectedType == None:
        #    raise TranslationError("Internal Compiler Error: coercing an untyped node")
        if exp.datatype == expectedType:
            return exp

        if fracttypes.canBeCast(exp.datatype, expectedType):
            self.warnCast(exp, expectedType)
            return ir.Cast(exp, exp.node, expectedType)
        else:
            self.badCast(exp,expectedType)
            
    def init(self,node):
        self.sections["init"] = self.stmlist(node)

    def loop(self, node):
        self.sections["loop"] = self.stmlist(node)

    def bailout(self,node):
        # ensure that last stm is a book
        bailList = self.stmlist(node)
        try:
            bailList.children[-1] = self.coerce(bailList.children[-1],Bool)
            self.sections["bailout"] = bailList
        except IndexError:
            self.warnings.append("No bailout expression found. Calculation will never terminate.")

    def badNode(self, node, rule):
        msg = "Internal Compiler Error: Unexpected node '%s' in %s" % \
            (node.type, rule)
        raise TranslationError(msg)

    def badCast(self, exp, expectedType):
        raise TranslationError(
           ("invalid type %s for %s on line %s, expecting %s" %
            (strOfType(exp.datatype), exp.node.leaf, exp.node.pos, strOfType(expectedType))))
    def warnCast(self,exp,expectedType):
        msg = "Warning: conversion from %s to %s on line %s" % \
        (strOfType(exp.datatype), strOfType(expectedType), exp.node.pos)
        self.warnings.append(msg)
        
parser = fractparser.parser
     
# debugging
if __name__ == '__main__':
    import sys
    
    for arg in sys.argv[1:]:
        s = open(arg,"r").read() # read in a whole file
        result = parser.parse(s)
        for formula in result.children:
            t = T(formula)
            if t.errors != []:
                print "Errors translating %s:" % formula.leaf
                for e in t.errors:
                    print "\t",e
