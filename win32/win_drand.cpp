
#include "win_drand.h"

#include <stdlib.h>

/* from "Summit: C Programming FAQs (section 13.21)" */

#define PRECISION 2.82e14 /* 2**48, rounded up */

double drand48()
{
	double x = 0;

	double denom = RAND_MAX + 1.;
	double need;

	for(need = PRECISION; need > 1; need /= (RAND_MAX + 1.))
	{
		x += rand() / denom;
		denom *= RAND_MAX + 1.;
	}

	return x;
}