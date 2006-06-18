// All the profilers I've tried produce nonsensical results when
// using multiple threads and/or dynamically loading code. This standalone
// program is used to make profiling easier.

// A chunk of code that computes a bunch of points.

#include "fract_public.h"
#include "pf.h"
#include "image.h"
#include "image_public.h"
#include "fractFunc.h"

int
main()
{
    IFractalSite doNothingSite;

    ListColorMap *cmap = new ListColorMap();
    cmap->init(256);
    for(int i = 0; i < 256; ++i)
    {
	int x = i % 2 ? 179 : 49;
	cmap->set(i,1.0/256.0, x, x, x, 255);
    }
    
    pf_obj *pfo = pf_new();

    s_param *pfoParams = new s_param[7];

    pfoParams[0].gradient = cmap; //gradient
    pfoParams[1].doubleval = 4.0; //bailout
    pfoParams[2].doubleval = 1.0; //cf0 density
    pfoParams[3].doubleval = 0.0; //cf0 offset
    pfoParams[4].doubleval = 4.0; //cf0 bailout
    pfoParams[5].doubleval = 1.0; //cf1 density
    pfoParams[6].doubleval = 0.0; // offset

    pfo->vtbl->init(
	pfo,1.0e-12,
	pfoParams,
	7);

    image *im = new image();
    im->set_resolution(4096,4096,-1,-1);

    double params[] = { 
	0.0, 0.0, 0.0, 0.0,
	4.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    calc(
	params,
	AA_FAST,
	32767,
	1,
	pfo,
	cmap,
	true,
	false,
	true,
	true,
	RENDER_TWO_D,
	-1,
	im,
	&doNothingSite);

    FILE *outfile = fopen("prof.tga", "wb");
    ImageWriter *iw = ImageWriter::create(FILE_TYPE_TGA, outfile, im);
    iw->save_header();
    iw->save_tile();
    iw->save_footer();
    fclose(outfile);
}
