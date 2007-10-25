Evil {
init:
	z = 0
loop:
	z = z
bailout:
	|z| < 4.0
default:
maxiter = 1000000000
}

WarpTest {
init:
	z = @p1
loop:
	z = z*z + #pixel
bailout:
	|z| < 4.0
}

PeterDeJong {
init:
	z = #rand
loop:
	float x = sin(@a * imag(z)) - cos(@b * real(z))
	float y = sin(@c * real(z)) - cos(@d * imag(z))
	z = (x,y)
default:
	
float param a
	default = 1.0
endparam

float param b
	default = 0.5
endparam

float param c
	default = 0.9
endparam

float param d
	default = 0.7
endparam
maxiter = 10000
}

C4G {; p1 is (plus or minus) 1 or i 
x=real(pixel), y=imag(pixel)*p1
a=b=0:
a1 = a^2-p1^2*b^2
b1 = 2*a*b
a=a1+x, b=b1+y
z = sqrt(a^2 + b^2)
z < 4 }

C6 group{
x=real(pixel), y=imag(pixel), v=p1
x1=x2=y1=y2=v1=v2=0:
    a1 = x1^2+ x2^2+2*y1*v1+2*y2*v2
    a2 = 2*x1*x2+2*y1*v2+2*y2*v1
    b1 = 2*x1*y1+2*x2*y2+v1^2+v2^2
    b2 = 2*x1*y2+2*x2*y1+2*v1*v2
    c1 = 2*x1*v1+2*x2*v2+y1^2+y2^2
    c2 = 2*x1*v2+2*x2*v1+2*y1*y2
    x1=a1+x, x2=a2-x
    y1=b1+y, y2=b2-y
    v1=c1+v, v2=c2-v
    z = (x1-x2)^2 + (y1-y2)^2+ (v1-v2)^2
z < 1000  }

Triternions{
c1=real(pixel), c2=imag(pixel), c3=p1
x=y=v=0:
    a = x^2+2*y*v
    b = v^2+2*x*y
    c = y^2+2*x*v
    x=a+c1, y=b+c2, v=c+c3
    z=x^2+y^2+v^2
z < 1000 }

General Burning Ship {
init:
	z = #zwpixel
loop:
	z = abs(z)
	z = @fn1(z*z) + #pixel
bailout: 
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
xycenter = (-0.5,-0.5)
}

Gravitybrot1 {
init:
	z = #zwpixel
loop:
	z = z*z + #pixel
	dz = @g / sqr(|z|)
	z = z - dz
bailout:
	@bailfunc(z) < @bailout
default:
float param g
	default = 1.0e-6
endparam
float func bailfunc
	default = cmag
endfunc
float param bailout
	default = 4.0
endparam
}

Gravitybrot2 {
init:
	z = #zwpixel
loop:
	z = z*z + #pixel
	dz = (z/|z| * @g) / sqr(|z|)
	z = z - dz
bailout:
	@bailfunc(z) < @bailout
default:
float param g
	default = 1.0e-6
endparam
float func bailfunc
	default = cmag
endfunc
float param bailout
	default = 4.0
endparam
}

Gravitybrot3 {
init:
	z = #zwpixel
loop:
	z = z*z + #pixel
	dz = (z/|z| * @g) / @gravfunc(|z|)
	z = z - dz
bailout:
	@bailfunc(z) < @bailout
default:
float param g
	default = 1.0e-6
endparam
float func bailfunc
	default = cmag
endfunc
float param bailout
	default = 4.0
endparam
float func gravfunc
	argtype = float
	default = sqr
endfunc
}

Damp {
init:
	z = #zwpixel
	zlast = 0.0
	float mfactor = 1.0 - @factor
loop:
	z = @factor * (@fn1(z*z) + #pixel) + mfactor * zlast
	zlast = z
bailout:
	@bailfunc(z) < @bailout
default:
float param factor
	default = 0.5
endparam
float func bailfunc
	default = cmag
endfunc
float param bailout
	default = 4.0
endparam
}

Mandelbrot {
; The classic Mandelbrot set
; with a DCA which matches the v1.x RGB colorizer
init:
	z = #zwpixel
loop:
	z = z * z + #pixel
bailout:
	@bailfunc(z) < @bailout
final:
	float dist = #numiter / 256.0
	float r = (dist * (1.0 + 10.0 * @base_r)) % 256.0
	float g = (dist * (1.0 + 10.0 * @base_g)) % 256.0
	float b = (dist * (1.0 + 10.0 * @base_b)) % 256.0
	#color = rgb(r,g,b)
default:
float param bailout
	default = 4.0
endparam
float param base_r
	default = 1.0 
endparam
float param base_g
	default = 0.0 
endparam
float param base_b
	default = 0.0 
endparam

float func bailfunc
	default = cmag
endfunc
}


Expanding_Horizon {
init:
	z = #zwpixel
	bail_point = 0
loop:
	z = @fn1(z*z) + #pixel
	bail_point = sqr(bail_point) + #pixel
bailout:
	@bailfunc(z) < @bailfunc(bail_point) + @bailout
default:
float param factor
	default = 1.0
endparam
float func bailfunc
	default = cmag
endfunc
float param bailout
	default = 4.0
endparam
}

Expanding_Horizon_2 {
init:
	z = #zwpixel
	bail_point = #zwpixel
loop:
	z = @fn1(z*z) + #pixel
	bail_point = @fn2(bail_point) + #pixel
bailout:
	@bailfunc(z) < @bailfunc(bail_point)
default:
float param factor
	default = 1.0
endparam
float func bailfunc
	default = cmag
endfunc
float param bailout
	default = 4.0
endparam
}
 
Glitch1 {
init:
	z = #zwpixel
loop:
	z = @fn2(@fn1(abs(real(z)),abs(imag(z))))
	z = (z - 1.0) * z + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
magnitude=6.0
}     

Glitch2 {
init:
	z = #zwpixel
loop:
	z = @fn2(@fn1(abs(real(z)),abs(imag(z)))) + (@fn3(100*z)/100)
	z = (z - 1.0) * z + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
magnitude=6.0
}     

MandelGlitch {
init:
	z = #zwpixel
loop:
	z = z*z + #pixel
	z = z + @fn1(z * @factor)/@factor
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
float param factor
	default = 10.0
endparam
}     

Direct CCL {
; iterates both critical points of the cubic set,
; colors results according to which basin they end up in
; ignores coloring algorithm

init:
k = #zwpixel
z1 = k
z2 = -k
int num_z1 = -1
int num_z2 = -1
int i = 0
loop:
z1 = z1*z1*z1 - 3*k + #pixel
z2 = z2*z2*z2 - 3*k + #pixel
if |z1| > @bailout && num_z1 == -1
   num_z1 = i
endif
if |z2| > @bailout && num_z2 == -1
   num_z2 = i
endif
i = i + 1
bailout:
|z1| < @bailout || |z2| < @bailout
final:
if num_z1 == -1
   if num_z2 == -1
      ; inside
      #color = rgb(0,0,0)
   else
      ; m+
      #color = blend(@mplus,@out,num_z2/i)
   endif
else
   if num_z2 == -1
      ; m-
      #color = blend(@mminus,@out,num_z1/i)
   else
      ; out
      if num_z1 > num_z2
         float r = num_z2/num_z1
         float bail_speed = (#maxiter - num_z1)/#maxiter
      else
         float r = num_z1/num_z2
         float bail_speed = (#maxiter - num_z2)/#maxiter
      endif
      #color = blend(blend(@mminus,@mplus,r),@out,bail_speed)
   endif
endif
#solid = false
default:
periodicity = 0
float param bailout
	default = 4.0
endparam
color param mplus
	default = rgb(1,0,0)
endparam
color param mminus
	default = rgb(0,1,0)
endparam
color param out
	default = rgb(0,0,1)
endparam
}

Taylor Series {
init:
target = exp(#pixel)
float denominator = 1
int count = 0
z = 0
start = exp(#zwpixel)
loop:
	z = z + exp(start) * ((#pixel - start)^count) / denominator
	if count > 0
		denominator = denominator * (count + 1)
	endif
	count = count + 1
bailout:
	|z - target| > @tolerance
default:
float param tolerance
	default = 0.00000001
endparam
}

EvenOddAbs {
init:
z = #zwpixel
int i = 0
loop:
	if i % 2 == 0
		z = (abs(real(z)),imag(z))
	else
		z = (real(z),abs(imag(z)))
	endif
	z = z*z + #pixel
bailout:
	|z| < 400.0
}

He02-01 {; V.1.1 - earlier versions may be discarded
         ; Copyright (c)1998,1999 Morgan L. Owens
         ; Chebyshev Types:
         ; Inspired by Clifford A. Pickover:
         ; Dynamic (Euler method)
         ;
         ; He(n+1) = xHe(n)-nHe(n-1)
         ; He(0)  = 1
         ; He(1)  = sqrt(2)x
         ;
         ; = xHe(1)-He(0)
  s=sqrt(2), t=#zwpixel, z=pixel:
  x=real(z), y=imag(z)
  Tx=s*x*x-1
  Ty=s*y*y-1
  x=x-t*Ty, y=y+t*Tx
  z=x+flip(y)
  |z|<= @bailout
default:
float param bailout
	default = 4.0
endparam
}

MandAutoCritInZ {; Jim Muth

a=real(p1), b=imag(p1), d=real(p2), f=imag(p2),
g=1/f, h=1/d, j=1/(f-b), z=(((-a*b*g*h)^j)+(p4)),
k=real(p3)+1, l=imag(p3)+100, c=fn1(pixel):
z=k*((a*(z^b))+(d*(z^f)))+c,
|z| < l 
}

T02-01-experiment {

; Dynamic (Euler method)
;
; T(n+1) = 2xT(n)-T(n-1)
; T(0)  = 1
; T(1)  = x
;
; = 2zT01-T00

  float t=real(p1), bailout=4, z=pixel:
  float x=real(z), float y=imag(z)
  float Tx=(x+x)*x-@relax
  float Ty=(y+y)*y-@relax
  x=x-t*Ty, y=y+t*Tx
  z=(x,y)
  |z|<=bailout
default:
float param relax
	default = 1.0
endparam
}

mandelfn {
init:
	z = #zwpixel
loop:
	z = @fn1(z * z * #pixel) + z + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
}

FnPartsPower {
; A generalization of Burning Ship - apply separate functions to the 
; X and Y parts of Z, then another to Z itself
init:
	z = #zwpixel
loop:
	z = (@fnReal(real(z)), @fnImag(imag(z)))^@pow + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
complex param pow
	default = (2.0, 0.0)
endparam
float param bailout
	default = 4.0
endparam
float func bailfunc
	default =cmag
endfunc
float func fnReal
	argtype = float
	default = abs
endfunc
float func fnImag
	argtype = float
	default = abs
endfunc
}


Chebyshev {
; a generalization of a number of Fractint Chebyshev functions
init:
  float s=sqrt(2)
  float a=0, float b=0, float c=0
  if @functype == "04-01"
    a = 8*s+7
  elseif @functype == "05-01"
    a = 8*s+7
  elseif @functype == "06-01"
    a = 33*s+12
  elseif @functype == "07-01"
    a=87*s+18, b=8*s-57
  elseif @functype == "08-01"
    a=185*s+25, b=41*s-141
  elseif @functype == "09-01"
    a=345*s+33, b=136*s-285
  elseif @functype == "10-01"
    a=588*s+42, b=321*s-510, c=41*s-1830
  endif
  float Tx, float Ty, float xx, float yy
  complex t=#zwpixel
  z=#pixel
loop:
  float x=real(z), float y=imag(z)
if @functype == "02-01"
  Tx=s*x*x-1
  Ty=s*y*y-1
elseif @functype == "03-01"
  Tx=x*(s*(x*x-2)-1)
  Ty=y*(s*(y*y-2)-1)
elseif @functype == "04-01"
  xx=x*x, yy=y*y
  Tx=xx*(s*(xx-5)-1)+3
  Ty=yy*(s*(yy-5)-1)+3
elseif @functype == "05-01"
  xx=x*x, yy=y*y
  Tx=x*(xx*(s*(xx-9)-1)+a)
  Ty=y*(yy*(s*(yy-9)-1)+a)
elseif @functype == "06-01"
  xx=x*x, yy=y*y
  Tx=xx*(xx*(s*(xx-14)-1)+a)-15
  Ty=yy*(yy*(s*(yy-14)-1)+a)-15
elseif @functype == "07-01"
  xx=x*x, yy=y*y
  Tx=x*(xx*(xx*(s*(xx-20)-1)+a)+b)
  Ty=y*(yy*(yy*(s*(yy-20)-1)+a)+b)
elseif @functype == "08-01"
  xx=x*x, yy=y*y
  Tx=xx*(xx*(xx*(s*(xx-27)-1)+a)+b)+105
  Ty=yy*(yy*(yy*(s*(yy-27)-1)+a)+b)+105
elseif @functype == "09-01"
  xx=x*x, yy=y*y
  Tx=x*(xx*(xx*(xx*(s*(xx-35)-1)+a)+b)+561)
  Ty=y*(yy*(yy*(yy*(s*(yy-35)-1)+a)+b)+561)
elseif @functype == "10-01"
  xx=x*x, yy=y*y
  Tx=xx*(xx*(xx*(xx*(s*(xx-44)-1)+a)+b)+c)-945
  Ty=yy*(yy*(yy*(yy*(s*(yy-44)-1)+a)+b)+c)-945
endif
  z= abs(x-t*Ty + flip(y+t*Tx))
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4000.0
endparam
float func bailfunc
	default =cmag
endfunc
int param functype
	enum = "02-01" "03-01" "04-01" "05-01" "06-01" "07-01" "08-01" "09-01" "10-01"
endparam
zcenter=1.0
wcenter=0.1
magnitude=8.0
maxiter=256
}
