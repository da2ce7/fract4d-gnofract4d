comment {

This file contains the standard fractal types shipped with Gnofract4D
In some cases, these have been adapted from Fractint formulas. 
These have had -G4 appended to avoid any confusion.
}

T03-01-G4 {; based on T03-01 in CHBY1.FRM by Morgan L. Owens
        ; Modified for Gf4D by EY
        ; = 2zT02-T01
  t=z, bailout=4, z=pixel:
  x=real(z), y=imag(z)
  Tx=x*(4*x*x-3)
  Ty=y*(4*y*y-3)
  x=x-t*Ty, y=y+t*Tx
  z=x+flip(y)
  |z|<=bailout
}

Mandelbrot {
init:
	; nothing to do here
loop:
	z = z * z + #pixel
bailout:
	|z| <= 4
}

Mandelbar {
init:
	; nothing to do here
loop:
	z = conj(z)^@p1 + #pixel
bailout:
	|z| <= 4
}

Quadratic {
init:
	; nothing to do here
loop:
	z = (@p1 * z + @p2) * z + @p3 * #pixel
bailout:
	|z| <= 4
}

Cubic Mandelbrot {
init:
	; nothing to do here
loop:
	z = z * z * (z - 3.0 * @p1) + #pixel
bailout:
	|z| <= 4
}

ManZPower {
loop:
	z = z^@p1 + #pixel
bailout:
	|z| <= 4
}

Barnsley Type 1 {
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
	|z| <= 4
}

Barnsley Type 2 {
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
	|z| < 4
}

Barnsley Type 3 {
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
	|z| < 4.0
}

Buffalo {
loop:
	z = (abs(real(z)),abs(imag(z)))
	z = (z - 1.0) * z + #pixel
bailout:
	|z| < 4.0
}     
		
Burning Ship {
loop:
	z = (abs(real(z)),abs(imag(z)))
	z = z*z + #pixel
bailout: 
	|z| < 4.0
}

Cubic Burning Ship {
loop:
	z = (abs(real(z)),abs(imag(z)))
	z = z*z*z + #pixel
bailout: 
	|z| < 4.0
}
