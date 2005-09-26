/* C wrapper around a few GTK functions I can't get at in PyGTK (darn it)
 */

#undef NDEBUG

#include "Python.h"

#include <assert.h>
#include <errno.h>

#include "gtk/gtk.h"
#include "gconf/gconf.h"

#include "image.h"

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

    PyObject *pyRet = PyString_FromString(setting);
    gconf_engine_unref(confEngine);
    return pyRet;
 err:
    gconf_engine_unref(confEngine);
    return NULL;
}


static PyObject *
image_save(PyObject *self, PyObject *args)
{
    PyObject *pyimage;
    char *filename = NULL;
    if(!PyArg_ParseTuple(args,"Os",&pyimage,&filename))
    {
	return NULL;
    }

    image *im = (image *)PyCObject_AsVoidPtr(pyimage);

    if(NULL == im)
    {
	/* an error */
	PyErr_SetString(PyExc_ValueError,"invalid image object");
	return NULL;
    }

    gchar *ext = strrchr(filename,'.');
    gchar *type = NULL;
    if(NULL != ext)
    {
	if(strcasecmp(ext,".jpg")==0 || strcasecmp(ext,".jpeg")==0)
	{ 
	    type = "jpeg";
	}
	else if(strcasecmp(ext, ".png")==0)
	{
	    type = "png";
	}
	else
	{
	    PyErr_Format(PyExc_ValueError,
			 "Unsupported file format '%s'. "
			 "Please use .JPG or .PNG.",
			 ext);
	    return NULL;
	}
    }
    else
    {
	PyErr_Format(PyExc_ValueError,
		     "No file extension in '%s'. Can't determine file format. "
		     "Please use .JPG or .PNG.",
		     filename);
	return NULL;
    }
    
    GdkPixbuf * pixbuf = gdk_pixbuf_new_from_data(
        (unsigned char *)im->getBuffer(),
        GDK_COLORSPACE_RGB,
	FALSE,
	8,
        im->Xres(),
        im->Yres(),
	im->row_length(),
	NULL, // no destroynotify fn - is this correct?
	NULL);

    bool ok = gdk_pixbuf_save(pixbuf, filename, type, NULL, NULL);
    gdk_pixbuf_unref(pixbuf);

    if(!ok)
    {
	PyErr_Format(
	    PyExc_IOError,
	    "Unable to save image to '%s' : %s",
	    filename,
	    strerror(errno));
	return NULL;
    } 

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Methods[] = {
    {"image_save",  image_save, METH_VARARGS, 
     "Write an image to disk using gtk pixbuf functions"},

    {"get_gconf_string", get_gconf_string, METH_VARARGS, 
     "Returns a user setting, according to gconf"},
 
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

extern "C" PyMODINIT_FUNC
initfract4dguic(void)
{
    (void) Py_InitModule("fract4dguic", Methods);
}
