/* C wrapper around pf so it can be called directly from python.
   This isn't used at runtime, it's primarily for unit testing */


#include "Python.h"

#include <dlfcn.h>

#include "pf.h"
#include "cmap.h"
#include "fractFunc.h"
#include "image.h"

/* not sure why this isn't defined already */
#ifndef PyMODINIT_FUNC 
#define PyMODINIT_FUNC void
#endif


/* 
 * pointfuncs
 */

static void
pf_unload(void *p)
{
#ifdef DEBUG_CREATION
    printf("Unloading %p\n",p);
#endif
    dlclose(p);
}

static PyObject *
pf_load(PyObject *self, PyObject *args)
{
    char *so_filename;
    if(!PyArg_ParseTuple(args,"s",&so_filename))
    {
	return NULL;
    }

    void *dlHandle = dlopen(so_filename, RTLD_NOW);
#ifdef DEBUG_CREATION
    printf("Loading %p\n",dlHandle);
#endif
    if(NULL == dlHandle)
    {
	/* an error */
	PyErr_SetString(PyExc_ValueError,dlerror());
	return NULL;
    }
    return PyCObject_FromVoidPtr(dlHandle,pf_unload);
}

struct pfHandle
{
    PyObject *pyhandle;
    pf_obj *pfo;
} ;

static void
pf_delete(void *p)
{
    struct pfHandle *pfh = (struct pfHandle *)p;
#ifdef DEBUG_CREATION
    printf("deleting %p\n",pfh);
#endif
    pfh->pfo->vtbl->kill(pfh->pfo);
    Py_DECREF(pfh->pyhandle);
}

static PyObject *
pf_create(PyObject *self, PyObject *args)
{
    struct pfHandle *pfh = (pfHandle *)malloc(sizeof(struct pfHandle));
    void *dlHandle;
    PyObject *pyobj;
    pf_obj *(*pfn)(void); 
    if(!PyArg_ParseTuple(args,"O",&pyobj))
    {
	return NULL;
    }
    if(!PyCObject_Check(pyobj))
    {
	PyErr_SetString(PyExc_ValueError,"Not a valid handle");
	return NULL;
    }

    dlHandle = PyCObject_AsVoidPtr(pyobj);
    pfn = (pf_obj *(*)(void))dlsym(dlHandle,"pf_new");
    if(NULL == pfn)
    {
	PyErr_SetString(PyExc_ValueError,dlerror());
	return NULL;
    }
    pf_obj *p = pfn();
    pfh->pfo = p;
    pfh->pyhandle = pyobj;
#ifdef DEBUG_CREATION
    printf("created %p(%p)\n",pfh,pfh->pfo);
#endif
    // refcount module so it can't be unloaded before all funcs are gone
    Py_INCREF(pyobj); 
    return PyCObject_FromVoidPtr(pfh,pf_delete);
}


static PyObject *
pf_init(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyarray;
    double period_tolerance;
    double *params;
    struct pfHandle *pfh;

    if(!PyArg_ParseTuple(args,"OdO",&pyobj,&period_tolerance,&pyarray))
    {
	return NULL;
    }
    if(!PyCObject_Check(pyobj))
    {
	PyErr_SetString(PyExc_ValueError,"Not a valid handle");
	return NULL;
    }

    pfh = (struct pfHandle *)PyCObject_AsVoidPtr(pyobj);
    /* printf("pfo:%p\n",pfo); */

    if(!PySequence_Check(pyarray))
    {
	PyErr_SetString(PyExc_TypeError,
			"Argument 3 should be an array of floats");
	return NULL;
    }

    int len = PySequence_Size(pyarray);
    if(len == 0)
    {
	params = (double *)malloc(sizeof(double));
	params[0] = 0.0;
    }
    else if(len > PF_MAXPARAMS)
    {
	PyErr_SetString(PyExc_ValueError,"Too many parameters");
	return NULL;
    }
    else
    {
	int i = 0;
	params = (double *)malloc(len * sizeof(double));
	if(!params) return NULL;
	for(i = 0; i < len; ++i)
	{
	    PyObject *pyitem = PySequence_GetItem(pyarray,i);
	    if(NULL == pyitem)
	    {
		return NULL;
	    }
	    if(PyFloat_Check(pyitem))
	    {
		params[i] = PyFloat_AsDouble(pyitem);
	    }
	    else
	    {
		Py_XDECREF(pyitem);
		PyErr_SetString(PyExc_ValueError,"All params must be floats");
		free(params);
		return NULL;
	    }
	    Py_XDECREF(pyitem);
	} 
	/*finally all args are assembled */
	pfh->pfo->vtbl->init(pfh->pfo,period_tolerance,params,len);
	free(params);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pf_calc(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyret;
    double params[4];
    struct pfHandle *pfh; 
    int nIters, nNoPeriodIters,x=0,y=0,aa=0;
    int outIters=0, outFate=0;
    double outDist=0.0;

    if(!PyArg_ParseTuple(args,"O(dddd)ii|iii",
			 &pyobj,
			 &params[0],&params[1],&params[2],&params[3],
			 &nIters,&nNoPeriodIters,&x,&y,&aa))
    {
	return NULL;
    }
    if(!PyCObject_Check(pyobj))
    {
	PyErr_SetString(PyExc_ValueError,"Not a valid handle");
	return NULL;
    }

    pfh = (struct pfHandle *)PyCObject_AsVoidPtr(pyobj);
    pfh->pfo->vtbl->calc(pfh->pfo,params,
		    nIters,nNoPeriodIters,
		    x,y,aa,
		    &outIters,&outFate,&outDist);
    pyret = Py_BuildValue("iid",outIters,outFate,outDist);
    return pyret; // Python can handle errors if this is NULL
}

/* 
 * cmaps
 */
static PyObject *
cmap_create(PyObject *self, PyObject *args)
{
    /* args = an array of (index,r,g,b,a) tuples */
    PyObject *pyarray, *pyret;
    int len, i;
    cmap_t *cmap;

    if(!PyArg_ParseTuple(args,"O",&pyarray))
    {
	return NULL;
    }

    if(!PySequence_Check(pyarray))
    {
	return NULL;
    }
    
    len = PySequence_Size(pyarray);
    if(len == 0)
    {
	PyErr_SetString(PyExc_ValueError,"Empty color array");
	return NULL;
    }
    
    cmap = cmap_new(len);
    if(!cmap)
    {
	return NULL;
    }
    for(i = 0; i < len; ++i)
    {
	double d;
	int r, g, b, a;
	PyObject *pyitem = PySequence_GetItem(pyarray,i);
	if(!pyitem)
	{
	    return NULL; 
	}
	if(!PyArg_ParseTuple(pyitem,"diiii",&d,&r,&g,&b,&a))
	{
	    return NULL;
	}
	cmap_set(cmap,i,d,r,g,b,a);
	Py_DECREF(pyitem);
    }
    pyret = PyCObject_FromVoidPtr(cmap,(void (*)(void *))cmap_delete);

    return pyret;
}

static PyObject *
cmap_pylookup(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyret;
    double d;
    rgba_t color;
    cmap_t *cmap;

    if(!PyArg_ParseTuple(args,"Od", &pyobj, &d))
    {
	return NULL;
    }

    cmap = (cmap_t *)PyCObject_AsVoidPtr(pyobj);
    if(!cmap)
    {
	return NULL;
    }

    color = cmap_lookup(cmap,d);
    
    pyret = Py_BuildValue("iiii",color.r,color.g,color.b,color.a);

    return pyret;
}

#ifdef THREADS
#define GET_LOCK PyEval_RestoreThread(state)
#define RELEASE_LOCK state = PyEval_SaveThread()
#else
#define GET_LOCK
#define RELEASE_LOCK
#endif

class PySite :public IFractalSite
{
public:
    PySite(PyObject *site_)
	{
	    site = site_;

	    has_pixel_changed_method = 
		PyObject_HasAttrString(site,"pixel_changed");

	    Py_INCREF(site);
	}

    virtual void parameters_changed()
	{
	    GET_LOCK;
	    PyObject *ret = PyObject_CallMethod(
		site,
		"parameters_changed",
		NULL);
	    Py_XDECREF(ret);
	    RELEASE_LOCK;
	}
    
    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int y1, int x2, int y2)
	{
	    GET_LOCK;
	    PyObject *ret = PyObject_CallMethod(
		site,
		"image_changed",
		"iiii",x1,y1,x2,y2);
	    Py_XDECREF(ret);
	    RELEASE_LOCK;
	}
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress)
	{
	    double d = (double)progress;

	    GET_LOCK;
	    PyObject *ret = PyObject_CallMethod(
		site,
		"progress_changed",
		"d",d);
	    Py_XDECREF(ret);
	    RELEASE_LOCK;
	}
    // one of the status values above
    virtual void status_changed(int status_val)
	{
	    assert(this != NULL && status_changed_cb != NULL);
	    //printf("sc: %p %p\n",this,this->status_changed_cb);

	    GET_LOCK;
	    PyObject *ret = PyObject_CallMethod(
		site,
		"status_changed",
		"i", status_val);

	    if(PyErr_Occurred())
	    {
		printf("bad status 2\n");
		PyErr_Print();
	    }
	    Py_XDECREF(ret);
	    RELEASE_LOCK;
	}

    // return true if we've been interrupted and are supposed to stop
    virtual bool is_interrupted()
	{
	    GET_LOCK;
	    PyObject *pyret = PyObject_CallMethod(
		site,
		"is_interrupted",NULL);

	    bool ret = false;
	    if(PyInt_Check(pyret))
	    {
		long i = PyInt_AsLong(pyret);
		//printf("ret: %ld\n",i);
		ret = (i != 0);
	    }

	    Py_XDECREF(pyret);
	    RELEASE_LOCK;
	    return ret;
	}

    // pixel changed
    virtual void pixel_changed(
	const double *params, int maxIters, int nNoPeriodIters,
	int x, int y, int aa,
	double dist, int fate, int nIters,
	int r, int g, int b, int a) 
	{
	    if(has_pixel_changed_method)
	    {
		GET_LOCK;
		PyObject *pyret = PyObject_CallMethod(
		    site,
		    "pixel_changed",
		    "(dddd)iiiiidiiiiii",
		   params[0],params[1],params[2],params[3],
		   x,y,aa,
		   maxIters,nNoPeriodIters,
		   dist,fate,nIters,
		   r,g,b,a);

		Py_XDECREF(pyret);
		RELEASE_LOCK;
	    }
	};

    ~PySite()
	{
	    //printf("dtor %p\n",this);
	    Py_DECREF(site);
	}

    //PyThreadState *state;
private:
    PyObject *site;
    bool has_pixel_changed_method;
};

typedef enum
{
    PARAMS,
    IMAGE,
    PROGRESS,
    STATUS,
    PIXEL
} msg_type_t;
    
typedef struct
{
    msg_type_t type;
    int p1,p2,p3,p4;
} msg_t;

// write the callbacks to a file descriptor
class FDSite :public IFractalSite
{
public:
    FDSite(int fd_) : fd(fd_)
	{

	}

    virtual void parameters_changed()
	{
	    msg_t m = { PARAMS, 0, 0, 0, 0};
	    write(fd,&m,sizeof(m));
	}
    
    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int y1, int x2, int y2)
	{
	    msg_t m = { IMAGE };
	    m.p1 = x1; m.p2 = y1; m.p3 = x2; m.p4 = y2;
	    write(fd,&m,sizeof(m));
	}
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress)
	{
	    msg_t m = { PROGRESS };
	    m.p1 = (int) (100.0 * progress);
	    m.p2 = m.p3 = m.p4 = 0;
	    write(fd,&m,sizeof(m));
	}
    // one of the status values above
    virtual void status_changed(int status_val)
	{
	    msg_t m = { STATUS };
	    m.p1 = status_val;
	    m.p2 = m.p3 = m.p4 = 0;
	    write(fd,&m,sizeof(m));
	}

    // return true if we've been interrupted and are supposed to stop
    virtual bool is_interrupted()
	{
	    return false; // FIXME
	}

    // pixel changed
    virtual void pixel_changed(
	const double *params, int maxIters, int nNoPeriodIters,
	int x, int y, int aa,
	double dist, int fate, int nIters,
	int r, int g, int b, int a) 
	{
	    return; // FIXME
	};

    ~FDSite()
	{
	    close(fd);
	}
private:
    int fd;
};

static void
site_delete(IFractalSite *site)
{
    delete site;
}

static PyObject *
pysite_create(PyObject *self, PyObject *args)
{
    PyObject *pysite;
    if(!PyArg_ParseTuple(
	   args,
	   "O",
	   &pysite))
    {
	return NULL;
    }

    IFractalSite *site = new PySite(pysite);

    //printf("pysite_create: %p\n",site);
    PyObject *pyret = PyCObject_FromVoidPtr(site,(void (*)(void *))site_delete);

    return pyret;
}

static PyObject *
pyfdsite_create(PyObject *self, PyObject *args)
{
    int fd;
    if(!PyArg_ParseTuple(args,"i", &fd))
    {
	return NULL;
    }

    IFractalSite *site = new FDSite(fd);

    PyObject *pyret = PyCObject_FromVoidPtr(site,(void (*)(void *))site_delete);

    return pyret;
}

static PyObject *
pycalc(PyObject *self, PyObject *args)
{
    PyObject *pypfo, *pycmap, *pyim, *pysite;
    double params[N_PARAMS];
    int eaa, maxiter, nThreads;
    bool auto_deepen;
    pf_obj *pfo;
    cmap_t *cmap;
    IImage *im;
    IFractalSite *site;
 
    if(!PyArg_ParseTuple(
	   args,
	   "(ddddddddddd)iiiOOiOO",
	   &params[0],&params[1],&params[2],&params[3],
	   &params[4],&params[5],&params[6],&params[7],
	   &params[8],&params[9],&params[10],
	   &eaa,&maxiter,&nThreads,
	   &pypfo,&pycmap,
	   &auto_deepen,
	   &pyim, &pysite
	   ))
    {
	return NULL;
    }

    cmap = (cmap_t *)PyCObject_AsVoidPtr(pycmap);
    pfo = ((pfHandle *)PyCObject_AsVoidPtr(pypfo))->pfo;
    im = (IImage *)PyCObject_AsVoidPtr(pyim);
    site = (IFractalSite *)PyCObject_AsVoidPtr(pysite);
    if(!cmap || !pfo || !im || !site)
    {
	return NULL;
    }

    //((PySite *)site)->state = PyEval_SaveThread();
    calc(params,eaa,maxiter,nThreads,pfo,cmap,auto_deepen,im,site);
    //PyEval_RestoreThread(((PySite *)site)->state);

    Py_INCREF(Py_None);
    return Py_None;
}

static void
image_delete(IImage *image)
{
    //printf("delete %p\n",image);
    delete image;
}

static PyObject *
image_create(PyObject *self, PyObject *args)
{
    int x, y;

    if(!PyArg_ParseTuple(args,"ii",&x,&y))
    { 
	return NULL;
    }

    IImage *i = new image();
    i->set_resolution(x,y);

    PyObject *pyret = PyCObject_FromVoidPtr(i,(void (*)(void *))image_delete);

    return pyret;
}

static PyObject *
image_resize(PyObject *self, PyObject *args)
{
    int x, y;
    PyObject *pyim;

    if(!PyArg_ParseTuple(args,"Oii",&pyim,&x,&y))
    { 
	return NULL;
    }

    IImage *i = (IImage *)PyCObject_AsVoidPtr(pyim);
    i->set_resolution(x,y);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
image_save(PyObject *self,PyObject *args)
{
    PyObject *pyim;
    char *fname;
    if(!PyArg_ParseTuple(args,"Os",&pyim,&fname))
    {
	return NULL;
    }
    image *i = (image *)PyCObject_AsVoidPtr(pyim);
    i->save(fname);

    Py_INCREF(Py_None);
    return Py_None;
}
    
static PyObject *
image_buffer(PyObject *self, PyObject *args)
{
    PyObject *pyim;
    PyObject *pybuf;

    if(!PyArg_ParseTuple(args,"O",&pyim))
    {
	return NULL;
    }
    image *i = (image *)PyCObject_AsVoidPtr(pyim);

    pybuf = PyBuffer_FromReadWriteMemory(i->getBuffer(),i->bytes());
    Py_XINCREF(pybuf);

    return pybuf;
}

static PyMethodDef PfMethods[] = {
    {"pf_load",  pf_load, METH_VARARGS, 
     "Load a new point function shared library"},
    {"pf_create", pf_create, METH_VARARGS,
     "Create a new point function"},
    {"pf_init", pf_init, METH_VARARGS,
     "Init a point function"},
    {"pf_calc", pf_calc, METH_VARARGS,
     "Calculate one point"},

    { "cmap_create", cmap_create, METH_VARARGS,
      "Create a new colormap"},
    { "cmap_lookup", cmap_pylookup, METH_VARARGS,
      "Get a color tuple from a distance value"},

    { "image_create", image_create, METH_VARARGS,
      "Create a new image buffer"},
    { "image_resize", image_resize, METH_VARARGS,
      "Change image dimensions - data is deleted" },
    { "image_save", image_save, METH_VARARGS,
      "save an image to .tga format"},
    { "image_buffer", image_buffer, METH_VARARGS,
      "get the rgb data from the image"},

    { "site_create", pysite_create, METH_VARARGS,
      "Create a new site"},
    { "fdsite_create", pyfdsite_create, METH_VARARGS,
      "Create a new file-descriptor site"},

    { "calc", pycalc, METH_VARARGS,
      "Calculate a fractal image"},

    {NULL, NULL, 0, NULL}        /* Sentinel */
};

extern "C" PyMODINIT_FUNC
initfract4d(void)
{
    (void) Py_InitModule("fract4d", PfMethods);
}
