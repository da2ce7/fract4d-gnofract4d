#!/usr/bin/env python

# functions to tidy up ir trees in various ways


import ir
import symbol
import copy

class T:
    def __init__(self,symbols):
        self.symbols = symbols

    def stms(self, eseq):
        return eseq.children[:-1]
    
    def linearize(self,tree):
        ''' remove all ESeq nodes and move Calls to top-level'''
        if tree == None:
            return None
        
        if tree.children == None:
            children = None
        else:
            children = self.linearize_list(tree.children)
            
        if isinstance(tree, ir.Binop):
            if isinstance(children[0], ir.ESeq):
                # binop(eseq[stms,e1],e2) => eseq([stms,binop(e1,e2)])
                eseq = children[0]
                stms = self.stms(eseq)
                e1 = eseq.children[-1]
                assert(not isinstance(e1, ir.ESeq))
                e2 = children[1]
                newtree = ir.ESeq(stms,
                                  ir.Binop(tree.op,[e1,e2],tree.node, tree.datatype),
                                  eseq.node, eseq.datatype)
                newtree = self.linearize(newtree)
            elif isinstance(children[1],ir.ESeq):
                #binop(e1,eseq(stms,e2))
                # => eseq([stms,binop(e1,e2)]) IF commutes(e1,stms)
                # => eseq(move(temp(t),e1), eseq(stms,binop(t, e2)) otherwise
                eseq = children[1]
                e1 = children[0]
                e2 = eseq.children[-1]
                stms = self.stms(eseq)
                if commutes(e1,stms):
                    newtree = ir.ESeq(stms,
                                      ir.Binop(tree.op,[e1,e2],tree.node, tree.datatype),
                                      eseq.node, eseq.datatype)
                    newtree = self.linearize(newtree)
                else:
                    t = ir.Var(self.symbols.newTemp(e1.datatype), e1.node, e1.datatype)
                    move = ir.Move(t ,e1, e1.node,e1.datatype)
                    binop = ir.Binop(tree.op, [t,e2], tree.node, tree.datatype)
                    eseq = ir.ESeq(stms, binop, eseq.node, eseq.datatype)
                    newtree = ir.ESeq([move],eseq, tree.node, tree.datatype)
                    newtree = self.linearize(newtree)
            else:
                newtree = ir.Binop(tree.op,children,tree.node,tree.datatype)
        elif isinstance(tree, ir.CJump):
            if isinstance(children[0], ir.ESeq):
                # cjump(eseq[stms,e1],e2) => seq([stms,cjump(e1,e2)])
                eseq = children[0]
                stms = self.stms(eseq)
                e1 = eseq.children[-1]
                assert(not isinstance(e1, ir.ESeq))
                e2 = children[1]
                newtree = ir.Seq(stms + [ir.CJump(tree.op,e1,e2,
                                                 tree.trueDest, tree.falseDest,
                                                 tree.node)], 
                                 eseq.node)
                newtree = self.linearize(newtree)
            elif isinstance(children[1],ir.ESeq):
                #cjump(e1,eseq(stms,e2))
                # => seq([stms,cjump(e1,e2)]) IF commutes(e1,stms)
                # => seq(move(temp(t),e1), seq(stms,cjump(t, e2)) otherwise
                eseq = children[1]
                e1 = children[0]
                e2 = eseq.children[-1]
                stms = self.stms(eseq)
                if commutes(e1,stms):
                    newtree = ir.Seq(stms + \
                                     [ir.CJump(tree.op,e1,e2,
                                               tree.trueDest, tree.falseDest,
                                               tree.node)],
                                     eseq.node)
                    newtree = self.linearize(newtree)
                else:
                    t = ir.Var(self.symbols.newTemp(e1.datatype), e1.node, e1.datatype)
                    move = ir.Move(t ,e1, e1.node,e1.datatype)
                    cjump = ir.CJump(tree.op, t,e2,
                                     tree.trueDest, tree.falseDest, tree.node)
                    newtree = ir.Seq([move]+ stms + [cjump], tree.node)
                    newtree = self.linearize(newtree)
            else:
                newtree = copy.copy(tree)
                newtree.children = children
                
        elif isinstance(tree, ir.ESeq) or isinstance(tree, ir.Seq):
            # flatten eseq trees, eg:
            #eseq(stms,eseq(stms2,e1),stms3,e2) => eseq(stms,stms2,e1,stms3,e2)
            stms = []
            for stm in children:
                if isinstance(stm,ir.ESeq) or isinstance(stm,ir.Seq):
                    stms = stms + stm.children
                else:
                    stms.append(stm)
            newtree = copy.copy(tree)
            newtree.children = stms
        elif isinstance(tree, ir.Cast):
            if isinstance(children[0],ir.ESeq):                
                # cast(eseq(stms,e)) => eseq(stms,cast(e))
                eseq = children[0]
                stms = self.stms(eseq)
                e = eseq.children[-1]
                newtree = ir.ESeq(stms,ir.Cast(e,tree.node, tree.datatype),
                                  eseq.node, tree.datatype)
            else:
                newtree = copy.copy(tree)
                newtree.children = children
        else:
            newtree = copy.copy(tree)
            newtree.children = children
            
        return newtree

    def copy_with_new_children(self,irNode,children):
        newNode = copy.copy(irNode)
        newNode.children = children
        return children
    
    def linearize_list(self,l):
        return map(self.linearize,l)

    def is_block_boundary(self, irNode):
        return self.is_jump(irNode) or isinstance(irNode, ir.Label)

    def is_jump(self, irNode):
        return isinstance(irNode, ir.Jump) or \
               isinstance(irNode, ir.CJump)
        
    def basic_blocks(self, tree, startLabel, endLabel):
        # divides tree into a list of basic blocks
        # we assume it has a Seq() at the top, and no other seqs or eseqs
        assert(isinstance(tree, ir.Seq))
        tree.children.append(ir.Label(endLabel,tree.node))
        
        blocks = []
        label = startLabel
        inBlock = 0
        block = []
        for stm in tree.children:
            if isinstance(stm, ir.Label):
                if block == []:                    
                    block.append(stm)
                else:
                    # close existing block, create a new one
                    if not self.is_jump(block[-1]):
                        # append a jump to current label
                        block.append(ir.Jump(stm.name, stm.node))
                    blocks.append(block)
                    block = [ stm ]
            else:
                if block == []:
                    # manufacture a label if first stm is not a label
                    block.append(ir.Label(label,tree.node))
                    label = self.symbols.newLabel()
                block.append(stm)
                if self.is_jump(stm):
                    blocks.append(block)
                    block = []
        return blocks
    
def commutes(t1,t2):
    '''true iff it doesn\'t matter which of t1 and t2 is done first'''
    # t1, t2 may be lists
    if isinstance(t1,ir.Const) or isinstance(t2,ir.Const):
        # constants always commute
        return 1
    return 0

