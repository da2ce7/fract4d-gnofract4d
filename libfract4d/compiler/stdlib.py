# The fractal standard library, including operators

from codegen import ComplexArg
from fracttypes import *

def reals(l):
    # [[a + ib], [c+id]] => [ a, c]
    return [x.re for x in l]

def imags(l):
    return [x.im for x in l]

def mul_cc_c(gen,t,srcs):
    # (a+ib) * (c+id) = ac - bd + i(bc + ad)
    ac = gen.emit_binop(t.op, [srcs[0].re, srcs[1].re], Float)
    bd = gen.emit_binop(t.op, [srcs[0].im, srcs[1].im], Float)
    bc = gen.emit_binop(t.op, [srcs[0].im, srcs[1].re], Float)
    ad = gen.emit_binop(t.op, [srcs[0].re, srcs[1].im], Float)
    dst = ComplexArg(
        gen.emit_binop('-', [ac, bd], Float),
        gen.emit_binop('+', [bc, ad], Float))
    return dst

def complex_ff_c(gen,t,srcs):
    # construct a complex number from two real parts
    return ComplexArg(srcs[0],srcs[1])

def add_cc_c(gen,t,srcs):
    # add 2 complex numbers
    dst = ComplexArg(
        gen.emit_binop(t.op,reals(srcs), Float),
        gen.emit_binop(t.op,imags(srcs), Float))
    return dst

# sub implemented same way as add
sub_cc_c = add_cc_c

def lt_cc_b(gen,t,srcs):    
    # compare real parts only
    return gen.emit_binop(t.op,reals(srcs), Bool)

# these comparisons implemented the same way
lte_cc_b = gt_cc_b = gte_cc_b = lt_cc_b

def eq_cc_b(gen,t,srcs):
    # compare 2 complex numbers for equality
    d1 = gen.emit_binop(t.op,reals(srcs), Bool)
    d2 = gen.emit_binop(t.op,imags(srcs), Bool)
    dst = gen.emit_binop("&&", [d1, d2], Bool)
    return dst

def noteq_cc_b(gen,t,srcs):
    # compare 2 complex numbers for inequality
    d1 = gen.emit_binop(t.op,reals(srcs), Bool)
    d2 = gen.emit_binop(t.op,imags(srcs), Bool)
    dst = gen.emit_binop("||", [d1, d2], Bool)
    return dst
