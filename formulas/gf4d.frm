comment {

This file contains the standard fractal types shipped with
Gnofract4D. They come from a variety of sources, which I've noted in
the comments for each fractal.

Each fractal includes its own Julia "twin" implicitly, so those aren't
listed as separate types.

If you modify these formulas, import of .fct files generated by previous
Gnofract4D versions may not work, so I suggest copying the formulas to
another file and renaming them before changing them.
 
In some cases, these have been adapted from Fractint formulas. 
These have had -G4 appended to avoid any confusion.


}

Mandelbrot {
; The classic Mandelbrot set
init:
	z = #zwpixel
loop:
	z = z * z + #pixel
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

HyperMandel {
; Hypercomplex Mandelbrot set
init:
	hyper h = @h0
	hyper c = (real(#pixel),imag(#pixel),real(#zwpixel), imag(#zwpixel)) 
loop:
	h = @hfunc(h) + c
bailout:
	|h| < @bailout
default:
float param bailout
	default = 64.0
endparam
hyper func hfunc
	default = sqr
endfunc
hyper param h0
	default = (0.0,0.0,0.0,0.0)
endparam
}

HyperJulia {
; Hypercomplex Julia set
init:
	hyper h = (real(#pixel),imag(#pixel),real(#zwpixel), imag(#zwpixel)) 
loop:
	h = @hfunc(h) + @c
bailout:
	|h| < @bailout
default:
float param bailout
	default = 64.0
endparam
hyper func hfunc
	default = sqr
endfunc
hyper param c
	default = (0.16,0.1,0.1,0.1)
endparam
}

Mandelbar {
; I first came across this at http://mathworld.wolfram.com/MandelbarSet.html
init:
	z = #zwpixel
loop:
	z = conj(z)^@a + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
complex param a
	title = "Power"
	default = (2.0,0.0)
endparam
zcenter=1.0e-10
}

Quadratic {
; Included for backwards compatibility with earlier versions. There are more
; parameters here than are strictly warranted, since any combination of A,B, 
; and C is actually equivalent to moving the initial point around.

init:
	z = #zwpixel
loop:
	z = (@a * z + @b) * z + @c * #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
complex param a
	default = (1.0, 0.0)
endparam
complex param b
	default = (1.0, 0.0)
endparam
complex param c
	default = (1.0, 0.0)
endparam
}

Cubic Mandelbrot {
; z <- z^3 + c
; The cubic set actually has two critical values, but this formula just uses  
; zero - to be fixed later.
init:
	z = #zwpixel
	; nothing to do here
loop:
	z = z * z * (z - 3.0 * @a) + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
complex param a
	default = (0.0,0.0)
endparam
}

ManZPower {
; The Mandelbrot set raised to the N'th power
init:
	z = #zwpixel
loop:
	z = z^@a + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
complex param a
	title = "Power"
	default = (4.0,0.0)
endparam
float func bailfunc
	default = cmag
endfunc
zcenter=1.0e-10
}

Barnsley Type 1 {
; From Michael Barnsley's book Fractals Everywhere, via Fractint
init:
	z = #zwpixel
loop:
	float x_cy = real(z) * imag(#pixel)
	float x_cx = real(z) * real(#pixel)
	float y_cy = imag(z) * imag(#pixel)
	float y_cx = imag(z) * real(#pixel)

	if(real(z) >= 0)
		z = (x_cx - real(#pixel) - y_cy, y_cx - imag(#pixel) + x_cy)
	else 
		z = (x_cx + real(#pixel) - y_cy, y_cx + imag(#pixel) + x_cy)
	endif
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

Barnsley Type 2 {
; From Michael Barnsley's book Fractals Everywhere, via Fractint
init:
	z = #zwpixel
loop:
	float x_cy = real(z) * imag(#pixel)
	float x_cx = real(z) * real(#pixel)
	float y_cy = imag(z) * imag(#pixel)
	float y_cx = imag(z) * real(#pixel)

	if(real(z) * imag(#pixel) + imag(z) * real(#pixel) >= 0)
		z = (x_cx - real(#pixel) - y_cy, y_cx - imag(#pixel) + x_cy)
	else 
		z = (x_cx + real(#pixel) - y_cy, y_cx + imag(#pixel) + x_cy)
	endif
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

Barnsley Type 3 {
; From Michael Barnsley's book Fractals Everywhere, via Fractint
init:
	z = #zwpixel
loop:
	float x2 = real(z) * real(z)
	float y2 = imag(z) * imag(z)
	float xy = real(z) * imag(z)

	if(real(z) > 0)
		z = (x2 - y2 - 1.0, xy * 2.0)
	else
		z = (x2 - y2 - 1.0 + real(#pixel) * real(z), \
		     xy * 2.0 + imag(#pixel) * real(z))
	endif
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

Buffalo {
; From the web page http://www.theory.org/fracdyn/ 

; The Burning Ship is essentially a Mandelbrot variant where the real
; and imaginary parts of the current point are set to their absolute
; values after each iteration, ie z <- (|x| + i |y|)^2 + c. The
; Buffalo fractal uses the same method with the function z <- z^2 - z
; + c, making it equivalent to the Quadratic type with the "absolute
; value" modification.  

init:
	z = #zwpixel
loop:
	z = (abs(real(z)),abs(imag(z)))
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
		
Burning Ship {
; From the web page http://www.theory.org/fracdyn/ 

; The Burning Ship is essentially a Mandelbrot variant where the real
; and imaginary parts of the current point are set to their absolute
; values after each iteration, ie z <- (|x| + i |y|)^2 + c. The
; Buffalo fractal uses the same method with the function z <- z^2 - z
; + c, making it equivalent to the Quadratic type with the "absolute
; value" modification.  


init:
	z = #zwpixel
loop:
	z = (abs(real(z)),abs(imag(z)))
	z = z*z + #pixel
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

Cubic Burning Ship {
init:
	z = #zwpixel
loop:
	z = (abs(real(z)),abs(imag(z)))
	z = z*z*z + #pixel
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

Lambda {

; The Lambda function calculates lambda * z * ( 1 - z). The complex
; parameter lambda is set by the z and w parameters, so if lambda is
; zero, all you'll see is a blank screen.

init:
	z = #zwpixel
loop:
	t = z * (1.0 - z)
	z = t * #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
xcenter=1.0
zcenter=0.5
magnitude=8.0
}

Magnet {

; Magnet and Magnet 2 are from Fractint, but images generated by
; Gnofract 4D look a bit different because I don't look for a finite
; attractor.

init:
	z = #zwpixel
loop:
	z = (z * z + #pixel - 1.0)/(2.0 * z + #pixel - 2.0)
	z = z *z
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
xcenter=2.0
magnitude=8.0
}

Magnet 2 {

; Magnet and Magnet 2 are from Fractint, but images generated by
; Gnofract 4D look a bit different because I don't look for a finite
; attractor.

init:
	z = #zwpixel
loop:
	cm1 = #pixel - 1.0, cm2 = #pixel - 2.0
	z = (z * z * z + 3.0 * cm1 * z + cm1 * cm2)/ \
	     (3.0 * z * z + 3.0 * cm2 * cm2 + cm1 * cm2 + 1.0)
	z = z*z

bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
xcenter=2.0
magnitude=3.0
}

Newton {
; Newton is the Newton-Raphson method applied to z^a = root
init:
	z = #zwpixel
	nm1 = @a - 1.0
loop:
	last = z
	z = z - (z ^ @a - @root)/ (@a * z ^ nm1)
bailout:
	|z - last| > #tolerance
default:
xzangle=1.5707963267948966
ywangle=1.5707963267948966
xcenter=1.0
param a
	default = (3.0, 0.0)
endparam
param root
	default = (1.0, 0.0)
endparam

}

Nova {
; Nova is Paul Derbyshire's Nova fractal.
init:
	z = #zwpixel
loop:
	last = z
	z = z - (@a * z * z * z - @b)/(@c * z * z) + #pixel
bailout:
	|z - last| > @epsilon
default:
param a
	default = (1.0, 0.0)
endparam
param b
	default = (1.0, 0.0)
endparam
param c
	default = (3.0, 0.0)
endparam
float param epsilon
	default = 0.01
endparam
zcenter=1.0
magnitude=3.0
}


Tetrate {
; Tetrate computes z <- z^c
init:
	z = #zwpixel
loop:
	z = #pixel^z
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


T02-01-G4 {; Modified for Gf4d by EY
	; V.1.1 - earlier versions may be discarded
        ; Copyright (c)1998,1999 Morgan L. Owens
        ; Chebyshev Types:
        ; Inspired by Clifford A. Pickover:
        ; Dynamic (Euler method)
        ;
        ; T(n+1) = 2xT(n)-T(n-1)
        ; T(0)  = 1
        ; T(1)  = x
        ;
        ; = 2zT01-T00
  t=#zwpixel, z=pixel:
  x=real(z), y=imag(z)
  Tx=(x+x)*x-1
  Ty=(y+y)*y-1
  x=x-t*Ty, y=y+t*Tx
  z=x+flip(y)
  |z| < @bailout
default:
float param bailout
	default = 4.0
endparam
zwcenter = (0.3,0.2)
}

T03-01-G4 {; based on T03-01 in CHBY1.FRM by Morgan L. Owens
        ; Modified for Gf4D by EY
        ; = 2zT02-T01
  t=#zwpixel, z=pixel:
  float x=real(z), float y=imag(z)
  float Tx=x*(4*x*x-3)
  float Ty=y*(4*y*y-3)
  cx=x-t*Ty, cy=y+t*Tx
  z=cx+flip(cy)
  |z| < @bailout
default:
float param bailout
	default = 4.0
endparam
zwcenter = (0.02,0.01)
}

