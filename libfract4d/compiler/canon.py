#!/usr/bin/env python

# functions to tidy up a ir trees in various ways


import ir

def linearize(tree):
    ''' remove all ESeq nodes and move Calls to top-level'''
    if tree == None:
        pass
    elif isinstance(tree, ir.Binop):
        if isinstance(tree.children[0], ir.ESeq):
            # binop(eseq[...,e1],e2) => eseq([...,binop(e1,e2)])
            stms = tree.children[0].children[0:-1]
            e1 = tree.children[0].children[-1]
            eseq = tree.children[0]
            tree.children[0] = e1
            eseq.children = stms + [tree]
            tree = linearize(eseq)
        elif isinstance(tree.children[1],ir.ESeq):
            #binop(e1,eseq(stms,e2)) => eseq(move(temp(),e1), eseq(stms,binop(t, e2))
            pass
    else:
        pass
    
    return tree

