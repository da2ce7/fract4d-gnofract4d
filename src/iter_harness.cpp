#include "pointFunc.h"
#include "colorizer_public.h"

#include <complex>

extern "C"
{

void *create_pointfunc(
    void *handle,
    double bailout,
    double period_tolerance,
    std::complex<double> *params,
    colorizer *pcf,        
    e_colorFunc outerCfType,
    e_colorFunc innerCfType);
}

int main()
{

    colorizer *pCizer = colorizer_new(COLORIZER_RGB);
    
    dvec4 params(-2.0,-1.0,0.0,0.0);
    pointFunc *pFunc = (pointFunc *)create_pointfunc(
            NULL,4.0,1.0E-17,NULL,pCizer,COLORFUNC_FLAT, COLORFUNC_ZERO);

    struct rgb pixel;
    int nIters;
    (*pFunc)(params,1000,1000,&pixel,&nIters);
}
