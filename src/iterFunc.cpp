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

/* This class eases the implementation of fractal types which 
   have no options */

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
    const char *type() const
        {
            return m_type;
        }
    int flags() const
        {
            return T::FLAGS;
        }
    iterFunc *clone() const
        {
            return new T((const T&)*this);
        }
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
    s << SECTION_STOP << "\n"; 
    return s; 
} 

template<class T, int NOPTIONS>
std::istream& 
operator>>(std::istream& s, iterImpl<T, NOPTIONS>& m) 
{ 
    /* don't need to read anything - just eat lines until SECTION_STOP */
    while(s)
    {
        std::string line;
        std::getline(s,line);

        if(SECTION_STOP == line) break;
    }
    return s; 
}

// z <- z^2 +c
class mandFunc : public iterImpl<mandFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    mandFunc() : iterImpl(name()) {}

#define ITER \
            p[X2] = p[X] * p[X]; \
            p[Y2] = p[Y] * p[Y]; \
            atmp = p[X2] - p[Y2] + p[CX]; \
            p[Y] = 2.0 * p[X] * p[Y] + p[CY]; \
            p[X] = atmp

    template<class T>inline void calc(T *p) const
        {
            T atmp;
            ITER;
        }
    void operator()(double *p) const
        {
            calc<double>(p);
        }
    void iter8(double *p) const
        {
            double atmp;

            ITER;
            ITER;
            ITER;
            ITER;
            ITER;
            ITER;
            ITER;
            ITER;                
#undef ITER
        }
#ifdef HAVE_GMP
    void operator()(gmp::f *p) const
        {
            calc<gmp::f>(p);        
        }
#endif
    static char *name()
        {
            return "Mandelbrot";
        }
};

// z <- (z^3-1)/3 z^2 + c
class novaFunc : public iterImpl<novaFunc,0>
{
#define ITER z = z - (z*z*z - 1.0)/(3.0 * z * z) + c
public:
    enum {  FLAGS = 0 };
    novaFunc() : iterImpl(name()) {};
    void operator()(double *p) const
        {
            complex<double> z(p[X],p[Y]), c(p[CX],p[CY]);

            ITER;
            p[X] = z.real(); p[Y] = z.imag();
        }
    void iter8(double *p) const
        {
            complex<double> z(p[X],p[Y]), c(p[CX],p[CY]);
    
            ITER; ITER; ITER; ITER; 
            ITER; ITER; ITER; ITER;
            p[X] = z.real(); p[Y] = z.imag();
        }
    static char *name()
        {
            return "Nova";
        }
#undef ITER
};
                               
// z <- ( re(z) > 0 ? (z - 1) * c : (z + 1) * c)
class barnsleyFunc: public iterImpl<barnsleyFunc,0>
{
public:
    enum {  FLAGS = 0 };
    barnsleyFunc() : iterImpl(name()) {};
    void operator()(double *p) const
        {
            double x_cy, x_cx, y_cy, y_cx;

#define ITER \
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

            ITER;
        }
    void iter8(double *p) const 
        {
            double x_cy, x_cx, y_cy, y_cx;

            ITER; ITER; ITER; ITER;
            ITER; ITER; ITER; ITER;
        }
    static char *name()
        {
            return "Barnsley Type 1";
        }
};

#undef ITER

// 
class barnsley2Func: public iterImpl<barnsley2Func,0>
{
#define ITER \
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
    void operator()(double *p) const
        {
            double x_cy, x_cx, y_cy, y_cx;

            ITER;
        }
    void iter8(double *p) const 
        {
            double x_cy, x_cx, y_cy, y_cx;

            ITER; ITER; ITER; ITER;
            ITER; ITER; ITER; ITER;
        }
    static const char *name()
        {
            return "Barnsley Type 2";
        }
#undef ITER
};

// z <- lambda * z * ( 1 - z)
class lambdaFunc: public iterImpl<lambdaFunc,0>
{
#define ITER \
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
    void operator()(double *p) const
        {
            double tx, ty;
            ITER;
        }
    void iter8(double *p) const 
        {
            double tx, ty;
            ITER; ITER; ITER; ITER;
            ITER; ITER; ITER; ITER;
        }
    static const char *name()
        {
            return "Lambda";
        }
#undef ITER
};

// z <- (|x| + i |y|)^2 + c
class shipFunc: public iterImpl<shipFunc,0>
{
#define ITER \
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
    void operator()(double *p) const 
        {
            double atmp;
            ITER;
        }
    void iter8(double *p) const 
        {
            double atmp;
            ITER; ITER; ITER; ITER;
            ITER; ITER; ITER; ITER;
        }
    static const char *name()
        {
            return "Burning Ship";
        }
#undef ITER
};

// z <- (|x| + i |y|)^2 + (|x| + i|y|) + c
class buffaloFunc: public iterImpl<buffaloFunc,0>
{
#define ITER \
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
    virtual void operator()(double *p) const
        {
            double atmp;
            ITER;
        }
    void iter8(double *p) const 
        {
            double atmp;
            ITER; ITER; ITER; ITER;
            ITER; ITER; ITER; ITER;
        }
    static const char *name()
        {
            return "Buffalo";
        }
#undef ITER
};

// z <- z^3 + c
class cubeFunc : public iterImpl<cubeFunc,0>
{
#define ITER  \
    p[X2] = p[X] * p[X]; \
    p[Y2] = p[Y] * p[Y]; \
    atmp = p[X2] * p[X] - 3.0 * p[X] * p[Y2] + p[CX]; \
    p[Y] = 3.0 * p[X2] * p[Y] - p[Y2] * p[Y] + p[CY]; \
    p[X] = atmp

public:
    enum {  FLAGS = 0 };
    cubeFunc() : iterImpl(name()) {}
    virtual void operator()(double *p) const
        {
            double atmp;
            ITER;
        }    
    void iter8(double *p) const 
        {
            double atmp;
            ITER;ITER;ITER;ITER;
            ITER;ITER;ITER;ITER;
        }
    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
#undef ITER
};

// generalised quadratic mandelbrot
// computes a[0] * z^2 + a[1] * z + a[2] * c
// a[] array should be an array of complex numbers, really
class quadFunc : public iterImpl<quadFunc,3>
{
#define ITER \
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
    virtual void operator()(double *p) const
        {
            double atmp;
            ITER; 
        }
    void iter8(double *p) const 
        {
            double atmp;
            ITER; ITER; ITER; ITER; 
            ITER; ITER; ITER; ITER; 
        }
    static char *name()
        {
            return "Quadratic";
        }
    const char *type() const 
        {
            return name();
        }
    IO_DECLS(quadFunc)
};

#define FIELD_QF1 "a"
#define FIELD_QF2 "b"
#define FIELD_QF3 "c"

std::ostream& operator<<(std::ostream& s, const quadFunc& f)
{
    write_field(s, FIELD_FUNCTION);
    s << f.type() << "\n";
    write_field(s, FIELD_QF1);
    s << f.a[0] << "\n";
    write_field(s, FIELD_QF2);
    s << f.a[1] << "\n";
    write_field(s, FIELD_QF3);    
    s << f.a[2] << "\n";
    s  << SECTION_STOP << "\n";
    return s;
} 

std::istream& 
operator>>(std::istream& s, quadFunc& f)
{
    while(s)
    {
        std::string name, value;
        read_field(s,name,value);

        std::istrstream vs(value.c_str());
        if(FIELD_QF1 == name)
            vs >> f.a[0];
        else if(FIELD_QF2 == name)
            vs >> f.a[1];
        else if(FIELD_QF3 == name)
            vs >> f.a[2];
        else if(SECTION_STOP == name)
            break;
    }
    return s;
}

const char * const *iterFunc_names()
{
    static const char *names[] =
    {
        mandFunc::name(),
        shipFunc::name(),
        buffaloFunc::name(),
        cubeFunc::name(),
        quadFunc::name(),
        barnsleyFunc::name(),
        barnsley2Func::name(),
        lambdaFunc::name(),
        novaFunc::name(),
        NULL
    };

    return names;
}

// factory method to make new iterFuncs
iterFunc *iterFunc_new(const char *name)
{
    if(!name) return NULL;

    if(0 == strcmp(name,mandFunc::name()))
        return new mandFunc;
    if(0 == strcmp(name,shipFunc::name()))
        return new shipFunc;
    if(0 == strcmp(name,buffaloFunc::name()))
        return new buffaloFunc;
    if(0 == strcmp(name,cubeFunc::name()))
        return new cubeFunc;
    if(0 == strcmp(name,quadFunc::name()))
        return new quadFunc;
    if(0 == strcmp(name,barnsleyFunc::name()))
        return new barnsleyFunc;
    if(0 == strcmp(name,lambdaFunc::name()))
        return new lambdaFunc;
    if(0 == strcmp(name,barnsley2Func::name()))
        return new barnsley2Func;
    if(0 == strcmp(name,novaFunc::name()))
        return new novaFunc;

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
