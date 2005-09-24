
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
