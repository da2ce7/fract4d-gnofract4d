#!/usr/bin/env python

# functions to tidy up ir trees in various ways


import ir
import symbol

class T:
    def __init__(self,symbols):
        self.symbols = symbols

    def stms(self, eseq):
        return eseq.children[:-1]
    
    def linearize(self,tree):
        ''' remove all ESeq nodes and move Calls to top-level'''
        if tree == None:
            pass
        elif isinstance(tree, ir.Binop):
            tree.children = self.linearize_list(tree.children)
            if isinstance(tree.children[0], ir.ESeq):
                # binop(eseq[...,e1],e2) => eseq([...,binop(e1,e2)])
                eseq = tree.children[0]
                stms = self.stms(eseq)
                e1 = eseq.children[-1]
                tree.children[0] = e1
                eseq.children = stms + [tree]
                tree = eseq
            elif isinstance(tree.children[1],ir.ESeq):
                #binop(e1,eseq(stms,e2))
                # => eseq([stms,binop(e1,e2)]) IF commutes(e1,srms)
                # => eseq(move(temp(t),e1), eseq(stms,binop(t, e2)) otherwise
                
                eseq = tree.children[1]
                e1 = tree.children[0]
                e2 = eseq.children[-1]
                stms = self.stms(eseq)
                if commutes(e1,stms):
                    tree.children[1] = e2
                    eseq.children = stms + [tree]
                    tree = eseq
                else:
                    t = ir.Var(self.symbols.newTemp(e1.datatype), e1.node, e1.datatype)
                    move = ir.Move(t ,e1, e1.node,e1.datatype)
                    tree.children[0] = t
                    tree.children[1] = e2
                    eseq.children = stms + [tree]
                    tree = ir.ESeq([move],eseq, tree.node, tree.datatype)
            else:
                pass
        else:
            pass
    
        return tree

    def linearize_list(self,l):
        return map(self.linearize,l)

def commutes(t1,t2):
    '''true iff it doesn\'t matter which of t1 and t2 is done first'''
    # t1, t2 may be lists
    if isinstance(t1,ir.Const) or isinstance(t2,ir.Const):
        # constants always commute
        return 1
    return 0

