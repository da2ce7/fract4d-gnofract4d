/* function objects which perform individual iterations of a fractal function */

#include "iterFunc.h"
#include "io.h"

#include <cstddef>
#include <iostream>
#include <string>
#include <cmath>
#include <complex>

#define IO_DECLS(className) \
    friend std::ostream& operator<< <>(std::ostream& s, const className& m); \
    friend std::istream& operator>> <>(std::istream& s, className& m); \
    std::ostream& put(std::ostream& s) const { return s << *this; } \
    std::istream& get(std::istream& s) { return s >> *this;  } 

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

/* This class eases the implementation of fractal types */
template<class T, int NOPTIONS>
class iterImpl : public iterFunc
{
protected:
    const char *m_type;
    double a[NOPTIONS];
public:
    iterImpl(const char *type) : m_type(type) {}

    int nOptions() const
        { 
            return NOPTIONS; 
        }
    virtual void setOption(int n, double val) 
        {
            if(n < 0 || n >= NOPTIONS) return;
            a[n] = val;
        }
    virtual double getOption(int n) const
        {
            if(n < 0 || n >= NOPTIONS) return 0.0; 
            return a[n];
        }
    virtual const char *optionName(int n) const
        {
            return NULL;            
        }
    const char *type() const
        {
            return m_type;
        }
    int flags() const
        {
            return T::FLAGS;
        }
    /* utility functions */

    /* copy constructor */
    iterFunc *clone() const
        {
            return new T((const T&)*this);
        }
    /* because you can't get a function pointer to a constructor (for no
       good reason that I can determine), we have a static member function
       called create which performs the construction for us. */
    static iterFunc *create()
        {
            return new T();
        }
    /* equality */
    bool operator==(const iterFunc &c) const
        {
            const T *p = dynamic_cast<const T *>(&c);
            if(!p) return false;
            for(int i = 0; i < NOPTIONS; ++i)
            {
                if(p->a[i] != a[i]) return false;
            }
            return true;
        }
    IO_DECLS(iterImpl)
};

template<class T, int NOPTIONS>
std::ostream& 
operator<<(std::ostream& s, const iterImpl<T,NOPTIONS>& m) 
{ 
    write_field(s,FIELD_FUNCTION);
    s << m.type() << "\n";
    for(int i = 0; i < NOPTIONS; ++i)
    {
        s << m.optionName(i) << "=" << m.getOption(i) << "\n";
    }
    s << SECTION_STOP << "\n"; 
    return s; 
} 

template<class T, int NOPTIONS>
std::istream& 
operator>>(std::istream& s, iterImpl<T, NOPTIONS>& m) 
{ 
    while(s)
    {
        std::string name,val;
        
        if(!read_field(s,name,val))
        {
            break;
        }

        for(int i = 0; i < NOPTIONS; ++i)
        {
            if(0 == strcmp(name.c_str(),m.optionName(i)))
            {
                std::istrstream vs(val.c_str());
                double opt;
                vs >> opt;
                m.setOption(i,opt);
                break;
            }
        }
        if(SECTION_STOP == name) break;
    }
    return s; 
}

#ifdef HAVE_GMP
#define GMP_FUNC_OP \ 
    void operator()(gmp::f *p) const \
        { \
            calc<gmp::f>(p);\
        }
#else
#define GMP_FUNC_OP
#endif

#define ITER_DECLS(decl, func) \
    template<class T>inline void calc(T *p) const \
        { \
            decl; \
            func; \
        }\
    template<class T>inline void calc8(T *p) const \
        { \
            decl; \
            func; func; func; func; func; func; func; func; \
        }\
    void operator()(double *p) const \
        {\
            calc<double>(p);\
        }\
    GMP_FUNC_OP \
    void iter8(double *p) const \
        { \
            calc8<double>(p); \
        } 

// z <- z^2 +c
class mandFunc : public iterImpl<mandFunc,0>
{
public:
    enum { FLAGS = HAS_X2 | HAS_Y2 };
    mandFunc() : iterImpl(name()) {}

#define MAND_DECL T atmp
#define MAND_ITER \
    p[X2] = p[X] * p[X]; \
    p[Y2] = p[Y] * p[Y]; \
    atmp = p[X2] - p[Y2] + p[CX]; \
    p[Y] = 2.0 * p[X] * p[Y] + p[CY]; \
    p[X] = atmp

    ITER_DECLS(MAND_DECL,MAND_ITER)

    static char *name()
        {
            return "Mandelbrot";
        }
};

// z <- (z^3-1)/3 z^2 + c
class novaFunc : public iterImpl<novaFunc,0>
{
#define NOVA_DECL complex<double> z(p[X],p[Y]), c(p[CX],p[CY])
#define NOVA_ITER z = z - (z*z*z - 1.0)/(3.0 * z * z) + c

public:
    enum {  FLAGS = 0 };
    novaFunc() : iterImpl(name()) {};

    ITER_DECLS(NOVA_DECL,NOVA_ITER)
    static char *name()
        {
            return "Nova";
        }
};
                               
// z <- ( re(z) > 0 ? (z - 1) * c : (z + 1) * c)
class barnsleyFunc: public iterImpl<barnsleyFunc,0>
{
#define BARNSLEY_DECL double x_cy, x_cx, y_cy, y_cx
#define BARNSLEY_ITER \
    x_cy = p[X] * p[CY]; x_cx = p[X] * p[CX];\
    y_cy = p[Y] * p[CY]; y_cx = p[Y] * p[CX];\
    \
    if(p[X] >= 0) \
    { \
        p[X] = (x_cx - p[CX] - y_cy ); \
        p[Y] = (y_cx - p[CY] + x_cy ); \
    } \
    else \
    { \
        p[X] = (x_cx + p[CX] - y_cy); \
        p[Y] = (y_cx + p[CY] + x_cy); \
    }

public:
    enum {  FLAGS = 0 };
    barnsleyFunc() : iterImpl(name()) {};

    ITER_DECLS(BARNSLEY_DECL, BARNSLEY_ITER)
    static char *name()
        {
            return "Barnsley Type 1";
        }
};

class barnsley2Func: public iterImpl<barnsley2Func,0>
{
#define BARNSLEY2_DECL double x_cy, x_cx, y_cy, y_cx
#define BARNSLEY2_ITER \
    x_cy = p[X] * p[CY]; x_cx = p[X] * p[CX]; \
    y_cy = p[Y] * p[CY]; y_cx = p[Y] * p[CX]; \
    \
    if(p[X]*p[CY] + p[Y]*p[CX] >= 0) \
    { \
        p[X] = (x_cx - p[CX] - y_cy ); \
        p[Y] = (y_cx - p[CY] + x_cy ); \
    } \
    else \
    { \
        p[X] = (x_cx + p[CX] - y_cy);\
        p[Y] = (y_cx + p[CY] + x_cy); \
    }

public:
    enum {  FLAGS = 0 };
    barnsley2Func() : iterImpl(name()) {};

    ITER_DECLS(BARNSLEY2_DECL, BARNSLEY2_ITER)
    static const char *name()
        {
            return "Barnsley Type 2";
        }
};

// z <- lambda * z * ( 1 - z)
class lambdaFunc: public iterImpl<lambdaFunc,0>
{
#define LAMBDA_DECL double tx, ty;
#define LAMBDA_ITER \
    p[X2] = p[X] * p[X]; p[Y2] = p[Y] * p[Y]; \
    \
    /* t <- z * (1 - z) */ \
    tx = p[X] - p[X2] + p[Y2]; \
    ty = p[Y] - 2.0 * p[X] * p[Y]; \
    \
    p[X] = p[CX] * tx - p[CY] * ty; \
    p[Y] = p[CX] * ty + p[CY] * tx

public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    lambdaFunc() : iterImpl(name()) {};

    ITER_DECLS(LAMBDA_DECL, LAMBDA_ITER)
    static const char *name()
        {
            return "Lambda";
        }
};

// z <- (|x| + i |y|)^2 + c
class shipFunc: public iterImpl<shipFunc,0>
{
#define SHIP_DECL double atmp;
#define SHIP_ITER \
    p[X] = fabs(p[X]); \
    p[Y] = fabs(p[Y]); \
    /* same as mbrot from here */ \
    p[X2] = p[X] * p[X]; \
    p[Y2] = p[Y] * p[Y]; \
    atmp = p[X2] - p[Y2] + p[CX]; \
    p[Y] = 2.0 * p[X] * p[Y] + p[CY]; \
    p[X] = atmp

public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    shipFunc() : iterImpl(name()) {};

    ITER_DECLS(SHIP_DECL, SHIP_ITER)
    static const char *name()
        {
            return "Burning Ship";
        }
};

// z <- (|x| + i |y|)^2 + (|x| + i|y|) + c
class buffaloFunc: public iterImpl<buffaloFunc,0>
{
#define BUFFALO_DECL double atmp
#define BUFFALO_ITER \
    p[X] = fabs(p[X]); \
    p[Y] = fabs(p[Y]); \
    \
    p[X2] = p[X] * p[X]; \
    p[Y2] = p[Y] * p[Y]; \
    atmp = p[X2] - p[Y2] - p[X] + p[CX]; \
    p[Y] = 2.0 * p[X] * p[Y] - p[Y] + p[CY]; \
    p[X] = atmp

public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    buffaloFunc() : iterImpl(name()) {}

    ITER_DECLS(BUFFALO_DECL, BUFFALO_ITER)
    static const char *name()
        {
            return "Buffalo";
        }
};

// z <- z^3 + c
class cubeFunc : public iterImpl<cubeFunc,0>
{
#define CUBE_DECL double atmp
#define CUBE_ITER  \
    p[X2] = p[X] * p[X]; \
    p[Y2] = p[Y] * p[Y]; \
    atmp = p[X2] * p[X] - 3.0 * p[X] * p[Y2] + p[CX]; \
    p[Y] = 3.0 * p[X2] * p[Y] - p[Y2] * p[Y] + p[CY]; \
    p[X] = atmp

public:
    enum {  FLAGS = 0 };
    cubeFunc() : iterImpl(name()) {}

    ITER_DECLS(CUBE_DECL, CUBE_ITER)
    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
};

// generalised quadratic mandelbrot
// computes a[0] * z^2 + a[1] * z + a[2] * c
// a[] array should be an array of complex numbers, really
class quadFunc : public iterImpl<quadFunc,3>
{
#define QUAD_DECL double atmp;
#define QUAD_ITER \
    p[X2] = p[X] * p[X]; \
    p[Y2] = p[Y] * p[Y]; \
    atmp = a[0] * (p[X2] - p[Y2]) + a[1] * p[X] + a[2] * p[CX]; \
    p[Y] = a[0] * (2.0 * p[X] * p[Y]) + a[1] * p[Y] + a[2] * p[CY]; \
    p[X] = atmp

public:
    enum { FLAGS = HAS_X2 | HAS_Y2 };
    quadFunc() : iterImpl(name()) {
        // default is z^2 - z + c
        a[0] = 1.0;
        a[1] = 1.0;
        a[2] = 1.0;
    }

    ITER_DECLS(QUAD_DECL, QUAD_ITER)
    static const char *name()
        {
            return "Quadratic";
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
};

#define CTOR_TABLE_ENTRY(className) \
    { className::name(), className::create }

ctorInfo ctorTable[] = {
    CTOR_TABLE_ENTRY(mandFunc),
    CTOR_TABLE_ENTRY(shipFunc),
    CTOR_TABLE_ENTRY(buffaloFunc),
    CTOR_TABLE_ENTRY(cubeFunc),
    CTOR_TABLE_ENTRY(quadFunc),
    CTOR_TABLE_ENTRY(barnsleyFunc),
    CTOR_TABLE_ENTRY(barnsley2Func),
    CTOR_TABLE_ENTRY(lambdaFunc),
    CTOR_TABLE_ENTRY(novaFunc),
    { NULL, NULL}
};


const ctorInfo *iterFunc_names()
{ 
    return ctorTable;
}

// factory method to make new iterFuncs
iterFunc *iterFunc_new(const char *name)
{
    if(!name) return NULL;

    ctorInfo *p = ctorTable;
    while(p->name)
    {
        if(0 == strcmp(name,p->name))
        {
            return p->ctor();
        }
        p++;
    }
    // unknown type
    return NULL;
}

// deserialize an iterFunc from a stream

iterFunc *iterFunc_read(std::istream& s)
{
    std::string name, value;

    while(s)
    {
        read_field(s,name,value);
    
        if(FIELD_FUNCTION == name)
        {
            iterFunc *f = iterFunc_new(value.c_str());
            if(f)
            {
                s >> *f;
            }
            return f;
        }
    }
    return NULL;
}
