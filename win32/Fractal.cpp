// Fractal.cpp : Implementation of CFractal

#include "stdafx.h"
#include "FractCtl.h"
#include "Fractal.h"

/////////////////////////////////////////////////////////////////////////////
// CFractal


/* definitions of callback functions */
extern "C" void gf4d_fractal_parameters_changed(Gf4dFractal *f)
{
	//ATLTRACE(_T("Parameters Changed"));
}

extern "C" void gf4d_fractal_image_changed(Gf4dFractal *f, int x1, int x2, int y1, int y2)
{
	//ATLTRACE(_T("Image Changed"));
}

extern "C" void gf4d_fractal_progress_changed(Gf4dFractal *f, float progress)
{
	//ATLTRACE(_T("Progress Changed"));
}

extern "C" void gf4d_fractal_status_changed(Gf4dFractal *f, int status_val)
{
	//ATLTRACE(_T("Status Changed"));
}
