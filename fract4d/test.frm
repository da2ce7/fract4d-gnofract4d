parse_error { 
  ===
}

test_circle {
loop:
z = pixel
bailout:
|z| < @bailout
default:
float param bailout
	default = 4.0
endparam
}

test_defaults {
default:
maxiter = 200
xzangle = 0.789
center = (1.0,2.0)
zwcenter = (7.1,2.9)
angle = 0.001
magn = 8.0
title = "Hello World"
float param bailout
	default = 8.0
endparam
param woggle
	default = (7.0,1.0)
endparam
}

test_simpleshape {
default:
maxiter = 1
init:
	z = pixel
bailout:
	real(z) + imag(z) < 0.0
}


test_func {
init:
	z = #zwpixel
loop:
z = @myfunc(z) + #pixel
bailout:
@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
func myfunc
	default = sqr()
endfunc
float func bailfunc
	default = cabs
endfunc
}

; a new-year's eve fractal - looks like a good torture test...

;ny04-1a            { ; Version 2002 Patchlevel 3
; reset=2002 type=formula formulafile=ny2004-4.frm
; formulaname=ny2004-4 function=sinh/sinh/ident/ident passes=1
;  center-mag=2.57336/0.749497/0.8909/1/7.5/0
;  params=-0.060358/0.53382/2.36/0.020655/0.873595/-0.48138/1/0.2012/1.5/38
;  float=y maxiter=800 inside=atan periodicity=0
;  colors=000<58>taJubJvbK<2>ydLzeLydL<55>642531421<2>100000001<56>Q_tQ`uR`\
;  v<2>SbyTczSby<61>000
;  }

ny2004-4 { ; fn1-fn4 ident = Mandelbrot 
           ; with lake transformation from Sylvie Gallet, Jan 16, 2000
           ; ---
           ; real(p1) = merging of text (function dependent)
           ; imag(p1) = idem
           ; real(p2) = diam. of backgr.fractal
           ; imag(p2) = 0-6.28 = rotation of backgr.fractal
           ; real(p3) = x-pos. of backgr.fractal
           ; imag(p3) = y-pos. of backgr.fractal
           ; ---
           ; If (B=A*C) then text is invisible, else=visible!
           ; A = real(p4), B = imag(p4), C = real(p5)
           ; -----
           ; real(p4) = diam. of fractal
           ; imag(p4) = diam. of text-fractal
           ; real(p5) = diam. & direction on x-axis of fractal
           ; -----
           ; imag(p5) = Waterlevel (0-100 % of screen hight)
           ; -----
           ; 'periodicity=0' and 'passes=1' recommended
  pp_3=(0.3,200)
    if (imag(p5) > 0 && imag(p5) <= 100)
    level = imag(p5) / 100
    ampl = real(pp_3)
    freq = imag(pp_3)
    angle = real(rotskew * pi / 180)
    exp_irot = exp(-flip(angle))
    h = 1 / real(magxmag)
    w = h / 0.75 * imag(magxmag)
    tanskew = tan(imag(rotskew * pi / 180))
    u = 2 * w * exp_irot
    v = 2 * h * (tanskew + flip(1)) * exp_irot
    z3rd = center + (-w-h*tanskew - flip(h)) * exp_irot
    z = pixel - z3rd
    b = imag(conj(u)*z) / imag(conj(u)*v)
    if (b <= level)
    dy = level - b
    z = z + 2*dy * (1+ampl*sin(freq*dy^0.2)) * v
    endif
    pixel = z + z3rd
    endif
    z=fn1(fn2(pixel))*p1
    x=real(z), y=imag(z)
chrH1 = x<-0.16646||x>-0.13646||(y<0.656&&y>0.644)&&x>-0.17846&&x<-0.12446
chra2 = abs(cabs(z+(0.09271,-0.65325))-0.01575)<0.006&&x<-0.09271||\
(abs(cabs(z+(0.08271,-0.65325))-0.01575)<0.006&&x>-0.08271)&&y>0.65325||((abs(cabs(z+(0.09271,-0.62175))-0.01575)<0.006&&x<-0.09271)||\
(abs(cabs(z+(0.08271,-0.62175))-0.01575)<0.006&&x>-0.08271))||(x>-0.09271&&x<-0.08271&&(y<0.612||(y>0.663&&y<0.675)||(y>0.6315&&y<0.6435)))||(x>-0.07296&&x<-0.06096&&y<0.65325)
chrp3 = x>-0.05096&&x<-0.03896&&y<0.675&&y>0.5625||(abs(cabs(z+(0.02021,-0.6375))-0.0315)<0.006&&x>-0.03896)
chrp4 = x>0.02729&&x<0.03929&&y<0.675&&y>0.5625||(abs(cabs(z+(-0.05804,-0.6375))-0.0315)<0.006&&x>0.03929)
xy=2.5*x
chry5 = y<xy+0.26116&&y>xy+0.22884||(y>-xy+0.93884&&y<-xy+0.97116)&&y>xy+0.22884&&y<0.675&&y>0.55
test1 = chrH1||chra2&&y>0.6||chrp3||chrp4||chry5&&y<0.7
xCN=2.5*x
chrN6 = x>-0.29573&&x<-0.28573||(x>-0.25573&&x<-0.24496)||(y>-xCN-0.18933&&y<-xCN-0.16241)
chre7 = abs(cabs(z+(0.19346,-0.4875))-0.0325)<0.005&&(x<-0.19346||y\
>0.48583||y<0.48083)||(y>0.48583&&y<0.49583&&x>-0.22596&&x<-0.16096\
)
xw=4*x
chrw8 = y<xw+0.94285&&y>xw+0.90162||(y>-xw+0.09048&&y<-xw+0.13171)&&y<0.51667||(y>-xw-0.04285&&y<-xw-0.00162)||(y<xw+0.80952&&y>xw+0.76829)&&y<0.525
xCY=2*x
chrY10 = y<xCY+0.42364&&y>xCY+0.40128||(y>-xCY+0.55636&&y<-xCY+0.57872)&&y>xCY+0.40128
chre11 = abs(cabs(z+(-0.12586,-0.4875))-0.0325)<0.005&&(x<0.12586||\
y>0.48583||y<0.48083)||(y>0.48583&&y<0.49583&&x>0.09336&&x<0.15836)
chra12 = abs(cabs(z+(-0.19861,-0.50375))-0.01625)<0.005&&x<0.19861||(abs(cabs(z+(-0.20861,-0.50375))-0.01625)<0.005&&x>0.20861)&&y>0.50375||\
((abs(cabs(z+(-0.19861,-0.47125))-0.01625)<0.005&&x<0.19861)||\
(abs(cabs(z+(-0.20861,-0.47125))-0.01625)<0.005&&x>0.20861))||\
(x>0.19861&&x<0.20861&&(y<0.46||(y>0.515&&y<0.525)||(y>0.4825&&y<0.4925\
)))||(x>0.21986&&x<0.22986&&y<0.50375)
chrr13 = x>0.24386&&x<0.25386&&y<0.525||(abs(cabs(z+(-0.2698,-0.49906))-0.02094)<0.005&&y>0.49906)
test2 = chrN6||chre7||chrw8||chrY10||chre11||chra12||chrr13&&y>0.45\
&&y<0.55
x2=2.5*x
chr214 = abs(cabs(z+(0.09317,-0.36435))-0.01935)<0.0063&&(y>0.36435\
||y>-x/1.21639+0.28775)||(y<1.21639*x+0.45714&&y>1.21639*x+0.4373&&\
y<-x/1.21639+0.28775)||y<0.3126&&x>-0.11882&&x<-0.06752
chr015 = abs(cabs(z+(0.03287,-0.36435))-0.01935)<0.0063&&y>0.36435||\
(abs(cabs(z+(0.03287,-0.32565))-0.01935)<0.0063&&y<0.32565)||(((x>\
-0.05852&&x<-0.04592)||(x>-0.01982&&x<-0.00722))&&y>0.32565&&y<0.36435)
chr016 = abs(cabs(z+(-0.02743,-0.36435))-0.01935)<0.0063&&y>0.36435\
||(abs(cabs(z+(-0.02743,-0.32565))-0.01935)<0.0063&&y<0.32565)||(((\
x>0.00178&&x<0.01438)||(x>0.04048&&x<0.05308))&&y>0.32565&&y<0.36435)
x4=1.8*x
chr417 = y<x4+0.21826&&y>x4+0.19232&&y>0.33||(x>0.09722&&x<0.10982)\
||(y>0.3174&&y<0.33&&x>0.06208&&x<0.11882)
test3 = chr214||chr015||chr016||chr417&&y>0.3&&y<0.39
test=test1||test2||test3
test0=test0&&whitesq
test0=((test0||test)==0)
f1=(1/conj(real(p5)))*(1/conj(real(p4)))*pixel
f2=(1/imag(p4))*pixel
pixel=(test==0)*f1+test*f2
z=c=fn1(fn2(pixel-p3)*(exp(p2)))
:
z=sqr(fn3(fn4(z)))+c
|z| <=4
  }

Fractint-9-21 {; Sylvie Gallet [101324,3444], 1996
               ; requires 'periodicity=0' 
  z = fn1(fn2(pixel)-fn3(0.025)^fn4(3)), x=real(z), y=imag(z)
  x1=x*1.8, x3=3*x
  ty2 = ( (y<0.025) && (y>-0.025) ) || (y>0.175)
  f = ( (x<-1.2) || ty2 ) && ( (x>-1.25) && (x<-1) )
  r = ( (x<-0.9) || ty2 ) && ( (x>-0.95) && (x<-0.8) )
  r = r || ((cabs(sqrt(|z+(0.8,-0.1)|)-0.1)<0.025) && (x>-0.8))
  r = r || (((y<(-x1-1.44)) && (y>(-x1-1.53))) && (y<0.025))
  a = (y>(x3+1.5)) || (y>(-x3-1.2)) || ((y>-0.125) && (y<-0.075))
  a = a && ((y<(x3+1.65)) && (y<(-x3-1.05)))
  c = (cabs(sqrt(|z+0.05|)-0.2)<0.025) && (x<0.05)
  t1 = ((x>0.225) && (x<0.275) || (y>0.175)) && ((x>0.1) && (x<0.4))
  i = (x>0.45) && (x<0.5)
  n = (x<0.6) || (x>0.8) || ((y>-x1+1.215) && (y<-x1+1.305))
  n = n && (x>0.55) && (x<0.85)
  t2 = ((x>1.025) && (x<1.075) || (y>0.175)) && ((x>0.9) && (x<1.2))
  test = 1 - (real(f||r||a||c||t1||i||n||t2)*real(y>-0.225)*real(y<0.225)) 
  z = 1+(0.0,-0.65)/(pixel+(0.0,.75)) :
  z2 = z*z, z4 = z2*z2, n = z4*z2-1, z = z-n/(6*z4*z)
  (|n|>=0.0001) && test
  ;SOURCE: bej012.frm
}
