#include <cstdlib>

#include "fract4d.h"

#include "image.h"

void err_cb(void *data, const char *msg, const char *detail)
{
    fprintf(stderr,"Compiler error: %s\nDetails:%s\n", msg, detail);
}

class callbacks : public IFractalSite
{
    // the parameters have changed (usually due to auto-deepening)
    virtual void parameters_changed() {};
    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int x2, int y1, int y2) {
	printf(".");
    };
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress) {};
    // one of the status values above
    virtual void status_changed(int status_val) {
	printf("status %d\n",status_val);	
    };
};

int main(int argc, char **argv)
{
    IFractal *f = IFractal::create();
    g_pCompiler = new compiler();
    g_pCompiler->set_err_callback(err_cb, NULL);
    g_pCompiler->set_cache_dir(".");
    image *im = new image();
    IFractalSite *site = new callbacks();

    im->set_resolution(640,480);

    for(int i = 1; i < argc ; ++i)
    {
	f->load_params(argv[i]);
	f->set_effective_aa(AA_FAST);
	f->calc(site,im);
	im->save("foo.tga");
    }

    delete f;

    return EXIT_SUCCESS;
}
