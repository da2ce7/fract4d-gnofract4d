#include <cstdlib>

#include "fract_public.h"

int main(int argc, char **argv)
{
    IFractal *f = IFractal::create();

    delete f;

    return EXIT_SUCCESS;
}
