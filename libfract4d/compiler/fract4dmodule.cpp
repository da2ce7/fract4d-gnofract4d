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


class PySite :public IFractalSite
{
public:
    PySite(
	PyObject *parameters_changed_cb_,
	PyObject *image_changed_cb_,
	PyObject *progress_changed_cb_,
	PyObject *status_changed_cb_,
	PyObject *is_interrupted_cb_)
	{
	    parameters_changed_cb = parameters_changed_cb_;
	    image_changed_cb =image_changed_cb_;
	    progress_changed_cb = progress_changed_cb_;
	    status_changed_cb = status_changed_cb_;
	    is_interrupted_cb = is_interrupted_cb_;
	    
	    Py_INCREF(parameters_changed_cb);
	    Py_INCREF(image_changed_cb);
	    Py_INCREF(progress_changed_cb);
	    Py_INCREF(status_changed_cb);
	    Py_INCREF(is_interrupted_cb);
	}

    virtual void parameters_changed()
	{
	    PyObject *args = Py_BuildValue("()");
	    PyObject *ret = PyEval_CallObject(parameters_changed_cb,args);
	    Py_XDECREF(ret);
	}
    
    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int x2, int y1, int y2)
	{
	    PyObject *args = Py_BuildValue("(iiii)",x1,x2,y1,y2);
	    PyObject *ret = PyEval_CallObject(image_changed_cb,args);
	    Py_XDECREF(ret);
	}
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress)
	{
	    double d = (double)progress;
	    PyObject *args = Py_BuildValue("(d)",d);
	    if(NULL == args)
	    {
		printf("bad progress\n");
		PyErr_Print();
	    }
	    PyObject *ret = PyEval_CallObject(progress_changed_cb,args);
	    Py_XDECREF(ret);

	}
    // one of the status values above
    virtual void status_changed(int status_val)
	{
	    assert(this != NULL && status_changed_cb != NULL);
	    printf("sc: %p %p\n",this,this->status_changed_cb);
	    if(PyErr_Occurred())
	    {
		printf("bad status 0\n");
		PyErr_Print();
	    }

	    PyObject *args = Py_BuildValue("(i)",status_val);
	    if(PyErr_Occurred())
	    {
		printf("bad status 1\n");
		PyErr_Print();
	    }

	    PyObject *ret = PyEval_CallObject(status_changed_cb,args);
	    if(PyErr_Occurred())
	    {
		printf("bad status 2\n");
		PyErr_Print();
	    }
	    Py_XDECREF(args);
	    Py_XDECREF(ret);

	}

    // return true if we've been interrupted and are supposed to stop
    virtual bool is_interrupted()
	{
	    PyObject *args = Py_BuildValue("()");
	    if(PyErr_Occurred())
	    {
		printf("bad interrupt 0\n");
		PyErr_Print();
	    }
	    PyObject *pyret = PyEval_CallObject(is_interrupted_cb,args);

	    bool ret = false;
	    if(PyInt_Check(pyret))
	    {
		long i = PyInt_AsLong(pyret);
		printf("ret: %ld\n",i);
		ret = (i != 0);
	    }

	    Py_XDECREF(pyret);
	    return ret;
	}

    ~PySite()
	{
	    printf("dtor %p\n",this);
	    Py_DECREF(parameters_changed_cb);
	    Py_DECREF(image_changed_cb);
	    Py_DECREF(progress_changed_cb);
	    Py_DECREF(status_changed_cb);
	    Py_DECREF(is_interrupted_cb);
	}
private:
    PyObject *parameters_changed_cb;
    PyObject *image_changed_cb;
    PyObject *progress_changed_cb;
    PyObject *status_changed_cb;
    PyObject *is_interrupted_cb;
};

static void
site_delete(IFractalSite *site)
{
    delete site;
}

static PyObject *
pysite_create(PyObject *self, PyObject *args)
{
    PyObject *parameters_changed_cb;
    PyObject *image_changed_cb;
    PyObject *progress_changed_cb;
    PyObject *status_changed_cb;
    PyObject *is_interrupted_cb;

    if(!PyArg_ParseTuple(
	   args,
	   "OOOOO",
	   &parameters_changed_cb,
	   &image_changed_cb,
	   &progress_changed_cb,
	   &status_changed_cb,
	   &is_interrupted_cb))
    {
	return NULL;
    }

    if(!PyCallable_Check(parameters_changed_cb) ||
       !PyCallable_Check(image_changed_cb) ||
       !PyCallable_Check(progress_changed_cb) ||
       !PyCallable_Check(status_changed_cb) ||
       !PyCallable_Check(is_interrupted_cb))
    {
	PyErr_SetString(PyExc_ValueError,"All arguments must be callable");
	return NULL;
    }

    IFractalSite *site = new PySite(
	parameters_changed_cb,
	image_changed_cb,
	progress_changed_cb,
	status_changed_cb,
	is_interrupted_cb);

    printf("pysite_create: %p\n",site);
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
	   "(dddddddddddd)iiiOOiOO",
	   &params[0],&params[1],&params[2],&params[3],
	   &params[4],&params[5],&params[6],&params[7],
	   &params[8],&params[9],&params[10],&params[11],
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

    printf("pycalc: %p\n",site);
    calc(params,eaa,maxiter,nThreads,pfo,cmap,auto_deepen,im,site);

    Py_INCREF(Py_None);
    return Py_None;
}

static void
image_delete(IImage *image)
{
    printf("delete %p\n",image);
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

    { "site_create", pysite_create, METH_VARARGS,
      "Create a new site"},

    { "calc", pycalc, METH_VARARGS,
      "Calculate a fractal image"},

    {NULL, NULL, 0, NULL}        /* Sentinel */
};

extern "C" PyMODINIT_FUNC
initfract4d(void)
{
    (void) Py_InitModule("fract4d", PfMethods);
}
