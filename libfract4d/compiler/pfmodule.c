/* C wrapper around pf so it can be called directly from python.
   This isn't used at runtime, it's primarily for unit testing */


#include "Python.h"

#include "pf.h"

static PyObject *
pf_create(PyObject * /* self */, PyObject * /*args*/)
{
    pf_obj *p = pf_new();
    return Py_CObject_FromVoidPtr(p,pf_delete);
}

static void
pf_delete(void *p)
{
    pf_obj *pfo = (pf_obj *)p;
    printf("deleting %p\n",pfo); 
    pfo->kill(pfo);
}
