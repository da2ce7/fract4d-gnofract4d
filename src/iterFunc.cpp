/* function objects which perform individual iterations of a fractal function */

#include "iterFunc.h"
#include "io.h"

#include <cstddef>
#include <iostream>
#include <string>
#include <cmath>

#define IO_DECLS(className) \
    friend std::ostream& operator<<(std::ostream& s, const className& m); \
    friend std::istream& operator>>(std::istream& s, className& m); \
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

class noOptions : public iterFunc
{
private:
    const char *m_type;
public:
    noOptions(const char *type) : m_type(type) {}

    int nOptions() const
        { 
            return 0; 
        }
    void setOption(int n, double val) 
        {
            // no options to set
        }
    double getOption(int n) const
        {
            // no real options
            return 0.0; 
        }
    const char *type() const
        {
            return m_type;
        }
    IO_DECLS(noOptions)
};

std::ostream& 
operator<<(std::ostream& s, const noOptions& m) 
{ 
    write_field(s,FIELD_FUNCTION);
    s << m.type() << "\n";
    s << SECTION_STOP << "\n"; 
    return s; 
} 

std::istream& 
operator>>(std::istream& s, noOptions& m) 
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
class mandFunc : public noOptions
{
public:
    mandFunc() : noOptions(name()) {}
    void operator()(double *p) const
        {
            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] - p[Y2] + p[CX];
            p[Y] = 2.0 * p[X] * p[Y] + p[CY];
            p[X] = atmp;
        }
    int flags() const
        {
            return HAS_X2 | HAS_Y2;
        }
    static char *name()
        {
            return "Mandelbrot";
        }
    iterFunc *clone() const
        {
            return new mandFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const mandFunc *p = dynamic_cast<const mandFunc *>(&c);
            if(!p) return false;
            return true;
        }
};

// z <- ( re(z) > 0 ? (z - 1) * c : (z + 1) * c)
class barnsleyFunc: public noOptions
{
public:
    barnsleyFunc() : noOptions(name()) {};
    void operator()(double *p) const
        {
            double x_cy = p[X] * p[CY], x_cx = p[X] * p[CX],
                y_cy = p[Y] * p[CY], y_cx = p[Y] * p[CX];
            
            if(p[X] >= 0)
            {
                p[X] = (x_cx - p[CX] - y_cy );
                p[Y] = (y_cx - p[CY] + x_cy );
            }
            else
            {
                p[X] = (x_cx + p[CX] - y_cy);
                p[Y] = (y_cx + p[CY] + x_cy);
            }
        }
    int flags() const
        {
            return 0;
        }
    static char *name()
        {
            return "Barnsley Type 1";
        }
    iterFunc *clone() const
        {
            return new barnsleyFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const barnsleyFunc *p = dynamic_cast<const barnsleyFunc *>(&c);
            if(!p) return false;
            return true;
        }
};

// 
class barnsley2Func: public noOptions
{
public:
    barnsley2Func() : noOptions(name()) {};
    void operator()(double *p) const
        {
            double x_cy = p[X] * p[CY], x_cx = p[X] * p[CX],
                y_cy = p[Y] * p[CY], y_cx = p[Y] * p[CX];
            
            if(p[X]*p[CY] + p[Y]*p[CX] >= 0)
            {
                p[X] = (x_cx - p[CX] - y_cy );
                p[Y] = (y_cx - p[CY] + x_cy );
            }
            else
            {
                p[X] = (x_cx + p[CX] - y_cy);
                p[Y] = (y_cx + p[CY] + x_cy);
            }
        }
    int flags() const
        {
            return 0;
        }
    static const char *name()
        {
            return "Barnsley Type 2";
        }
    iterFunc *clone() const
        {
            return new barnsley2Func(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const barnsley2Func *p = dynamic_cast<const barnsley2Func *>(&c);
            if(!p) return false;
            return true;
        }
};

// z <- lambda * z * ( 1 - z)
class lambdaFunc: public noOptions
{
public:
    lambdaFunc() : noOptions(name()) {};
    void operator()(double *p) const
        {
            p[X2] = p[X] * p[X]; p[Y2] = p[Y] * p[Y];

            /* t <- z * (1 - z) */
            double tx = p[X] - p[X2] + p[Y2];
            double ty = p[Y] - 2.0 * p[X] * p[Y];

            p[X] = p[CX] * tx - p[CY] * ty;
            p[Y] = p[CX] * ty + p[CY] * tx;
        }
    int flags() const
        {
            return HAS_X2 | HAS_Y2;
        }
    static const char *name()
        {
            return "Lambda";
        }
    iterFunc *clone() const
        {
            return new lambdaFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const lambdaFunc *p = dynamic_cast<const lambdaFunc *>(&c);
            if(!p) return false;
            return true;
        }
};

// z <- (|x| + i |y|)^2 + c
class shipFunc: public noOptions
{
public:
    shipFunc() : noOptions(name()) {};
    void operator()(double *p) const 
        {
            p[X] = fabs(p[X]);
            p[Y] = fabs(p[Y]);
            // same as mbrot from here
            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] - p[Y2] + p[CX];
            p[Y] = 2.0 * p[X] * p[Y] + p[CY];
            p[X] = atmp;
        }
    static const char *name()
        {
            return "Burning Ship";
        }
    int flags() const
        {
            return HAS_X2 | HAS_Y2;
        }
    iterFunc *clone() const
        {
            return new shipFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const shipFunc *p = dynamic_cast<const shipFunc *>(&c);
            if(!p) return false;
            return true;
        }
};

// z <- (|x| + i |y|)^2 + (|x| + i|y|) + c
class buffaloFunc: public noOptions
{
public:
    buffaloFunc() : noOptions(name()) {}
    virtual void operator()(double *p) const
        {
            p[X] = fabs(p[X]);
            p[Y] = fabs(p[Y]);

            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] - p[Y2] - p[X] + p[CX];
            p[Y] = 2.0 * p[X] * p[Y] - p[Y] + p[CY];
            p[X] = atmp;
        }
    virtual int flags() const
        {
            return HAS_X2 | HAS_Y2;
        }
    static const char *name()
        {
            return "Buffalo";
        }
    iterFunc *clone() const
        {
            return new buffaloFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const buffaloFunc *p = dynamic_cast<const buffaloFunc *>(&c);
            if(!p) return false;
            return true;
        }
};

// z <- z^3 + c
class cubeFunc : public noOptions
{
public:
    cubeFunc() : noOptions(name()) {}
    virtual void operator()(double *p) const
        {
            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = p[X2] * p[X] - 3.0 * p[X] * p[Y2] + p[CX];
            p[Y] = 3.0 * p[X2] * p[Y] - p[Y2] * p[Y] + p[CY];
            p[X] = atmp;
        }    
    virtual int flags() const 
        {
            return 0;
        }
    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
    iterFunc *clone() const
        {
            return new cubeFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const cubeFunc *p = dynamic_cast<const cubeFunc *>(&c);
            if(!p) return false;
            return true;
        }
};

// generalised quadratic mandelbrot
// computes a[0] * z^2 + a[1] * z + a[2] * c
// a[] array should be an array of complex numbers, really
class quadFunc : public iterFunc
{
private:
    double a[3];
public:
    quadFunc() {
        // default is z^2 - z + c
        a[0] = 1.0;
        a[1] = 1.0;
        a[2] = 1.0;
    }
    virtual void operator()(double *p) const
        {
            p[X2] = p[X] * p[X];
            p[Y2] = p[Y] * p[Y];
            double atmp = a[0] * (p[X2] - p[Y2]) + a[1] * p[X] + a[2] * p[CX];
            p[Y] = a[0] * (2.0 * p[X] * p[Y]) + a[1] * p[Y] + a[2] * p[CY];
            p[X] = atmp;
        }
    virtual int flags() const
        {
            return HAS_X2 | HAS_Y2;
        }
    static char *name()
        {
            return "Quadratic";
        }
    virtual int nOptions() const
        { 
            return 3; 
        }
    virtual void setOption(int n, double val) 
        {
            if(n < 0 || n > 2) return;
            a[n] = val;
        }
    virtual double getOption(int n) const
        {
            if(n < 0 || n > 2) return 0.0; 
            return a[n];
        }
    const char *type() const 
        {
            return name();
        }
    iterFunc *clone() const
        {
            return new quadFunc(*this);
        }
    bool operator==(const iterFunc &c) const
        {
            const quadFunc *p = dynamic_cast<const quadFunc *>(&c);
            if(!p) return false;
            return p->a[0] == a[0] && p->a[1] == a[1] && p->a[2] == a[2];
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
