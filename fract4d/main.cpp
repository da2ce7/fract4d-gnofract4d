#include <cstdlib>

#include "fract4d.h"

#include "image.h"


int main(int argc, char **argv)
{
    IFractal *f = IFractal::create();

    image *im = new image();
    IFractalSite *site = new IFractalSite();

    im->set_resolution(640,480);

    for(int i = 1; i < argc ; ++i)
    {
	f->load_params(argv[i]);
	f->calc(site,im);
    }

    delete f;

    return EXIT_SUCCESS;
}
