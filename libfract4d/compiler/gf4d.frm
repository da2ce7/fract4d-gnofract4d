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
