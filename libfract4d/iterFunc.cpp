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


iterFunc_data infoTable[] = {
    /* mandFunc */
    {
	"Mandelbrot",
	// flags
	0,
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
	NO_OVERRIDES
    },
    /* mandelBarFunc : z <- conj(z)^2 + c */
    { 
	"Mandelbar",
	// flags
	HAS_X2 | HAS_Y2,
	// bailFunc
	BAILOUT_MAG,
	// decl code
	"double atmp",
	// iter code
	"p[Y] = -p[Y];"
	"p[X2] = p[X] * p[X];"
	"p[Y2] = p[Y] * p[Y];"
	"atmp = p[X2] - p[Y2] + p[CX];"
	"p[Y] = 2.0 * p[X] * p[Y] + p[CY];"
	"p[X] = atmp",
	DEFAULT_SIMPLE_CODE,
	NO_OPTIONS,
	NO_OVERRIDES
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
	newtonOverrideValues
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
	novaOverrideValues
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
    virtual void setOption(int n, std::complex<double> val) 
        {
            if(n < 0 || n >= m_data->nOptions) return; 
            m_a[n] = val;
	    std::cout << "set" << m_a[n] << "\n";  
        }
    virtual std::complex<double> *opts()
        {
            return m_a;
        }
    virtual std::complex<double> getOption(int n) const
        {
            if(n < 0 || n >= m_data->nOptions) return 0.0;
	    std::cout << "get" << m_a[n] << "\n";
            return m_a[n];
        }
    virtual const char *optionName(int n) const
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
    virtual void reset(double *params)
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
		std::cout << m_a[i] << "\n";
	    }	    
	}
    virtual e_bailFunc preferred_bailfunc(void)
        {
            return m_data->preferred_bailFunc;
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
    virtual std::string decl_code() const { 
	return m_data->decl_code; 
    };
    virtual std::string iter_code() const {
        return m_data->iter_code;
    }

    virtual std::string ret_code() const { 
	return m_data->ret_code; 
    };
    virtual std::string save_iter_code() const {
        return m_data->save_iter_code;
    }
    virtual std::string restore_iter_code() const {
        return m_data->restore_iter_code;
    }
    
    virtual void get_code(std::map<std::string,std::string>& code_map) const 
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

#if 0



// z <- ( re(z) > 0 ? (z - 1) * c : (z + 1) * c)
class barnsleyFunc: public iterImpl<barnsleyFunc,0>
{
public:
    enum {  FLAGS = NO_UNROLL };
    barnsleyFunc() : iterImpl<barnsleyFunc,0>(name()) {};

    static char *name()
        {
            return "Barnsley Type 1";
        }
    std::string decl_code() const 
        { 
            return "double x_cy, x_cx, y_cy, y_cx";
        }
    std::string iter_code() const 
        { 
            return 
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
                "}";
        }
};


class barnsley2Func: public iterImpl<barnsley2Func,0>
{
public:
    enum {  FLAGS = NO_UNROLL };
    barnsley2Func() : iterImpl<barnsley2Func,0>(name()) {};

    static const char *name()
        {
            return "Barnsley Type 2";
        }
    std::string decl_code() const 
        { 
            return "double x_cy, x_cx, y_cy, y_cx";
        }
    std::string iter_code() const 
        { 
            return 
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
                "}";
        }
};


// z <- lambda * z * ( 1 - z)
class lambdaFunc: public iterImpl<lambdaFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    lambdaFunc() : iterImpl<lambdaFunc,0>(name()) {};

    static const char *name()
        {
            return "Lambda";
        }
    virtual void reset(double *params)
        {
            iterImpl<lambdaFunc,0>::reset(params);
            // override some defaults for a prettier picture
            params[XCENTER] = 1.0;
            params[ZCENTER] = 0.5;
            params[MAGNITUDE] = 8.0;
        }
    std::string decl_code() const 
        { 
            return "double tx, ty";
        }
    std::string iter_code() const 
        { 
            return
                "p[X2] = p[X] * p[X]; p[Y2] = p[Y] * p[Y];"
    
                /* t <- z * (1 - z) */
                "tx = p[X] - p[X2] + p[Y2];"
                "ty = p[Y] - 2.0 * p[X] * p[Y];"
    
                "p[X] = p[CX] * tx - p[CY] * ty;"
                "p[Y] = p[CX] * ty + p[CY] * tx";
        }
};

// z <- (|x| + i |y|)^2 + c
class shipFunc: public iterImpl<shipFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    shipFunc() : iterImpl<shipFunc,0>(name()) {};

    static const char *name()
        {
            return "Burning Ship";
        }
    std::string iter_code() const 
        { 
            return
                "p[X] = fabs(p[X]);"
                "p[Y] = fabs(p[Y]);"

                /* same as mbrot from here */
                "p[X2] = p[X] * p[X];"
                "p[Y2] = p[Y] * p[Y];"
                "atmp = p[X2] - p[Y2] + p[CX];"
                "p[Y] = 2.0 * p[X] * p[Y] + p[CY];"
                "p[X] = atmp";
        }
    std::string decl_code() const 
        { 
            return "double atmp";
        }
    virtual void reset(double *params)
        {
            iterImpl<shipFunc,0>::reset(params);
            // override some defaults for a prettier picture
            params[XCENTER] = -0.5;
            params[YCENTER] = -0.5;
        }
};

// z <- a[0] * (|x| + i |y|)^2 + a[1] * (|x| + i|y|) + a[2] * c
class buffaloFunc: public iterImpl<buffaloFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    buffaloFunc() : iterImpl<buffaloFunc,0>(name()) {}

    static const char *name()
        {
            return "Buffalo";
        }
    std::string decl_code() const 
        { 
            return "double atmp";
        }
    std::string iter_code() const
        {
            return 
                "p[X] = fabs(p[X]);"
                "p[Y] = fabs(p[Y]);"
   
                "p[X2] = p[X] * p[X];"
                "p[Y2] = p[Y] * p[Y];"
                "atmp = p[X2] - p[Y2] - p[X] + p[CX];"
                "p[Y] = 2.0 * p[X] * p[Y] - p[Y] + p[CY];"
                "p[X] = atmp";
        }
    virtual void reset(double *params)
        {
            iterImpl<buffaloFunc,0>::reset(params);
            // override some defaults for a prettier picture
            params[MAGNITUDE] = 6.0;
        }
};

// z <- z^3 + c
class cubeFunc : public iterImpl<cubeFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    cubeFunc() : iterImpl<cubeFunc,0>(name()) {}

    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
    std::string decl_code() const 
        { 
            return "double atmp";
        }
    std::string iter_code() const
        {
            return 
                "p[X2] = p[X] * p[X];"
                "p[Y2] = p[Y] * p[Y];"
                "atmp = p[X2] * p[X] - 3.0 * p[X] * p[Y2] + p[CX];"
                "p[Y] = 3.0 * p[X2] * p[Y] - p[Y2] * p[Y] + p[CY];"
                "p[X] = atmp";
        }
};


// computes z^a + c
class ztoaFunc : public iterImpl<ztoaFunc,1>
{
public:
    enum { FLAGS = USE_COMPLEX };
    ztoaFunc() : iterImpl<ztoaFunc,1>(name()) {
    }
    static const char *name()
        {
            return "ManZPower";
        }
    std::string decl_code() const 
        { 
            return 
                "std::complex<double> z(p[X],p[Y]);" 
                "std::complex<double> c(p[CX],p[CY]);";
        }
    std::string iter_code() const
        {
            return
                "z = pow(z,a[0]) + c;";
        }
    std::string ret_code() const
        {
            return "p[X] = z.real(); p[Y] = z.imag()";
        }
    std::string save_iter_code() const
        {
            return "std::complex<double> last_z = z";
        }
    std::string restore_iter_code() const
        {
            return "z = last_z";
        }
    const char *optionName(int i) const
        {
            if(i != 0)  return NULL;
            return "a";
        }
    virtual void reset(double *params)
        {
            reset_opts();
            iterImpl<ztoaFunc,1>::reset(params);
            params[ZCENTER] = 1.0E-10; // avoid weird behavior with pow(0,...)
        }
private:
    void reset_opts()
        {
            // default is z^4 + c
            a[0] = std::complex<double>(4.0,0.0);
        }

};


// generalised quadratic mandelbrot
// computes a[0] * z^2 + a[1] * z + a[2] * c
class quadFunc : public iterImpl<quadFunc,3>
{
public:
    enum { FLAGS = USE_COMPLEX };
    quadFunc() : iterImpl<quadFunc,3>(name()) {
        reset_opts();
    }
    static const char *name()
        {
            return "Quadratic";
        }
    std::string decl_code() const 
        { 
            return 
                "std::complex<double> z(p[X],p[Y]);" 
                "std::complex<double> c(p[CX],p[CY]);";
        }
    std::string iter_code() const
        {
            return 
		"z = (a[0] * z + a[1]) * z + a[2] * c;";
	    //"z = (1.0 * z + 1.0) * z + 1.0 * c;";
        }
    std::string ret_code() const
        {
            return "p[X] = z.real(); p[Y] = z.imag()";
        }
    std::string save_iter_code() const
        {
            return "std::complex<double> last_z = z";
        }
    std::string restore_iter_code() const
        {
            return "z = last_z";
        }
    const char *optionName(int i) const
        {
            static const char *optNames[] =
            {
                "a", "b", "c"
            };
            if(i < 0 || i >= 3) return NULL;
            return optNames[i];
        }

    virtual void reset(double *params)
        {
            reset_opts();
            iterImpl<quadFunc,3>::reset(params);
            params[XCENTER]=-0.75;
        }
private:
    void reset_opts()
        {
            // default is z^2 - z + c
            a[0] = std::complex<double>(1.0,0.0);
            a[1] = std::complex<double>(1.0,0.0);
            a[2] = std::complex<double>(1.0,0.0);
        }
};

#endif

#if 0
// Taylor series approximation to exp
class taylorFunc : public iterImpl<taylorFunc,0>
{
#define CUBE_DECL double atmp
#define CUBE_ITER 
    p[X2] = p[X] * p[X];
    p[Y2] = p[Y] * p[Y];
    atmp = p[X2] * p[X] - 3.0 * p[X] * p[Y2] + p[CX];
    p[Y] = 3.0 * p[X2] * p[Y] - p[Y2] * p[Y] + p[CY];
    p[X] = atmp

public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    cubeFunc() : iterImpl<cubeFunc,0>(name()) {}

    ITER_DECLS(CUBE_DECL, CUBE_ITER)
    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
};
#endif

#if 0
#define CTOR_TABLE_ENTRY(className) \
    { className::name(), className::create }

ctorInfo ctorTable[] = {
    CTOR_TABLE_ENTRY(mandFunc),

    CTOR_TABLE_ENTRY(quadFunc),
    CTOR_TABLE_ENTRY(cubeFunc),
    CTOR_TABLE_ENTRY(ztoaFunc),

    CTOR_TABLE_ENTRY(lambdaFunc),
    CTOR_TABLE_ENTRY(mandelBarFunc),

    CTOR_TABLE_ENTRY(shipFunc),
    CTOR_TABLE_ENTRY(buffaloFunc),
    CTOR_TABLE_ENTRY(barnsleyFunc),
    CTOR_TABLE_ENTRY(barnsley2Func),
    CTOR_TABLE_ENTRY(novaFunc),
    CTOR_TABLE_ENTRY(newtFunc),

    { NULL, NULL}
};

#endif

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

const char **iterFunc_names()
{ 
    static const char **nameTable = createNameTable();

    return nameTable;
}

// factory method to make new iterFuncs
iterFunc *iterFunc::create(const char *name)
{
    if(!name) return NULL;

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
            iterFunc *f = iterFunc::create(value.c_str());
            if(f)
            {
                s >> *f;
            }
            return f;
        }
    }
    return NULL;
}
