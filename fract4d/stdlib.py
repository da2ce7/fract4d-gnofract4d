# The fractal standard library, including operators
import math

from codegen import ComplexArg, ConstFloatArg, ConstIntArg, TempArg
from fracttypes import *

def reals(l):
    # [[a + ib], [c+id]] => [ a, c]
    return [x.re for x in l]

def imags(l):
    return [x.im for x in l]

# unary negation
def neg_i_i(gen,t,srcs):
    return gen.emit_func('-', srcs, Int)

def neg_f_f(gen,t,srcs):
    return gen.emit_func('-', srcs, Float)

def neg_c_c(gen,t,srcs):
    return ComplexArg(
        gen.emit_func('-', [srcs[0].re], Float),
        gen.emit_func('-', [srcs[0].im], Float))

# basic binary operation
def add_ff_f(gen,t,srcs):
    return gen.emit_binop(t.op,srcs,t.datatype)

# many equivalent funcs
sub_ff_f = mul_ff_f = div_ff_f = add_ff_f
add_ii_i = sub_ii_i = mul_ii_i = div_ii_i = add_ff_f
gt_ii_b = gte_ii_b = lt_ii_b = lte_ii_b = eq_ii_b = noteq_ii_b = add_ff_f
gt_ff_b = gte_ff_b = lt_ff_b = lte_ff_b = eq_ff_b = noteq_ff_b = add_ff_f

def mod_ii_i(gen,t,srcs):
    return gen.emit_binop('%%', srcs, t.datatype)

def mod_ff_f(gen,t,srcs):
    return gen.emit_func2('fmod', srcs, Float)

def mul_cc_c(gen,t,srcs):
    # (a+ib) * (c+id) = ac - bd + i(bc + ad)
    ac = gen.emit_binop('*', [srcs[0].re, srcs[1].re], Float)
    bd = gen.emit_binop('*', [srcs[0].im, srcs[1].im], Float)
    bc = gen.emit_binop('*', [srcs[0].im, srcs[1].re], Float)
    ad = gen.emit_binop('*', [srcs[0].re, srcs[1].im], Float)
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
        gen.emit_binop('+',reals(srcs), Float),
        gen.emit_binop('+',imags(srcs), Float))
    return dst

def sub_cc_c(gen,t,srcs):
    # subtract 2 complex numbers
    dst = ComplexArg(
        gen.emit_binop('-',reals(srcs), Float),
        gen.emit_binop('-',imags(srcs), Float))
    return dst

def div_cc_c(gen,t,srcs):
    # (a+ib)/(c+id) = (a+ib)*(c-id) / (c+id)*(c-id)
    # = (ac + bd + i(bc - ad))/mag(c+id)
    denom = cmag_c_f(gen,'mag', [srcs[1]])
    ac = gen.emit_binop('*', [srcs[0].re, srcs[1].re], Float)
    bd = gen.emit_binop('*', [srcs[0].im, srcs[1].im], Float)
    bc = gen.emit_binop('*', [srcs[0].im, srcs[1].re], Float)
    ad = gen.emit_binop('*', [srcs[0].re, srcs[1].im], Float)
    dre = gen.emit_binop('+', [ac, bd], Float)
    dim = gen.emit_binop('-', [bc, ad], Float)
    return ComplexArg(
        gen.emit_binop('/', [dre, denom], Float),
        gen.emit_binop('/', [dim, denom], Float))

def div_cf_c(gen,t,srcs):
    # divide a complex number by a real one
    return ComplexArg(
        gen.emit_binop(t.op,[srcs[0].re, srcs[1]], Float),
        gen.emit_binop(t.op,[srcs[0].im, srcs[1]], Float))

mul_cf_c = div_cf_c

def cmag_c_f(gen,t,srcs):
    # |x| = x_re * x_re + x_im * x_im
    src = srcs[0]
    re_2 = gen.emit_binop('*',[src.re,src.re],Float)
    im_2 = gen.emit_binop('*',[src.im,src.im],Float)
    return gen.emit_binop('+',[re_2,im_2],Float)

def log_f_f(gen,t,srcs):
    return gen.emit_func('log', srcs, Float)

def log_c_c(gen,t,srcs):
    # log(a+ib) = (log(mag(a+ib)), atan2(a+ib))
    re = gen.emit_func('log', [cabs_c_f(gen,t,srcs)], Float)
    im = atan2_c_f(gen,t,srcs)
    return ComplexArg(re,im)

def polar_ff_c(gen,t,srcs):
    # polar(r,theta) = (r * cos(theta), r * sin(theta))
    re = gen.emit_binop('*',[srcs[0],cos_f_f(gen,t,[srcs[1]])], Float)
    im = gen.emit_binop('*',[srcs[0],sin_f_f(gen,t,[srcs[1]])], Float)
    return ComplexArg(re,im)

def exp_f_f(gen,t,srcs):
    return gen.emit_func('exp', srcs, Float)

def exp_c_c(gen,t,srcs):
    #exp(a+ib) = polar(exp(a),b)
    expx = gen.emit_func('exp', [srcs[0].re], Float)
    return polar_ff_c(gen,t,[expx, srcs[0].im])

def pow_ff_f(gen,t,srcs):
    return gen.emit_func2('pow', srcs, Float)

def pow_cf_c(gen,t,srcs):
    nonzero = gen.symbols.newLabel()
    done = gen.symbols.newLabel()
    dst_re = TempArg(gen.symbols.newTemp(Float))
    dst_im = TempArg(gen.symbols.newTemp(Float))

    gen.emit_cjump(srcs[0].im,nonzero)

    # compute result if just real
    tdest = pow_ff_f(gen,t,[srcs[0].re,srcs[1]])
    gen.emit_move(tdest,dst_re)
    gen.emit_jump(done)

    gen.emit_label(nonzero)
    # result if real + imag
    # temp = log(a+ib)
    # polar(y * real(temp), y * imag(temp))

    temp = log_c_c(gen,t,[srcs[0]])
    t_re = gen.emit_binop('*',[temp.re, srcs[1]], Float)
    t_re = gen.emit_func('exp',[t_re], Float)
    t_im = gen.emit_binop('*',[temp.im, srcs[1]], Float)
    temp2 = polar_ff_c(gen,t,[t_re, t_im])
    gen.emit_move(temp2.re,dst_re)
    gen.emit_move(temp2.im,dst_im)
    gen.emit_label(done)

    return ComplexArg(dst_re,dst_im)

def pow_cc_c(gen,t,srcs):
    nonzero = gen.symbols.newLabel()
    done = gen.symbols.newLabel()
    dst_re = TempArg(gen.symbols.newTemp(Float))
    dst_im = TempArg(gen.symbols.newTemp(Float))

    gen.emit_cjump(srcs[0].re,nonzero)
    gen.emit_cjump(srcs[0].im,nonzero)
    
    # 0^foo = 0
    gen.emit_move(ConstFloatArg(0.0),dst_re)
    gen.emit_move(ConstFloatArg(0.0),dst_im)
    gen.emit_jump(done)

    gen.emit_label(nonzero)
    # exp(y*log(x))

    logx = log_c_c(gen,t,[srcs[0]])
    ylogx = mul_cc_c(gen,t,[srcs[1],logx])
    xtoy = exp_c_c(gen,t,[ylogx])
    
    gen.emit_move(xtoy.re,dst_re)
    gen.emit_move(xtoy.im,dst_im)
    gen.emit_label(done)

    return ComplexArg(dst_re,dst_im)
    
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

# sqr = square(x) = x*x

def sqr_c_c(gen,t,srcs):
    # sqr(a+ib) = a2 - b2 + i(2ab)
    src = srcs[0]
    a2 = gen.emit_binop('*', [src.re, src.re], Float)
    b2 = gen.emit_binop('*', [src.im, src.im], Float)
    ab = gen.emit_binop('*', [src.re, src.im], Float)
    dst = ComplexArg(
        gen.emit_binop('-', [a2, b2], Float),
        gen.emit_binop('+', [ab, ab], Float))
    return dst
    
def sqr_f_f(gen,t,srcs):
    return gen.emit_binop('*',[srcs[0], srcs[0]], Float)

sqr_i_i = sqr_f_f

def conj_c_c(gen,t,srcs):
    # conj (a+ib) = a-ib
    b = gen.emit_binop('-', [ ConstFloatArg(0.0), srcs[0].im], Float)
    return ComplexArg(srcs[0].re,b)

def flip_c_c(gen,t,srcs):
    # flip(a+ib) = b+ia
    return ComplexArg(srcs[0].im,srcs[0].re)

def imag_c_f(gen,t,srcs):
    return srcs[0].im

def imag2_c_f(gen,t,srcs):
    return gen.emit_binop('*', [srcs[0].im, srcs[0].im], Float)

def real_c_f(gen,t,srcs):
    return srcs[0].re

def real2_c_f(gen,t,srcs):
    return gen.emit_binop('*', [srcs[0].re, srcs[0].re], Float)

def ident_i_i(gen,t,srcs):
    return srcs[0]

ident_f_f = ident_c_c = ident_b_b = ident_i_i

def recip_f_f(gen,t,srcs):
    # reciprocal
    return gen.emit_binop('/', [ConstFloatArg(1.0), srcs[0]], Float)

def recip_c_c(gen,t,srcs):
    return div_cc_c(gen, None,
                    [ComplexArg(ConstFloatArg(1.0), ConstFloatArg(0.0)), srcs[0]])

def abs_f_f(gen,t,srcs):
    return gen.emit_func('fabs',srcs, Float)

def abs_c_c(gen,t,srcs):
    return ComplexArg(abs_f_f(gen,t,[srcs[0].re]), abs_f_f(gen,t,[srcs[0].im]))

def cabs_c_f(gen,t,srcs):
    # FIXME: per std_complex.h,should divide numbers first to avoid overflow
    return sqrt_f_f(gen,t,[cmag_c_f(gen,t,srcs)])

def sqrt_f_f(gen,t,srcs):
    return gen.emit_func('sqrt', srcs, Float)

def min2_c_f(gen,t,srcs):
    r2 = real2_c_f(gen,t,srcs)
    i2 = imag2_c_f(gen,t,srcs)
    real_larger = gen.symbols.newLabel()
    done = gen.symbols.newLabel()
    dst = TempArg(gen.symbols.newTemp(Float))

    rgt = gen.emit_binop('>=',[r2,i2], Float)
    gen.emit_cjump(rgt,real_larger)

    # imag larger
    gen.emit_move(r2,dst)
    gen.emit_jump(done)

    gen.emit_label(real_larger)
    gen.emit_move(i2,dst)
    gen.emit_label(done)

    return dst

def max2_c_f(gen,t,srcs):
    r2 = real2_c_f(gen,t,srcs)
    i2 = imag2_c_f(gen,t,srcs)
    real_larger = gen.symbols.newLabel()
    done = gen.symbols.newLabel()
    dst = TempArg(gen.symbols.newTemp(Float))

    rgt = gen.emit_binop('>=',[r2,i2], Float)
    gen.emit_cjump(rgt,real_larger)

    # imag larger
    gen.emit_move(i2,dst)
    gen.emit_jump(done)

    gen.emit_label(real_larger)
    gen.emit_move(r2,dst)
    gen.emit_label(done)

    return dst

def sqrt_c_c(gen,t,srcs):
    xnonzero = gen.symbols.newLabel()
    done = gen.symbols.newLabel()
    dst_re = TempArg(gen.symbols.newTemp(Float))
    dst_im = TempArg(gen.symbols.newTemp(Float))

    gen.emit_cjump(srcs[0].re,xnonzero)
    
    # only an imaginary part :
    # temp = sqrt(abs(z.im) / 2);
    # return (temp, __y < 0 ? -__temp : __temp);
    
    temp = sqrt_f_f(gen, t, [ abs_f_f(gen,t, [
        gen.emit_binop('/',[srcs[0].im, ConstFloatArg(2.0)],Float)])])

    gen.emit_move(temp,dst_re)
    # y >= 0?
    ypos = gen.emit_binop('>=',[srcs[0].im,ConstFloatArg(0.0)], Float)
    ygtzero = gen.symbols.newLabel()
    gen.emit_cjump(ypos,ygtzero)
    
    nt = neg_f_f(gen,t, [temp])
    gen.emit_move(nt,temp)
    
    gen.emit_label(ygtzero)
    gen.emit_move(temp,dst_im)
    gen.emit_jump(done)

    gen.emit_label(xnonzero)
    # both real and imaginary

    # temp = sqrt(2 * (cabs(z) + abs(z.re)));
    # u = temp/2
    temp = sqrt_f_f(
        gen,t,
        [ gen.emit_binop(
            '*',
            [ConstFloatArg(2.0),
             gen.emit_binop(
                 '+',
                 [cabs_c_f(gen,t,[srcs[0]]),
                  abs_f_f(gen,t,[srcs[0].re])],
                 Float)
             ],
            Float)
          ])
    u = gen.emit_binop('/',[temp,ConstFloatArg(2.0)], Float)
    
    #x > 0?
    xpos = gen.emit_binop('>',[srcs[0].re,ConstFloatArg(0.0)], Float)    
    xgtzero = gen.symbols.newLabel()
    gen.emit_cjump(xpos,xgtzero)

    # x < 0:

    # x = abs(im)/temp
    gen.emit_move(gen.emit_binop(
        '/',
        [abs_f_f(gen,t,[srcs[0].im]), temp], Float) , dst_re)

    # y < 0 ? -u : u
    ypos2 = gen.emit_binop('>=',[srcs[0].im,ConstFloatArg(0.0)], Float)    
    ygtzero2 = gen.symbols.newLabel()
    gen.emit_cjump(ypos2,ygtzero2)
    gen.emit_move(neg_f_f(gen,t,[u]), dst_im)
    gen.emit_jump(done)
    gen.emit_label(ygtzero2)
    gen.emit_move(u, dst_im)
    gen.emit_jump(done)

    # x > 0:
    gen.emit_label(xgtzero)

    # (u, im/temp)
    gen.emit_move(u,dst_re)
    gen.emit_move(gen.emit_binop('/',[srcs[0].im, temp], Float),dst_im)
    
    gen.emit_label(done)

    return ComplexArg(dst_re,dst_im)

def sin_f_f(gen,t,srcs):
    return gen.emit_func('sin', srcs, Float)

def sin_c_c(gen,t,srcs):
    # sin(a+ib) = (sin(a) * cosh(b), cos(a) * sinh(b))
    a = srcs[0].re ; b = srcs[0].im
    re = gen.emit_binop('*', [ sin_f_f(gen,t,[a]), cosh_f_f(gen,t,[b])], Float)
    im = gen.emit_binop('*', [ cos_f_f(gen,t,[a]), sinh_f_f(gen,t,[b])], Float)
    return ComplexArg(re,im)

def cos_f_f(gen,t,srcs):
    return gen.emit_func('cos', srcs, Float)

def cos_c_c(gen,t,srcs):
    # cos(a+ib) = (cos(a) * cosh(b), -(sin(a) * sinh(b)))
    a = srcs[0].re ; b = srcs[0].im
    re = gen.emit_binop('*', [ cos_f_f(gen,t,[a]), cosh_f_f(gen,t,[b])], Float)
    im = gen.emit_binop('*', [ sin_f_f(gen,t,[a]), sinh_f_f(gen,t,[b])], Float)
    
    nim = gen.emit_func('-',[im], Float)
    return ComplexArg(re,nim)
        
def tan_f_f(gen,t,srcs):
    return gen.emit_func('tan', srcs, Float)

def tan_c_c(gen,t,srcs):
    # tan = sin/cos
    return div_cc_c(gen,t, [sin_c_c(gen,t, [srcs[0]]), cos_c_c(gen,t,[srcs[0]])])

def cotan_c_c(gen,t,srcs):
    return div_cc_c(gen,t, [cos_c_c(gen,t, [srcs[0]]), sin_c_c(gen,t,[srcs[0]])])

def cotan_f_f(gen,t,srcs):
    return gen.emit_binop('/', [gen.emit_func('cos', srcs, Float),
                                gen.emit_func('sin', srcs, Float)], Float)

def cotanh_f_f(gen,t,srcs):
    return gen.emit_binop('/', [gen.emit_func('cosh', srcs, Float),
                                gen.emit_func('sinh', srcs, Float)], Float)

def cotanh_c_c(gen,t,srcs):
    return div_cc_c(gen,t, [cosh_c_c(gen,t, [srcs[0]]),
                            sinh_c_c(gen,t,[srcs[0]])])

def cosh_f_f(gen,t,srcs):
    return gen.emit_func('cosh', srcs, Float)

def cosh_c_c(gen,t,srcs):
    # cosh(a+ib) = cosh(a)*cos(b) + i (sinh(a) * sin(b))
    a = [srcs[0].re]; b = [srcs[0].im]
    re = gen.emit_binop('*', [ cosh_f_f(gen,t,a), cos_f_f(gen,t,b)], Float)
    im = gen.emit_binop('*', [ sinh_f_f(gen,t,a), sin_f_f(gen,t,b)], Float)    
    return ComplexArg(re,im)

def sinh_f_f(gen,t,srcs):
    return gen.emit_func('sinh', srcs, Float)

def sinh_c_c(gen,t,srcs):
    # sinh(a+ib) = sinh(a)*cos(b) + i (cosh(a) * sin(b))
    a = [srcs[0].re]; b = [srcs[0].im]
    re = gen.emit_binop('*', [ sinh_f_f(gen,t,a), cos_f_f(gen,t,b)], Float)
    im = gen.emit_binop('*', [ cosh_f_f(gen,t,a), sin_f_f(gen,t,b)], Float)    
    return ComplexArg(re,im)

def tanh_f_f(gen,t,srcs):
    return gen.emit_func('tanh', srcs, Float)

def tanh_c_c(gen,t,srcs):
    # tanh = sinh / cosh
    return div_cc_c(gen,t, [sinh_c_c(gen,t, [srcs[0]]), cosh_c_c(gen,t,[srcs[0]])])

def asin_f_f(gen,t,srcs):
    return gen.emit_func('asin', srcs, Float)

def asin_c_c(gen,t,srcs):
    # asin(z) = -i * log(i*z + sqrt(1-z*z))
     one = ComplexArg(ConstFloatArg(1.0),ConstFloatArg(0.0))
     i = ComplexArg(ConstFloatArg(0.0),ConstFloatArg(1.0))
     minus_i = ComplexArg(ConstFloatArg(0.0),ConstFloatArg(-1.0))
   
     one_minus_z2 = sub_cc_c(gen,t,[one,sqr_c_c(gen,t,srcs)])
     sq = sqrt_c_c(gen,t,[one_minus_z2])
     arg = add_cc_c(gen,t,[mul_cc_c(gen,t,[i,srcs[0]]), sq])

     l = log_c_c(gen,t,[arg])
     return mul_cc_c(gen,t,[minus_i,l])                         

def acos_f_f(gen,t,srcs):
    return gen.emit_func('acos', srcs, Float)

def acos_c_c(gen,t,srcs):
    # acos(z) = pi/2 - asin(z)
    pi_by_2 = ComplexArg(ConstFloatArg(math.pi/2.0),ConstFloatArg(0.0))
    return sub_cc_c(gen,t,[pi_by_2, asin_c_c(gen,t,srcs)])

def atan_f_f(gen,t,srcs):
    return gen.emit_func('atan', srcs, Float)

def atan_c_c(gen,t,srcs):
    # atan(z) = i/2 * log(i+x/i-x)
    i = ComplexArg(ConstFloatArg(0.0),ConstFloatArg(1.0))
    iby2 = ComplexArg(ConstFloatArg(0.0),ConstFloatArg(0.5))
    ratio = div_cc_c(gen,t,[add_cc_c(gen,t,[i,srcs[0]]),
                            sub_cc_c(gen,t,[i,srcs[0]])])
    return mul_cc_c(gen,t,[iby2,log_c_c(gen,t,[ratio])])

def atan2_c_f(gen,t,srcs):
    return gen.emit_func2('atan2', [srcs[0].im, srcs[0].re], Float)

def asinh_f_f(gen,t,srcs):
    return gen.emit_func('asinh', srcs, Float)

def asinh_c_c(gen,t,srcs):
    # log(z + sqrt(z*z+1))
    one = ComplexArg(ConstFloatArg(1.0),ConstFloatArg(0.0))
    sq = sqrt_c_c(gen,t,[add_cc_c(gen,t,[one,sqr_c_c(gen,t,srcs)])])
    return log_c_c(gen,t,[add_cc_c(gen,t,[srcs[0],sq])])

def acosh_f_f(gen,t,srcs):
    return gen.emit_func('acosh', srcs, Float)

def acosh_c_c(gen,t,srcs):
    # log(z + sqrt(z-1)*sqrt(z+1))
    one = ComplexArg(ConstFloatArg(1.0),ConstFloatArg(0.0))    
    sqzm1 = sqrt_c_c(gen,t,[sub_cc_c(gen,t,[srcs[0],one])])
    sqzp1 = sqrt_c_c(gen,t,[add_cc_c(gen,t,[srcs[0],one])])
    sum = add_cc_c(gen,t,[srcs[0],mul_cc_c(gen,t,[sqzm1,sqzp1])])
    return log_c_c(gen,t,[sum])
    
def atanh_f_f(gen,t,srcs):
    return gen.emit_func('atanh', srcs, Float)

def manhattanish_c_f(gen,t,srcs):
    return gen.emit_binop('+',[srcs[0].re,srcs[0].im],Float)

def manhattan_c_f(gen,t,srcs):
    return gen.emit_binop('+',[abs_f_f(gen,t,[srcs[0].re]),
                               abs_f_f(gen,t,[srcs[0].im])], Float)

def manhattanish2_c_f(gen,t,srcs):
    return sqr_f_f(
        gen,t,[gen.emit_binop('+',[sqr_f_f(gen,t,[srcs[0].re]),
                                   sqr_f_f(gen,t,[srcs[0].im])], Float)])
