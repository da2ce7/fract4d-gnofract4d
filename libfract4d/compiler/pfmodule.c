/* C wrapper around pf so it can be called directly from python.
   This isn't used at runtime, it's primarily for unit testing */


#include "Python.h"

#include <dlfcn.h>

#include "pf.h"

/* not sure why this isn't defined already */
#ifndef PyMODINIT_FUNC 
#define PyMODINIT_FUNC void
#endif

static void
pf_unload(void *p)
{
    /* printf("Unloading %p\n",p); */
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
    /* printf("deleting %p\n",pfh); */
    pfh->pfo->vtbl->kill(pfh->pfo);
    Py_DECREF(pfh->pyhandle);
}

static PyObject *
pf_create(PyObject *self, PyObject *args)
{
    struct pfHandle *pfh = malloc(sizeof(struct pfHandle));
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

    pfh = PyCObject_AsVoidPtr(pyobj);
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
	params = malloc(sizeof(double));
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
	params = malloc(len * sizeof(double));
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

    pfh = PyCObject_AsVoidPtr(pyobj);
    pfh->pfo->vtbl->calc(pfh->pfo,params,
		    nIters,nNoPeriodIters,
		    x,y,aa,
		    &outIters,&outFate,&outDist);
    pyret = Py_BuildValue("iid",outIters,outFate,outDist);
    return pyret; // Python can handle errors if this is NULL
}

static PyMethodDef PfMethods[] = {
    {"load",  pf_load, METH_VARARGS, 
     "Load a new point function shared library"},
    {"create", pf_create, METH_VARARGS,
     "Create a new point function"},
    {"init", pf_init, METH_VARARGS,
     "Init a point function"},
    {"calc", pf_calc, METH_VARARGS,
     "Calculate one point"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpf(void)
{
    (void) Py_InitModule("pf", PfMethods);
}
