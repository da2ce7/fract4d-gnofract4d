3daMand01 {; Mandelbrot/Zexpe via Lee Skinner
  ; based on 4dFRACT.FRM by Gordon Lamb (CIS: 100272,3541)
  z=real(pixel) +flip(imag(pixel)*p1)
  c=p2+p1*real(pixel)+flip(imag(pixel))
:
  z=z^2.01 + c
    |z|<=100
  }

mandelfn {
   z = 0:
   z = fn1(z*z) + pixel
   |z| < 4.0
}

fnz {
   z = 0:
   z = fn1(z) + pixel
   |z| < 4.0
}

fn_with_intparam {
init:
z = #zwpixel
loop:
z = z*z + #pixel
bailout:
|z| < @x
default:
int param x
	default = 3
endparam
}
 
dmj-ManyJulia {
;
; This formula breaks the image up into a grid of
; squares, each square containing a small Julia set
; using the c value from the center of the square.
; As the size of the grid is reduced, the image will
; approach that of the Mandelbrot set.
;
init:
  float iscale = 1 / @scale
  c = round(#pixel * @scale) * iscale
  z = (#pixel - c) * @scale * @jscale

loop:
  z = z^@power + c
  
bailout:
  |z| < @bailout
  
default:
  title = "ManyJulia"
  helpfile = "dmj-pub\dmj-pub-uf-manyjulia.htm"
  maxiter = 1000
  center = (-0.5,0)
  magn = 1.0
  
  param power
    caption = "Exponent"
    default = (2,0)
    hint = "Overall exponent for the equation.  (2,0) gives \
            the classic Mandelbrot type."
  endparam
  param bailout
    caption = "Bailout"
    default = 1.0e20
    hint = "Defines how soon an orbit bails out, i.e. doesn't belong \
            to the Mandelbrot set anymore."
  endparam
  param scale
    caption = "Julia Density"
    default = 2.0
    hint = "Specifies the density of separate Julia sets; higher \
            numbers will produce more divisions."
  endparam
  param jscale
    caption = "Julia Zoom"
    default = 3.0
    hint = "Specifies the zoom level of Julia sets within each division."
  endparam
}
