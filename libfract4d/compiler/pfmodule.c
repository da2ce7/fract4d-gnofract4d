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

static void
pf_delete(void *p)
{
    pf_obj *pfo = (pf_obj *)p;
    /* printf("deleting %p\n",pfo);  */
    pfo->vtbl->kill(pfo);
}

static PyObject *
pf_create(PyObject *self, PyObject *args)
{
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
    return PyCObject_FromVoidPtr(p,pf_delete);
}

static PyMethodDef PfMethods[] = {
    {"load",  pf_load, METH_VARARGS, 
     "Load a new point function shared library"},
    {"create", pf_create, METH_VARARGS,
     "Create a new point function"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpf(void)
{
    (void) Py_InitModule("pf", PfMethods);
}
