#include "soi.h"

void
soi_mandel_iter(double *p, double *temp)
{
    temp[S_X] = p[S_X] * p[S_X];
    temp[S_Y] = p[S_Y] * p[S_Y];
    double atmp = temp[S_X] - temp[S_Y] + temp[S_CX];
    p[S_Y] = 2.0 * p[S_X] * p[S_Y] + temp[S_CY];
    p[S_X] = atmp;
}

bool
soi_mag_bailout(double *squares, double bailout)
{
    return (squares[S_X] + squares[S_Y] > bailout);
}

/* calculate the parametric quadratic polynomial which passes through 
   t = 0, x = x0
   t = 1/2, x = x1
   t = 1, x = x2

   if f(t) = at^2 + bt + c, this gives
   a = 2 x2 - 4x1 + 2x0 , b = 4x1 - x2 - 3x0, c = x0
*/

double 
interpolate(double x0, double x1, double x2, double t)
{
    double a =  2 * x2 - 4 * x1 + 2 * x0;
    double b = -1 * x2 + 4 * x1 - 3 * x0; 
    double c = x0;

    return (a * t + b)*t + c; // Horner eval
}

/* since we only call interpolate for t = 1/4 & t = 3/4, 
 * the fns below are a possible optimization I haven't bothered 
 * to implement yet 
 */

/* calculate above function for t = 1/4 */
double 
interpquarter(double x0, double x1, double x2)
{
    return (3 * x0 + 6 * x1 - x2)/8;
}

/* do both parts of a complex number */
void
c_interpquarter(double z0[2], double z1[2], double z2[2], double *z)
{
    z[0] = interpquarter(z0[0],z1[0],z2[0]);
    z[1] = interpquarter(z0[1],z1[1],z2[1]);
}

/* interpolate for t = 3/4 */
double 
interpthreequarter(double x0, double x1, double x2)
{
    return (3 * x2 + 6 * x1 - x0)/8;
}

void
c_interpthreequarter(double z0[2], double z1[2], double z2[2], double *z)
{
    z[0] = interpthreequarter(z0[0],z1[0],z2[0]);
    z[1] = interpthreequarter(z0[1],z1[1],z2[1]);
}
