/* C wrapper around a few GTK functions I can't get at in PyGTK (darn it)
 */

#undef NDEBUG

#include "Python.h"

#include <assert.h>
#include <errno.h>

#include "gconf/gconf.h"

/* not sure why this isn't defined already */
#ifndef PyMODINIT_FUNC 
#define PyMODINIT_FUNC void
#endif


/* ask gconf what user's preferred mail editor is */
static PyObject *
get_gconf_string(PyObject *self, PyObject *args)
{
    char *path = NULL;
    if(!PyArg_ParseTuple(args, "s", &path))
    {
	return NULL;
    }

    GConfEngine *confEngine = gconf_engine_get_default();
    PyObject *pyRet = NULL;

    if(NULL==confEngine)
    {
	PyErr_SetString(PyExc_EnvironmentError,"Couldn't get gconf engine");
	return NULL;
    }

    GError *err = NULL;
    gchar *setting = gconf_engine_get_string(
	confEngine,
	path,
	&err);

    if(NULL != err)
    {
	PyErr_SetString(PyExc_EnvironmentError,err->message);
	goto err;
    }

    if(NULL == setting)
    {
	PyErr_SetString(PyExc_EnvironmentError,"No such setting found");
	goto err;
    }

    pyRet = PyString_FromString(setting);
    gconf_engine_unref(confEngine);
    return pyRet;
 err:
    gconf_engine_unref(confEngine);
    return NULL;
}

static PyMethodDef Methods[] = {
    {"get_gconf_string", get_gconf_string, METH_VARARGS, 
     "Returns a user setting, according to gconf"},
 
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

extern "C" PyMODINIT_FUNC
initfract4dguic(void)
{
    (void) Py_InitModule("fract4dguic", Methods);
}
