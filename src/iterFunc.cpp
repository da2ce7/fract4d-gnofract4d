/* functions which perform individual iterations of a fractal function */

#include "iterFunc.h"

#include <cstddef>
#include <iostream>
#include <string>

// for some reason these have to be declared in the leaf class, even
// though they're the same all over. Odd.
#define IO_DECLS(className) \
    friend std::ostream& operator<<(std::ostream& s, const className& m); \
    friend std::istream& operator>>(std::istream& s, className& m); \
    std::ostream& put(std::ostream& s) const { return s << *this; } \
    std::istream& get(std::istream& s) { return s;  } 

#define IO_DEFNS(className) \
std::ostream& \
operator<<(std::ostream& s, const className& m) \
{ \
    s << m.type() << "\n"; \
    return s; \
} \
\
std::istream& \
operator>>(std::istream& s, className& m) \
{ \
    /* don't need to do anything */ \
    return s; \
}

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
public:
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
};

// z <- z^2 +c
class mandFunc : public noOptions
{
public:
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
    char *name() const
        {
            return "Mandelbrot";
        }
    int type() const
        {
            return 0;
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
    IO_DECLS(mandFunc)
};

IO_DEFNS(mandFunc)

// z <- (|x| + i |y|)^2 + c
class shipFunc: public noOptions
{
public:
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
    char *name() const
        {
            return "Burning Ship";
        }
    int flags() const
        {
            return HAS_X2 | HAS_Y2;
        }
    int type() const
        {
            return 1;
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
    IO_DECLS(shipFunc)
};

IO_DEFNS(shipFunc)

// z <- (|x| + i |y|)^2 + (|x| + i|y|) + c
class buffaloFunc: public noOptions
{
public:
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
    virtual char *name() const 
        {
            return "Buffalo";
        }
    int type() const
        {
            return 2;
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
    IO_DECLS(buffaloFunc)
};

IO_DEFNS(buffaloFunc);

// z <- z^3 + c
class cubeFunc : public noOptions
{
public:
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
    virtual char *name() const 
        {
            return "Cubic Mandelbrot";
        }
    int type() const
        {
            return 3;
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
    IO_DECLS(cubeFunc)
};

IO_DEFNS(cubeFunc)

// generalised quadratic mandelbrot
// computes a[0] * z^2 + a[1] * z + a[2] * c
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
    virtual char *name() const
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
    int type() const 
        {
            return 4;
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

std::ostream& operator<<(std::ostream& s, const quadFunc& f)
{
    s << f.type() << "\n";
    s << f.a[0] << "\n"
      << f.a[1] << "\n"
      << f.a[2] << "\n";

    return s;
} 

std::istream& 
operator>>(std::istream& s, quadFunc& f)
{
    s >> f.a[0] >> f.a[1] >> f.a[2];
    return s;
}

// factory method to make new iterFuncs
iterFunc *iterFunc_new(int nFunc)
{
    switch(nFunc){
    case 0:
        return new mandFunc;

    case 1:
        return new shipFunc;
    case 2:
        return new buffaloFunc;
    case 3:
        return new cubeFunc;
    case 4:
        return new quadFunc;
    default:
        return NULL;
    }
}

// deserialize an iterFunc from a stream

iterFunc *iterFunc_read(std::istream& s)
{
    int type;
    s >> type;
    
    iterFunc *f = iterFunc_new(type);
    
    s >> *f;

    return f;
}
