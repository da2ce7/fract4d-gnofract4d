/* function objects which perform individual iterations of a fractal function */

#include "iterFunc.h"
#include "io.h"

#include <cstddef>
#include <iostream>
#include <iomanip> // setprecision
#include <string>  // strstream
#include <cmath>
#include <complex>
#include <sstream>
#include <cassert>

#include "Python.h"

#define FIELD_FUNCTION "function"

// forward static calls of << to appropriate virtual function
std::ostream& 
operator<<(std::ostream& s, const iterFunc& iter)
{
    return iter.put(s);
}

std::istream&
operator>>(std::istream& s, iterFunc& iter)
{
    return iter.get(s);
}


typedef struct 
{
    const char * name;
    const int flags;
    const e_bailFunc preferred_bailFunc;
    const char * decl_code;
    const char * iter_code;
    const char * ret_code;
    const char * save_iter_code;
    const char * restore_iter_code;
    int nOptions;
    const char **optNames;
    const double *optDefaults;
    int nParamOverrides;
    const param_t *paramOverrideNames;
    const double *paramOverrideValues;
    int nCriticalValues;
    const char *criticalValueCode;
} iterFunc_data;

const char *newtonOptNames[] = { "a" };
const double newtonOptDefaults[] = {
    3.0, 0.0 // a
};
const param_t newtonOverrides[] = { XZANGLE, YWANGLE, XCENTER };
const double newtonOverrideValues[] = { M_PI/2.0, M_PI/2.0, 0.1};

const char *novaOptNames[] = { "a", "b", "c" };
const double novaOptDefaults[] = {
    1.0, 0.0, // a
    1.0, 0.0, // b
    3.0, 0.0  // c
};

const param_t novaOverrides[] = { ZCENTER, MAGNITUDE };
const double novaOverrideValues[] = { 1.0, 3.0};

const char *mandelBarOptNames[] = { "a" };
const double mandelBarOptDefaults[] = {
    2.0, 0.0 // power
};

const param_t mandelBarOverrides[] = { ZCENTER };
const double mandelBarOverrideValues[] = { 1.0E-10 };

const char *cubicOptNames[] = { "a" };
const double cubicOptDefaults[] = {
    0.0, 0.0 //a
};

const param_t lambdaOverrides[] = { XCENTER, ZCENTER, MAGNITUDE };
const double lambdaOverrideValues[] = { 1.0, 0.5, 8.0 };

const param_t shipOverrides[] = { XCENTER, YCENTER};
const double shipOverrideValues[] = { -0.5, -0.5 };

const param_t buffaloOverrides[] = { MAGNITUDE};
const double buffaloOverrideValues[] = { 6.0 };

const char *mandelPowerOptNames[] = { "a" };
const double mandelPowerOptDefaults[] = {
    4.0, 0.0 //a
};

const param_t mandelPowerOverrides[] = { ZCENTER};
const double mandelPowerOverrideValues[] = { 1.0E-10 };

const char *quadraticOptNames[] = { "a", "b", "c" };
const double quadraticOptDefaults[] = {
    1.0, 0.0, // a
    1.0, 0.0, // b
    1.0, 0.0  // c
};

const param_t magnetOverrides[] = { XCENTER, MAGNITUDE };
const double magnetOverrideValues[] = { 2.0, 8.0 };

const param_t magnet2Overrides[] = { XCENTER, MAGNITUDE };
const double magnet2OverrideValues[] = { 2.0, 3.0 };

#define NO_OPTIONS 0, NULL, NULL
#define NO_OVERRIDES 0, NULL, NULL

#define DEFAULT_COMPLEX_RET_CODE  "p[X] = z.real(); p[Y] = z.imag()"
#define DEFAULT_COMPLEX_SAVE_CODE "std::complex<double> last_z = z"
#define DEFAULT_COMPLEX_RESTORE_CODE "z = last_z"
#define DEFAULT_COMPLEX_CODE \
    DEFAULT_COMPLEX_RET_CODE, \
    DEFAULT_COMPLEX_SAVE_CODE, \
    DEFAULT_COMPLEX_RESTORE_CODE

#define DEFAULT_SIMPLE_RET_CODE ""
#define DEFAULT_SIMPLE_SAVE_CODE "T lastx = p[X]; T lasty = p[Y]"
#define DEFAULT_SIMPLE_RESTORE_CODE "p[X] = lastx; p[Y] = lasty"
#define DEFAULT_SIMPLE_CODE \
    DEFAULT_SIMPLE_RET_CODE, \
    DEFAULT_SIMPLE_SAVE_CODE, \
    DEFAULT_SIMPLE_RESTORE_CODE

#define DEFAULT_CRITICAL_VALUES 1,"cv[0] = std::complex<double>(0.0)"

iterFunc_data infoTable[] = {
    /* mandFunc */
    {
	"Mandelbrot",
	// flags
	NO_UNROLL,
	// bailFunc
	BAILOUT_MAG,
	// decl code
	"double atmp",
	// iter code
	"p[X2] = p[X] * p[X];"
	"p[Y2] = p[Y] * p[Y];"
	"atmp = p[X2] - p[Y2] + p[CX];"
	"p[Y] = 2.0 * p[X] * p[Y] + p[CY];"
	"p[X] = atmp",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	NO_OVERRIDES,
	DEFAULT_CRITICAL_VALUES
    },
    /* quadratic mandelbrot: z <- A z^2 + B z + C c */
    {
	"Quadratic",
	USE_COMPLEX | NO_UNROLL, //flags
	BAILOUT_MAG,
	// decl code
	"std::complex<double> z(p[X],p[Y]);" 
	"std::complex<double> c(p[CX],p[CY]);",
	// iter code
	"z = (a[0] * z + a[1]) * z + a[2] * c;",
	DEFAULT_COMPLEX_CODE,
	3,
	quadraticOptNames,
	quadraticOptDefaults,
	NO_OVERRIDES,
	DEFAULT_CRITICAL_VALUES
    },
    /* cubic mandelbrot: z <- z^3 -3 A z^2 + c */
    {
	"Cubic Mandelbrot",
	USE_COMPLEX | NO_UNROLL, //flags
	BAILOUT_MAG,
	// decl code
	"std::complex<double> z(p[X],p[Y]) , c(p[CX],p[CY])",
	// iter code
	"z = z * z * ( z - 3.0 * a[0]) + c",
	DEFAULT_COMPLEX_CODE,
	1,
	cubicOptNames,
	cubicOptDefaults,
	NO_OVERRIDES,
	2,
	"cv[0] = -a[0]; cv[1] = a[0]"
    },
    /* mandelBarFunc : z <- conj(z)^2 + c */
    { 
	"Mandelbar",
	// flags
	USE_COMPLEX | NO_UNROLL,
	// bailFunc
	BAILOUT_MAG,
	// decl code
	"std::complex<double> z(p[X],p[Y]) , c(p[CX],p[CY])",
	// iter code
	" z = pow(conj(z),a[0]) + c",
	DEFAULT_COMPLEX_CODE,
	1,
	mandelBarOptNames,
	mandelBarOptDefaults,
	1,
	mandelBarOverrides,
	mandelBarOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* mandelPower: z <- z^A + c */
    {
	"ManZPower",
	USE_COMPLEX, //flags
	BAILOUT_MAG,
	// decl code
	"std::complex<double> z(p[X],p[Y]);" 
	"std::complex<double> c(p[CX],p[CY]);",
	// iter code
	"z = pow(z,a[0]) + c;",
	DEFAULT_COMPLEX_CODE,
	1,
	mandelPowerOptNames,
	mandelPowerOptDefaults,
	1,
	mandelPowerOverrides,
	mandelPowerOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* barnsley t1: z <- ( re(z) > 0 ? (z - 1) * c : (z + 1) * c) */
    {
	"Barnsley Type 1",
	NO_UNROLL,
	BAILOUT_MAG,
	"T x_cy, x_cx, y_cy, y_cx",
	//iter code
	"x_cy = p[X] * p[CY]; x_cx = p[X] * p[CX];"
	"y_cy = p[Y] * p[CY]; y_cx = p[Y] * p[CX];"
	
	"if(p[X] >= 0)"
	"{"
	"p[X] = (x_cx - p[CX] - y_cy );"
	"p[Y] = (y_cx - p[CY] + x_cy );"
	"}"
	"else"
	"{"
	"p[X] = (x_cx + p[CX] - y_cy);"
	"p[Y] = (y_cx + p[CY] + x_cy);"
	"}",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	NO_OVERRIDES,
	DEFAULT_CRITICAL_VALUES
    },
    /* barnsley t2 */
    {
	"Barnsley Type 2",
	NO_UNROLL,
	BAILOUT_MAG,
	"T x_cy, x_cx, y_cy, y_cx",
	//iter code
	"x_cy = p[X] * p[CY]; x_cx = p[X] * p[CX];"
	"y_cy = p[Y] * p[CY]; y_cx = p[Y] * p[CX]; "
    
	"if(p[X]*p[CY] + p[Y]*p[CX] >= 0) "
	"{" 
	    "p[X] = (x_cx - p[CX] - y_cy );"
	    "p[Y] = (y_cx - p[CY] + x_cy );"
	"}" 
	"else"
	"{" 
	    "p[X] = (x_cx + p[CX] - y_cy);"
	    "p[Y] = (y_cx + p[CY] + x_cy);" 
	"}",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	NO_OVERRIDES,
	DEFAULT_CRITICAL_VALUES
    },
    /* barnsley t3 */
    {
	"Barnsley Type 3",
	NO_UNROLL,
	BAILOUT_MAG,
	"T xy;",
	//iter code
	"p[X2] = p[X] * p[X];"
	"p[Y2] = p[Y] * p[Y];"
	"xy = p[X] * p[Y];"
    
	"if(p[X] > 0)"
	"{" 
	    "p[X] = p[X2] - p[Y2] - 1.0;"
	    "p[Y] = xy * 2.0;"
	"}" 
	"else"
	"{" 
	    "p[Y] = xy * 2.0 + p[CY] * p[X];"
	    "p[X] = p[X2] - p[Y2] - 1.0 + p[CX] * p[X];"
	"}",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	NO_OVERRIDES,
	DEFAULT_CRITICAL_VALUES
    },
    /* buffalo: z <- a[0] * (|x| + i |y|)^2 + a[1] * (|x| + i|y|) + a[2] * c */
    {
	"Buffalo",
	NO_UNROLL,
	BAILOUT_MAG,
	"T atmp",
	//iter code
	"p[X] = fabs(p[X]);"
	"p[Y] = fabs(p[Y]);"
   
	"p[X2] = p[X] * p[X];"
	"p[Y2] = p[Y] * p[Y];"
	"atmp = p[X2] - p[Y2] - p[X] + p[CX];"
	"p[Y] = 2.0 * p[X] * p[Y] - p[Y] + p[CY];"
	"p[X] = atmp",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	1,
	buffaloOverrides,
	buffaloOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* burning ship */
    {
	"Burning Ship",
	0,
	BAILOUT_MAG,
	"T atmp",
	//iter code
	"p[X] = fabs(p[X]);"
	"p[Y] = fabs(p[Y]);"
	
	/* same as mbrot from here */
	"p[X2] = p[X] * p[X];"
	"p[Y2] = p[Y] * p[Y];"
	"atmp = p[X2] - p[Y2] + p[CX];"
	"p[Y] = 2.0 * p[X] * p[Y] + p[CY];"
	"p[X] = atmp",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	2,
	shipOverrides,
	shipOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* lambda */
    {
	"Lambda",
	NO_UNROLL,
	BAILOUT_MAG,
	"T tx, ty",
	//iter code
	"p[X2] = p[X] * p[X]; p[Y2] = p[Y] * p[Y];"
    
	/* t <- z * (1 - z) */
	"tx = p[X] - p[X2] + p[Y2];"
	"ty = p[Y] - 2.0 * p[X] * p[Y];"
    
	"p[X] = p[CX] * tx - p[CY] * ty;"
	"p[Y] = p[CX] * ty + p[CY] * tx",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	3,
	lambdaOverrides,
	lambdaOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* Magnet 1: z <- ((z^2 + c - 1)/(2z + c -2))^2 */
    {
	"Magnet",
	USE_COMPLEX | NO_UNROLL,
	BAILOUT_MAG,
	"std::complex<double> z(p[X],p[Y]);"
	"std::complex<double> c(p[CX],p[CY]);",
	//iter code
	"z = (z * z + c - 1.0)/(2.0 * z + c - 2.0);"
	"z *= z;",
	DEFAULT_COMPLEX_CODE,
	NO_OPTIONS,
	2,
	magnetOverrides,
	magnetOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* Magnet 2: z <- ((z^3 + 3(c-1)*z + (c-1)*(c-2))/
                      (3z^2 + 3(c-2)^2+ (c-1)(c-2) + 1))^2 */
    {
	"Magnet 2",
	USE_COMPLEX | NO_UNROLL,
	BAILOUT_MAG,
	"std::complex<double> z(p[X],p[Y]);"
	"std::complex<double> c(p[CX],p[CY]), cm1, cm2;",
	//iter code
	"cm1 = c - 1.0; cm2 = c - 2.0;"
	"z = (z * z * z + 3.0 * cm1 * z + cm1 * cm2)/"
	     "(3.0 * z * z + 3.0 * cm2 * cm2 + cm1 * cm2 + 1.0);"
	"z *= z;",
	DEFAULT_COMPLEX_CODE,
	NO_OPTIONS,
	2,
	magnet2Overrides,
	magnet2OverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* newtFunc */
    {
	"Newton",
	// flags
	USE_COMPLEX,
	// bailFunc
	BAILOUT_DIFF,
	// decl code
	"std::complex<double> z(p[X],p[Y]) , c(p[CX],p[CY]), n_minus_one(a[0] - 1.0)",
	// iter code
	"z = z - (pow(z,a[0]) - 1.0)/ (a[0] * pow(z,n_minus_one))",
	// ret code, save iter code, restore iter code
	DEFAULT_COMPLEX_CODE,
	1,
	newtonOptNames,
	newtonOptDefaults,
	3,
	newtonOverrides,
	newtonOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* novaFunc: z <- (Az^3-B)/C z^2 + c */
    {
	"Nova",
	// flags
	USE_COMPLEX | NO_UNROLL,
	// bailFunc
	BAILOUT_DIFF,
	// decl code
	"std::complex<double> z(p[X],p[Y]), c(p[CX],p[CY])",
	// iter code
	"z = z - (a[0] * z*z*z - a[1])/(a[2] * z * z) + c",
	DEFAULT_COMPLEX_CODE,
	3,
	novaOptNames,
	novaOptDefaults,
	2,
	novaOverrides,
	novaOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },
    /* tetrate: z <- c^z */
    {
	"Tetrate",
	USE_COMPLEX | NO_UNROLL, //flags
	BAILOUT_MAG,
	// decl code
	"std::complex<double> z(p[X],p[Y]);" 
	"std::complex<double> c(p[CX],p[CY]);",
	// iter code
	"z = pow(c,z);",
	DEFAULT_COMPLEX_CODE,
	NO_OPTIONS,
	1,
	mandelPowerOverrides,
	mandelPowerOverrideValues,
	DEFAULT_CRITICAL_VALUES
    },

    /* sentinel value */
    {
	NULL, // name
	0, // flags
	BAILOUT_MAG, // bailFunc
	NULL, // decl code
	NULL, // iter code
	NULL, // ret code
	NULL, // save iter code
	NULL, // restore iter code
	NO_OPTIONS,
	NO_OVERRIDES
    }
};


/* This class eases the implementation of fractal types 
   T is the type of the actual fractal subclass, used for boring things 
       like cloning
   NOPTIONS is the number of parameters the fractal has */

class iterImpl : public iterFunc
{
protected:
    iterFunc_data *m_data;
    std::complex<double> *m_a;

public:
    iterImpl(iterFunc_data *data) : m_data(data), m_a(NULL) {
	if(m_data->nOptions > 0)
	{
	    m_a = new std::complex<double>[m_data->nOptions];
	}
	reset_opts();
    }
    ~iterImpl() { 
	delete[] m_a; 
    }
    int nOptions() const
        { 
            return m_data->nOptions;
        }
    void setOption(int n, std::complex<double> val) 
        {
            if(n < 0 || n >= m_data->nOptions) return; 
            m_a[n] = val;
        }
    std::complex<double> *opts()
        {
            return m_a;
        }
    std::complex<double> getOption(int n) const
        {
            if(n < 0 || n >= m_data->nOptions) return 0.0;
            return m_a[n];
        }
    const char *optionName(int n) const
        {
	    if(n < 0 || n >= m_data->nOptions) return NULL;
            return m_data->optNames[n];
        }
    const char *type() const
        {
            return m_data->name;
        }
    int flags() const
        {
            return m_data->flags;
        }
    void reset(double *params)
        {
            /* suitable defaults for most types */
            // FIXME : duplicated in fractal.cpp
            params[XCENTER] = 0.0;
            params[YCENTER] = 0.0;
            params[ZCENTER] = 0.0;
            params[WCENTER] = 0.0;
            
            params[MAGNITUDE] = 4.0;
            params[BAILOUT] = 4.0;
            for(int i = XYANGLE; i < ZWANGLE+1; i++) 
	    {
                params[i] = 0.0;
            }
	    // override appropriate values
	    for(int i = 0; i < m_data->nParamOverrides; ++i)
	    {
		params[m_data->paramOverrideNames[i]] = 
		    m_data->paramOverrideValues[i];
	    }

	    reset_opts(); 
        }
    void reset_opts()
	{
	    for(int i = 0; i < m_data->nOptions; ++i) 
	    {
		assert(m_a != NULL);
		m_a[i] = std::complex<double>(
		    m_data->optDefaults[2*i],m_data->optDefaults[2*i+1]);
	    }	    
	}
    e_bailFunc preferred_bailfunc(void)
        {
            return m_data->preferred_bailFunc;
        }
    int nCriticalValues() const 
	{
	    return m_data->nCriticalValues;
	}
    /* utility functions */

    /* copy constructor & friends */
    void copy(const iterImpl& source)
	{
	    m_data = source.m_data; 
	    delete[] m_a; m_a = NULL;	    
	    if(nOptions() > 0)
	    {
		m_a = new std::complex<double>[nOptions()];
		for(int i = 0; i < nOptions(); ++i)
		{
		    m_a[i] = source.m_a[i];
		}
	    }

	}
    iterImpl(const iterImpl& source)
	{
	    m_a = NULL;
	    copy(source);
	}
    iterImpl& operator=(const iterImpl& source)
	{   
	    if(!(source == *this))
	    {
		copy(source);
	    }
	    return *this;
	}
    iterFunc *clone() const
        {
            return new iterImpl(*this);
        }
    /* equality */
    bool operator==(const iterFunc &c) const
        {
            const iterImpl *p = dynamic_cast<const iterImpl *>(&c);
            if(!p) return false; // a different class altogether

	    // is this a different kind of fractal? 
	    if(p->m_data != m_data) return false; 

	    // different option values?
            for(int i = 0; i < nOptions(); ++i)
            {
                if(p->m_a[i] != m_a[i]) return false;
            }
            return true;
        }
    std::string decl_code() const { 
	return m_data->decl_code; 
    };
    std::string iter_code() const {
        return m_data->iter_code;
    }

    std::string ret_code() const { 
	return m_data->ret_code; 
    };
    std::string save_iter_code() const {
        return m_data->save_iter_code;
    }
    std::string restore_iter_code() const {
        return m_data->restore_iter_code;
    }
    std::string cv_code() const {
	return m_data->criticalValueCode;
    }
    void get_code(std::map<std::string,std::string>& code_map) const 
        {
            code_map["ITER"]=iter_code();
            code_map["DECL"]=decl_code();
            code_map["RET"]= ret_code();
            std::ostringstream os; 
            os << nOptions();
            code_map["N_OPTIONS"]= os.str();
            code_map["SAVE_ITER"]=save_iter_code();
            code_map["RESTORE_ITER"]=restore_iter_code();
            code_map["XPOS"]= flags() & USE_COMPLEX ? "z.real()" : "p[X]";
            code_map["YPOS"]= flags() & USE_COMPLEX ? "z.imag()" : "p[Y]";
	    code_map["CXPOS"] = flags() & USE_COMPLEX ? "c.real()" : "p[CX]";
	    code_map["CYPOS"] = flags() & USE_COMPLEX ? "c.imag()" : "p[CY]";
	    code_map["SETCV"] = cv_code();
        }
    
    friend std::ostream& operator<< (std::ostream& s, const iterImpl& m);
    friend std::istream& operator>> (std::istream& s, iterImpl& m);
    std::ostream& put(std::ostream& s) const { return s << *this; } 
    std::istream& get(std::istream& s) { return s >> *this;  } 

};

std::ostream& 
operator<<(std::ostream& s, const iterImpl& m) 
{ 
    write_field(s,FIELD_FUNCTION);
    s << m.type() << "\n";
    s << std::setprecision(20);
    for(int i = 0; i < m.nOptions(); ++i)
    {
        s << m.optionName(i) << "=" << m.getOption(i) << "\n";
    }
    s << SECTION_STOP << "\n"; 
    return s; 
} 

std::istream& 
operator>>(std::istream& s, iterImpl& m) 
{ 
    while(s)
    {
        std::string name,val;
        
        if(!read_field(s,name,val))
        {
            break;
        }

        for(int i = 0; i < m.nOptions(); ++i)
        {
            if(0 == strcmp(name.c_str(),m.optionName(i)))
            {
                std::istringstream vs(val.c_str());
                std::complex<double> opt;
                vs >> opt;
                m.setOption(i,opt);
                break;
            }
        }
        if(SECTION_STOP == name) break;
    }
    return s; 
}



class iterFuncFactory
{
private:
    bool m_ok;
    PyObject *pClass;
    PyObject *pCompiler;
    PyObject *pModule;

public:
    bool ok() const { return m_ok; };
    iterFuncFactory();
    ~iterFuncFactory();
};


iterFuncFactory::iterFuncFactory()
{
    m_ok = false;
    pModule = pCompiler = pClass = NULL;
    Py_Initialize(); // FIXME can this go wrong?

    PyObject *pName = PyString_FromString("fc");
    assert(pName);

    pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    PyObject *pDict = NULL, 
	*pArgs = NULL; 

    if(!pModule) goto error;


    pDict = PyModule_GetDict(pModule);
    if(!pDict) goto error;

    pClass = PyDict_GetItemString(pDict, "Compiler");
    if(!pClass) goto error;

    pArgs = PyTuple_New(0);
    if(!pArgs) goto error;

    pCompiler = PyInstance_New(pClass,pArgs, NULL);
    if(!pCompiler) goto error;
    
    m_ok = true;
 error:
    if(PyErr_Occurred())
    {
	PyErr_Print();
    }
    Py_XDECREF(pModule);
    Py_XDECREF(pArgs);
    Py_XDECREF(pCompiler);
}

iterFuncFactory::~iterFuncFactory()
{
    Py_XDECREF(pModule);
    Py_XDECREF(pCompiler);
    Py_Finalize();
}

static const char **createNameTable()
{
    int nNames = sizeof(infoTable)/sizeof(infoTable[0]);
    const char **names = new const char *[ nNames + 1 ];

    for(int i = 0; i < nNames; ++i)
    {
	names[i] = infoTable[i].name;
    }
    return names;
}

const char **iterFunc::names()
{ 
    static const char **nameTable = createNameTable();

    return nameTable;
}

#if 0
bool 
iterFunc::load_file(const char *filename)
{


}
#endif

static 
bool ensure_initialized()
{
    static iterFuncFactory *factory = new iterFuncFactory();
    return factory->ok();
}


// factory method to make new iterFuncs
iterFunc *iterFunc::create(const char *name, const char *filename)
{
    if(!name) return NULL;
    if(!ensure_initialized())
    {
	return NULL;
    }
    

    iterFunc_data *p = infoTable;
    while(p->name)
    {
        if(0 == strcmp(p->name,name))
        {
            return new iterImpl(p);
        }
        p++;
    }
    // unknown type
    return NULL;
}

// deserialize an iterFunc from a stream
// without knowing its type

iterFunc *iterFunc::read(std::istream& s)
{
    std::string name, value;

    while(s)
    {
        read_field(s,name,value);
    
        if(FIELD_FUNCTION == name)
        {
            iterFunc *f = iterFunc::create(value.c_str(),NULL);
            if(f)
            {
                s >> *f;
            }
            return f;
        }
    }
    return NULL;
}
