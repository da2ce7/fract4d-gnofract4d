#include <cstdlib>

#include "fract4d.h"

#include "image.h"


class callbacks : public IFractalSite, public ICompilerSite
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

    // compiler warns us of an error
    void err_callback(const char *msg, const char *detail) {
	fprintf(stderr,"Compiler error: %s\nDetails:%s\n", msg, detail);
    }

};

int main(int argc, char **argv)
{
    IFractalSite *site = new callbacks();
    IFractal *f = IFractal::create();
    g_pCompiler = ICompiler::create((ICompilerSite *)site);

    void *h = g_pCompiler->compile(f);
    printf("%p\n",h);
    //g_pCompiler->set_cache_dir(".");
    image *im = new image();

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
