/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

#ifndef _VECTORS_H_
#define _VECTORS_H_

#include <math.h>
// forward declarations 
template<class T> class vec2;
template<class T> class vec3;
template<class T> class vec4;
template<class T> class mat3;
template<class T> class mat4;

enum {VX, VY, VZ, VW};		    // axes


/****************************************************************
*								*
*			    2D Vector				*
*								*
****************************************************************/

/* g++ demands that friend decls be templated ; VC++ demands that they're not! */
#ifndef _WIN32
#define ET <>
#endif

template<class T>
class vec2
{
protected:

	T n[2];
	
public:

        // Constructors

	vec2() {};
	
	vec2(const T& x, const T& y) { n[VX] = x; n[VY] = y; };
	
	explicit vec2(const T d) { n[VX] = n[VY] = d; };
	
	// copy constructor
	vec2(const vec2& v) { 
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; 
	}; 

	// cast v3 to v2 NB it is up to caller to avoid divide-by-zero
	explicit vec2(const vec3<T>& v) { 
		n[VX] = v.n[VX]/v.n[VZ]; n[VY] = v.n[VY]/v.n[VZ]; 
	};

	// cast v3 to v2 by throwing away a dimension
	explicit vec2(const vec3<T>& v, int dropAxis) {
		switch (dropAxis) {
		case VX: n[VX] = v.n[VY]; n[VY] = v.n[VZ]; break;
		case VY: n[VX] = v.n[VX]; n[VY] = v.n[VZ]; break;
		default: n[VX] = v.n[VX]; n[VY] = v.n[VY]; break;
		}
	}

	// Assignment operators

	// assignment of a vec2
	vec2& operator	= ( const vec2& v ) { 
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; return *this; 
	};

	// In-place update operators

	// incrementation by a vec2
	vec2& operator += ( const vec2& v ) {
		n[VX] += v.n[VX]; n[VY] += v.n[VY]; return *this; 
	};

	// decrementation by a vec2
	vec2& operator -= ( const vec2& v ) { 
		n[VX] -= v.n[VX]; n[VY] -= v.n[VY]; return *this; 
	};

	// multiplication by a scalar
	vec2& operator *= ( const T& d ) {
		n[VX] *= d; n[VY] *= d; return *this; 
	}
	
	// division by a scalar
	vec2& operator /= ( const T& d ) {
		n[VX] /= d; n[VY] /= d; return *this; 
	}

	// indexing
	T operator [] ( int i) {
		return n[i];
	}

	// special functions

#if 0
// There's a problem with templates here. 
// The original functions worked fine with doubles,
// but give problems if you want a vec2 of (say) complex numbers

	// length of a vec2
	T length() {
		return sqrt(length2());
	}

	// squared length of a vec2
	T length2() {
		return n[VX]*n[VX] + n[VY]*n[VY]; 
	};

	// normalize a vec2 NB it is up to caller to avoid divide-by-zero 
	vec2& normalize() {
		*this /= length(); return *this; 
	};
#endif

// friends

	friend vec2 operator - ET (const vec2& v);			    // -v1
	friend vec2 operator + ET (const vec2& a, const vec2& b);	    // v1 + v2
	friend vec2 operator - ET (const vec2& a, const vec2& b);	    // v1 - v2
	friend vec2 operator * ET (const vec2& a, const T& d);	    // v1 * 3.0
	friend vec2 operator * ET (const T& d, const vec2& a);	    // 3.0 * v1
	friend vec2 operator * ET (const mat3<T>& a, const vec2& v);	    // M . v
	friend vec2 operator * ET (const vec2& v, mat3<T>& a);	    // v . M
	friend T operator * ET (const vec2& a, const vec2& b);    // dot product
	friend vec2 operator / ET (const vec2& a, const T& d);	    // v1 / 3.0
	friend vec3<T> operator ^ ET (const vec2& a, const vec2& b);	    // cross product
	friend bool operator == ET (const vec2& a, const vec2& b);	    // v1 == v2 ?
	friend bool operator != ET (const vec2& a, const vec2& b);	    // v1 != v2 ?
	friend void swap ET (vec2& a, vec2& b);			    // swap v1 & v2
	friend vec2 prod ET (const vec2& a, const vec2& b);		    // term by term *

// necessary friend declarations

	friend class vec3<T>;
};

template<class T> 
vec2<T> operator - (const vec2<T>& a)
{ return vec2<T>(-a.n[VX],-a.n[VY]); }

template<class T> vec2<T> operator + (const vec2<T>& a, const vec2<T>& b)
{ return vec2<T>(a.n[VX]+ b.n[VX], a.n[VY] + b.n[VY]); }

template<class T> 
vec2<T> operator - (const vec2<T>& a, const vec2<T>& b)
{ return vec2<T>(a.n[VX]-b.n[VX], a.n[VY]-b.n[VY]); }

template<class T> 
vec2<T> operator * (const vec2<T>& a, const T& d)
{ return vec2<T>(d*a.n[VX], d*a.n[VY]); }

template<class T> 
vec2<T> operator * (const T& d, const vec2<T>& a)
{ return a*d; }

template<class T> 
vec2<T> operator * (const mat3<T>& a, const vec2<T>& v) {
	vec3<T> av;

	av.n[VX] = a.v[0].n[VX]*v.n[VX] + a.v[0].n[VY]*v.n[VY] + a.v[0].n[VZ];
	av.n[VY] = a.v[1].n[VX]*v.n[VX] + a.v[1].n[VY]*v.n[VY] + a.v[1].n[VZ];
	av.n[VZ] = a.v[2].n[VX]*v.n[VX] + a.v[2].n[VY]*v.n[VY] + a.v[2].n[VZ];
	return av;
}

template<class T> 
vec2<T> operator * (const vec2<T>& v, mat3<T>& a)
{ return a.transpose() * v; }

template<class T> 
T operator * (const vec2<T>& a, const vec2<T>& b)
{ return (a.n[VX]*b.n[VX] + a.n[VY]*b.n[VY]); }

template<class T> 
vec2<T> operator / (const vec2<T>& a, const T& d) {
	return vec2<T>(a.n[VX]/d, a.n[VY]/d); 
}

template<class T> 
vec3<T> operator ^ (const vec2<T>& a, const vec2<T>& b) { 
	return vec3<T>(0.0, 0.0, a.n[VX] * b.n[VY] - b.n[VX] * a.n[VY]); 
}

template<class T> 
bool operator == (const vec2<T>& a, const vec2<T>& b) { 
	return (a.n[VX] == b.n[VX]) && (a.n[VY] == b.n[VY]); 
}

template<class T> 
bool operator != (const vec2<T>& a, const vec2<T>& b) { 
	return !(a == b); 
}
template<class T>
void swap(vec2<T>& a, vec2<T>& b)
{
	vec2<T> tmp(a);
	a = b;
	b = tmp;
}

template<class T>
vec2<T> prod(const vec2<T>& a, const vec2<T>& b)
{ 
	return vec2<T>(a.n[VX] * b.n[VX], a.n[VY] * b.n[VY]); 
}

template<class T>
class vec3
{
protected:
	T n[3];
public:
	
 // Constructors

	vec3() { };

	vec3(const T& x, const T& y, const T& z){ 
		n[VX] = x; n[VY] = y; n[VZ] = z; 
	};
	explicit vec3(const T& d){ 
		n[VX] = n[VY] = n[VZ] = d; 
	};

	// copy constructor
	vec3(const vec3& v){ 
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = v.n[VZ]; 
	};

        // cast v2 to v3
	explicit vec3(const vec2<T>& v) { 
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = 1.0; 
	};			    
	
	// cast v2 to v3
	explicit vec3(const vec2<T>& v, T& d) {
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = d;
	};

        // cast v4 to v3
	explicit vec3(const vec4<T>& v) {
		n[VX] = v.n[VX] / v.n[VW]; 
		n[VY] = v.n[VY] / v.n[VW];
		n[VZ] = v.n[VZ] / v.n[VW]; 
	};	

	// cast v4 to v3
	explicit vec3(const vec4<T>& v, int dropAxis) {
		switch (dropAxis) {
		case VX: n[VX] = v.n[VY]; n[VY] = v.n[VZ]; n[VZ] = v.n[VW]; break;
		case VY: n[VX] = v.n[VX]; n[VY] = v.n[VZ]; n[VZ] = v.n[VW]; break;
		case VZ: n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = v.n[VW]; break;
		default: n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = v.n[VZ]; break;
		}
	};

	// Assignment operators
	
        // assignment of a vec3
	vec3& operator	= ( const vec3& v ) {
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = v.n[VZ]; return *this; 
	};	    

	// In-place update operators

        // incrementation by a vec3
	vec3& operator += ( const vec3& v ) {
		n[VX] += v.n[VX]; n[VY] += v.n[VY]; n[VZ] += v.n[VZ]; return *this;
	};

	// decrementation by a vec3
	vec3& operator -= ( const vec3& v ) {
		n[VX] -= v.n[VX]; n[VY] -= v.n[VY]; n[VZ] -= v.n[VZ]; return *this;
	}

        // multiplication by a scalar
	vec3& operator *= ( const T& d ){ 
		n[VX] *= d; n[VY] *= d; n[VZ] *= d; return *this; 
	};	    

        // division by a scalar
	vec3& operator /= ( const T& d ) { 
		n[VX] /= d; n[VY] /= d; n[VZ] /= d;
		return *this; 
	};	    

	// indexing
	T operator [] ( int i) {
		return n[i];
	};
	
        // friends


	friend vec3 operator - ET (const vec3& v);	            // -v1
	friend vec3 operator + ET (const vec3& a, const vec3& b);    // v1 + v2
	friend vec3 operator - ET (const vec3& a, const vec3& b);    // v1 - v2
	friend vec3 operator * ET (const vec3& a, const T& d);	    // v1 * 3.0
	friend vec3 operator * ET (const T& d, const vec3& a);	    // 3.0 * v1
	friend vec3 operator * ET (const mat4<T>& a, const vec3& v); // M . v
	friend vec3 operator * ET (const vec3& v, mat4<T>& a);	    // v . M
	friend T operator * ET (const vec3& a, const vec3& b);       // dot product
	friend vec3 operator / ET (const vec3& a, const T& d);	    // v1 / 3.0
	friend vec3 operator ^ ET (const vec3& a, const vec3& b);    // cross product
	friend bool operator == ET (const vec3& a, const vec3& b);   // v1 == v2 ?
	friend bool operator !=  ET (const vec3& a, const vec3& b);   // v1 != v2 ?
	friend void swap ET (vec3& a, vec3& b);			    // swap v1 & v2
	friend vec3 prod ET (const vec3& a, const vec3& b);	    // term by term *

        // necessary friend declarations

	friend class vec2<T>;
	friend class vec4<T>;
	friend class mat3<T>;

        // linear transform
	friend vec2<T> operator * ET (const mat3<T>& a, const vec2<T>& v);

	// matrix 3 product
	friend mat3<T> operator * ET (mat3<T>& a, mat3<T>& b);

};


// vec3 friends

template<class T>
vec3<T> operator - (const vec3<T>& a) {
	return vec3<T>(-a.n[VX],-a.n[VY],-a.n[VZ]); 
}

template<class T>
vec3<T> operator + (const vec3<T>& a, const vec3<T>& b){ 
	return vec3<T>(a.n[VX]+ b.n[VX], a.n[VY] + b.n[VY], a.n[VZ] + b.n[VZ]); 
}

template<class T>
vec3<T> operator - (const vec3<T>& a, const vec3<T>& b) { 
	return vec3<T>(a.n[VX]-b.n[VX], a.n[VY]-b.n[VY], a.n[VZ]-b.n[VZ]); 
}

template<class T>
vec3<T> operator * (const vec3<T>& a, const T& d) { 
	return vec3<T>(d*a.n[VX], d*a.n[VY], d*a.n[VZ]); 
}

template<class T>
vec3<T> operator * (const T& d, const vec3<T>& a) { 
	return a*d; 
}

template<class T>
vec3<T> operator * (const mat4<T>& a, const vec3<T>& v) { 
	return a * vec4<T>(v); 
}

template<class T>
vec3<T> operator * (const vec3<T>& v, mat4<T>& a) { 
	return a.transpose() * v; 
}

template<class T>
T operator * (const vec3<T>& a, const vec3<T>& b) { 
	return (a.n[VX]*b.n[VX] + a.n[VY]*b.n[VY] + a.n[VZ]*b.n[VZ]); 
}

template<class T>
vec3<T> operator / (const vec3<T>& a, const T& d) { 
	return vec3<T>(a.n[VX]/d_inv, a.n[VY]/d_inv,a.n[VZ]/d_inv); 
}

template<class T>
vec3<T> operator ^ (const vec3<T>& a, const vec3<T>& b) {
    return vec3<T>(a.n[VY]*b.n[VZ] - a.n[VZ]*b.n[VY],
		a.n[VZ]*b.n[VX] - a.n[VX]*b.n[VZ],
		a.n[VX]*b.n[VY] - a.n[VY]*b.n[VX]);
}

template<class T>
bool operator == (const vec3<T>& a, const vec3<T>& b) { 
	return (a.n[VX] == b.n[VX]) && (a.n[VY] == b.n[VY]) && (a.n[VZ] == b.n[VZ]);
}

template<class T>
bool operator != (const vec3<T>& a, const vec3<T>& b)
{ return !(a == b); }

template<class T>
void swap(vec3<T>& a, vec3<T>& b)
{ vec3<T> tmp(a); a = b; b = tmp; }

template<class T>
vec3<T> prod(const vec3<T>& a, const vec3<T>& b)
{ return vec3<T>(a.n[VX] * b.n[VX], a.n[VY] * b.n[VY], a.n[VZ] * b.n[VZ]); }

// 4 element vector

template<class T>
class vec4
{
public:

	T n[4];

public:

	// Constructors

	vec4() {};
	vec4(const T& x, const T& y, const T& z, const T& w) {
		n[VX] = x; n[VY] = y; n[VZ] = z; n[VW] = w;
	};
	explicit vec4(const T& d) {  
		n[VX] = n[VY] = n[VZ] = n[VW] = d; 
	};

	// copy constructor
	vec4(const vec4& v) {
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = v.n[VZ]; n[VW] = v.n[VW];
	};

	// cast vec3 to vec4
	explicit vec4(const vec3<T>& v, const T& d = 1.0) { 
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; n[VZ] = v.n[VZ]; n[VW] = d; 
	};
	
        // Assignment operators

	// assignment of a vec4
	vec4& operator	= ( const vec4& v ) {
		n[VX] = v.n[VX]; n[VY] = v.n[VY]; 
		n[VZ] = v.n[VZ]; n[VW] = v.n[VW];
		return *this;
	};

	// In-place update operators

	// incrementation by a vec4
	vec4& operator += ( const vec4& v ) { 
		n[VX] += v.n[VX]; n[VY] += v.n[VY]; 
		n[VZ] += v.n[VZ]; n[VW] += v.n[VW];
		return *this; 
	};

	// decrementation by a vec4
	vec4& operator -= ( const vec4& v ) { 
		n[VX] -= v.n[VX]; n[VY] -= v.n[VY]; 
		n[VZ] -= v.n[VZ]; n[VW] -= v.n[VW];
		return *this; 
	};

	// multiplication by a scalar
	vec4& operator *= ( const T& d ) { 
		n[VX] *= d; n[VY] *= d; n[VZ] *= d; n[VW] *= d; 
		return *this; 
	};

	// division by a constant
	vec4& operator /= ( const T& d ) { 
		n[VX] /= d; n[VY] /= d; 
		n[VZ] /= d; n[VW] /= d; 
		return *this; 
	};

	// indexing
	T& operator [] ( int i) {
		return n[i];
	};

        // friends

	friend vec4 operator -  ET (const vec4& v);			    // -v1
	friend vec4 operator +  ET (const vec4& a, const vec4& b);	    // v1 + v2
	friend vec4 operator -  ET (const vec4& a, const vec4& b);	    // v1 - v2
	friend vec4 operator *  ET (const vec4& a, const T& d);	    // v1 * 3.0
	friend vec4 operator *  ET (const T& d, const vec4& a);	    // 3.0 * v1
	friend vec4 operator *  ET (const mat4<T>& a, const vec4& v);	    // M . v
	friend vec4 operator *  ET (const vec4& v, mat4<T>& a);	    // v . M
	friend T operator *     ET (const vec4& a, const vec4& b);    // dot product
	friend vec4 operator /  ET (const vec4& a, const T& d);	    // v1 / 3.0
	friend bool operator == ET (const vec4& a, const vec4& b);	    // v1 == v2 ?
	friend bool operator != ET (const vec4& a, const vec4& b);	    // v1 != v2 ?
	friend void swap ET (vec4& a, vec4& b);			    // swap v1 & v2
	friend vec4 prod ET (const vec4& a, const vec4& b);		    // term by term *

        // necessary friend declarations

	friend class vec3<T>;
	friend class mat4<T>;
	friend vec3<T> operator * ET (const mat4<T>& a, const vec3<T>& v);	    // linear transform
	friend mat4<T> operator * ET (const mat4<T>& a, const mat4<T>& b);		    // matrix 4 product
};

// vec4 friends

template<class T>
vec4<T> operator - (const vec4<T>& a) { 
	return vec4<T>(-a.n[VX],-a.n[VY],-a.n[VZ],-a.n[VW]); 
}

template<class T>
vec4<T> operator + (const vec4<T>& a, const vec4<T>& b) { 
	return vec4<T>(a.n[VX] + b.n[VX], a.n[VY] + b.n[VY], 
		       a.n[VZ] + b.n[VZ], a.n[VW] + b.n[VW]); 
}

template<class T>
vec4<T> operator - (const vec4<T>& a, const vec4<T>& b) {  
	return vec4<T>(a.n[VX] - b.n[VX], a.n[VY] - b.n[VY], 
		       a.n[VZ] - b.n[VZ], a.n[VW] - b.n[VW]); 
}

template<class T>
vec4<T> operator * (const vec4<T>& a, const T& d) { 
	return vec4<T>(d*a.n[VX], d*a.n[VY], d*a.n[VZ], d*a.n[VW] ); 
}

template<class T>
vec4<T> operator * (const T& d, const vec4<T>& a) { 
	return a*d; 
}

template<class T>
vec4<T> operator * (const mat4<T>& a, const vec4<T>& v) {
    #define ROWCOL(i) a.v[i].n[0]*v.n[VX] + a.v[i].n[1]*v.n[VY] \
    + a.v[i].n[2]*v.n[VZ] + a.v[i].n[3]*v.n[VW]
    return vec4<T>(ROWCOL(0), ROWCOL(1), ROWCOL(2), ROWCOL(3));
    #undef ROWCOL
}

template<class T>
vec4<T> operator * (const vec4<T>& v, mat4<T>& a) { 
	return a.transpose() * v; 
}

template<class T>
T operator * (const vec4<T>& a, const vec4<T>& b) { 
	return (a.n[VX]*b.n[VX] + a.n[VY]*b.n[VY] + 
		a.n[VZ]*b.n[VZ] + a.n[VW]*b.n[VW]);
}

template<class T>
vec4<T> operator / (const vec4<T>& a, const T& d) { 
	return vec4<T>(a.n[VX]/d, a.n[VY]/d, a.n[VZ]/d, a.n[VW]/d);
}

template<class T>
bool operator == (const vec4<T>& a, const vec4<T>& b) { 
	return (a.n[VX] == b.n[VX]) && (a.n[VY] == b.n[VY]) && 
		(a.n[VZ] == b.n[VZ]) && (a.n[VW] == b.n[VW]); 
}

template<class T>
bool operator != (const vec4<T>& a, const vec4<T>& b) { 
	return !(a == b); 
}

template<class T>
void swap(vec4<T>& a, vec4<T>& b) { 
	vec4<T> tmp(a); a = b; b = tmp; 
}

template<class T>
vec4<T> prod(const vec4<T>& a, const vec4<T>& b) { 
	return vec4<T>(a.n[VX] * b.n[VX], a.n[VY] * b.n[VY], 
		       a.n[VZ] * b.n[VZ], a.n[VW] * b.n[VW]); 
}

template<class T>
class mat3
{
protected:

	vec3<T> v[3];

public:

        // Constructors

	mat3() { };
	mat3(const vec3<T>& v0, const vec3<T>& v1, const vec3<T>& v2) {
		v[0] = v0; v[1] = v1; v[2] = v2;
	};

	explicit mat3(const T& d) {
		v[0] = v[1] = v[2] = vec3<T>(d);
	}
	// copy comstructor
	mat3(const mat3& m) {
		v[0] = m.v[0]; v[1] = m.v[1]; v[2] = m.v[2];
	};
	
        // Assignment operators

	mat3& operator	= ( const mat3& m ) { 
		v[0] = m.v[0]; v[1] = m.v[1]; v[2] = m.v[2]; return *this; 
	};

	// In-place update operators

        // incrementation by a mat3
	mat3& operator += ( const mat3& m ) {
		v[0] += m.v[0]; v[1] += m.v[1]; v[2] += m.v[2]; return *this; 
	};

	// decrementation by a mat3	    
	mat3& operator -= ( const mat3& m ) { 
		v[0] -= m.v[0]; v[1] -= m.v[1]; v[2] -= m.v[2]; return *this; 
	};

        // multiplication by a constant
	mat3& operator *= ( const T& d ) {
		v[0] *= d; v[1] *= d; v[2] *= d; return *this; 
	};

	// division by a constant	    
	mat3& operator /= ( const T& d ) {
		v[0] /= d; v[1] /= d; v[2] /= d; return *this; 
	};

	// indexing
	vec3<T>& operator [] ( int i) {
		return v[i];
	};


        // special functions

	mat3 transpose() {
		return mat3(vec3<T>(v[0][0], v[1][0], v[2][0]),
			    vec3<T>(v[0][1], v[1][1], v[2][1]),
			    vec3<T>(v[0][2], v[1][2], v[2][2]));
	};

#if 0 
	// this causes template problems too...

        // Gauss-Jordan elimination with partial pivoting
	mat3 inverse() {
		mat3 a(*this),	    // As a evolves from original mat into identity
		     b(identity2D());   // b evolves from identity into inverse(a)
		int	 i, j, i1;

		// Loop over cols of a from left to right, eliminating above and below diag
		for (j=0; j<3; j++) {   // Find largest pivot in column j among rows j..2
			i1 = j;		    // Row with largest pivot candidate
			for (i=j+1; i<3; i++) {
				if (fabs(a.v[i].n[j]) > fabs(a.v[i1].n[j]))
					i1 = i;
			}
			// Swap rows i1 and j in a and b to put pivot on diagonal
			swap(a.v[i1], a.v[j]);
			swap(b.v[i1], b.v[j]);
			
			// Scale row j to have a unit diagonal
			// if it's zero this'll cause div by zero
			/*
			if (a.v[j].n[j]==0.)
				throw(std::overflow_error);
			*/
			b.v[j] /= a.v[j].n[j];
			a.v[j] /= a.v[j].n[j];
			
			// Eliminate off-diagonal elems in col j of a, doing identical ops to b
			for (i=0; i<3; i++) {
				if (i!=j) {
					b.v[i] -= a.v[i].n[j]*b.v[j];
					a.v[i] -= a.v[i].n[j]*a.v[j];
				}
			}
		}
		return b;
	};			
#endif

        // friends

	friend mat3 operator - ET (const mat3& a);			    // -m1
	friend mat3 operator + ET (const mat3& a, const mat3& b);	    // m1 + m2
	friend mat3 operator - ET (const mat3& a, const mat3& b);	    // m1 - m2
	friend mat3 operator * ET (mat3& a, mat3& b);		    // m1 * m2
	friend mat3 operator * ET (const mat3& a, const T&);	    // m1 * 3.0
	friend mat3 operator * ET (const T&, const mat3& a);	    // 3.0 * m1
	friend mat3 operator / ET (const mat3& a, const T& d);	    // m1 / 3.0
	friend bool operator ==ET (const mat3& a, const mat3& b);	    // m1 == m2 ?
	friend bool operator !=ET (const mat3& a, const mat3& b);	    // m1 != m2 ?
	friend void swap ET (mat3& a, mat3& b);			    // swap m1 & m2
	
        // necessary friend declarations
	
	friend vec3<T> operator * ET (const mat3& a, const vec3<T>& v);	    // linear transform
	friend vec2<T> operator * ET (const mat3& a, const vec2<T>& v);	    // linear transform
};


// mat3 friends

template<class T>
mat3<T> operator - (const mat3<T>& a) { 
	return mat3<T>(-a.v[0], -a.v[1], -a.v[2]); 
}

template<class T>
mat3<T> operator + (const mat3<T>& a, const mat3<T>& b) { 
	return mat3<T>(a.v[0] + b.v[0], a.v[1] + b.v[1], a.v[2] + b.v[2]); 
}

template<class T>
mat3<T> operator - (const mat3<T>& a, const mat3<T>& b) { 
	return mat3<T>(a.v[0] - b.v[0], a.v[1] - b.v[1], a.v[2] - b.v[2]); 
}

template<class T>
mat3<T> operator * (mat3<T>& a, mat3<T>& b) {
    #define ROWCOL(i, j) \
    a.v[i].n[0]*b.v[0][j] + a.v[i].n[1]*b.v[1][j] + a.v[i].n[2]*b.v[2][j]
    return mat3<T>(vec3<T>(ROWCOL(0,0), ROWCOL(0,1), ROWCOL(0,2)),
		vec3<T>(ROWCOL(1,0), ROWCOL(1,1), ROWCOL(1,2)),
		vec3<T>(ROWCOL(2,0), ROWCOL(2,1), ROWCOL(2,2)));
    #undef ROWCOL
}

template<class T>
mat3<T> operator * (const mat3<T>& a, const T& d) { 
	return mat3<T>(a.v[0] * d, a.v[1] * d, a.v[2] * d); 
}

template<class T>
mat3<T> operator * (const T& d, const mat3<T>& a) { 
	return a*d; 
}

template<class T>
mat3<T> operator / (const mat3<T>& a, const T& d) { 
	return mat3<T>(a.v[0] / d, a.v[1] / d, a.v[2] / d); 
}

template<class T>
bool operator == (const mat3<T>& a, const mat3<T>& b) { 
	return (a.v[0] == b.v[0]) && (a.v[1] == b.v[1]) && (a.v[2] == b.v[2]); 
}

template<class T>
bool operator != (const mat3<T>& a, const mat3<T>& b) { 
	return !(a == b); 
}

template<class T>
void swap(mat3<T>& a, mat3<T>& b) { 
	mat3<T> tmp(a); a = b; b = tmp; 
}

// 4 x 4 matrix

template<class T>
class mat4
{
protected:

	vec4<T> v[4];

public:

        // Constructors

	mat4() { };
	mat4(const vec4<T>& v0, const vec4<T>& v1, const vec4<T>& v2, const vec4<T>& v3) {
		v[0] = v0; v[1] = v1; v[2] = v2; v[3] = v3;
	};

	explicit mat4(const T& d) {
		v[0] = v[1] = v[2] = v[3] = vec4<T>(d);
	};

	// copy constructor
	mat4(const mat4& m) {
		v[0] = m.v[0]; v[1] = m.v[1]; v[2] = m.v[2]; v[3] = m.v[3];
	};
	
        // Assignment operators
	
	mat4& operator	= ( const mat4& m ) { 
		v[0] = m.v[0]; v[1] = m.v[1]; v[2] = m.v[2]; v[3] = m.v[3];
		return *this; 
	};	    

	// In-place update operators

	// incrementation by a mat4
	mat4& operator += ( const mat4& m ) { 
		v[0] += m.v[0]; v[1] += m.v[1]; v[2] += m.v[2]; v[3] += m.v[3];
		return *this; 
	};

	// decrementation by a mat4
	mat4& operator -= ( const mat4& m ) { 
		v[0] -= m.v[0]; v[1] -= m.v[1]; v[2] -= m.v[2]; v[3] -= m.v[3];
		return *this; 
	};

	// multiplication by a scalar
	mat4& operator *= ( const T& d ) { 
		v[0] *= d; v[1] *= d; v[2] *= d; v[3] *= d; return *this;
	};
	// division by a scalar
	mat4& operator /= ( const double d ) {
		v[0] /= d; v[1] /= d; v[2] /= d; v[3] /= d; return *this;
	};

	// indexing
	vec4<T>& operator [] ( int i) {
		return v[i];
	};		

        // special functions

	mat4 transpose() {
		return mat4(vec4<T>(v[0][0], v[1][0], v[2][0], v[3][0]),
			    vec4<T>(v[0][1], v[1][1], v[2][1], v[3][1]),
			    vec4<T>(v[0][2], v[1][2], v[2][2], v[3][2]),
			    vec4<T>(v[0][3], v[1][3], v[2][3], v[3][3]));

	};
#if 0
	mat4 inverse() {
		// As a evolves from original mat into identity, 
		// b evolves from identity into inverse(a) 
		mat4 a(*this), b(identity3D());   
		int i, j, i1;

		// Loop over cols of a from left to right, 
                // eliminating above and below diag
		for (j=0; j<4; j++) {
			// Find largest pivot in column j among rows j..3
			i1 = j;		    // Row with largest pivot candidate
			for (i=j+1; i<4; i++) {
				if (fabs(a.v[i].n[j]) > fabs(a.v[i1].n[j]))
					i1 = i;
			}

			// Swap rows i1 and j in a and b to put pivot on diagonal
			swap(a.v[i1], a.v[j]);
			swap(b.v[i1], b.v[j]);

			// Scale row j to have a unit diagonal
			if (a.v[j].n[j]==0.)
				VECTOR_ERROR("mat4::inverse: singular matrix; can't invert\n");
			b.v[j] /= a.v[j].n[j];
			a.v[j] /= a.v[j].n[j];

			// Eliminate off-diagonal elems in col j of a, doing identical ops to b
			for (i=0; i<4; i++)
				if (i!=j) {
					b.v[i] -= a.v[i].n[j]*b.v[j];
					a.v[i] -= a.v[i].n[j]*a.v[j];
				}
		}
		return b;
		
	};				
#endif

        // friends

	friend mat4 operator - ET (const mat4& a);			    // -m1
	friend mat4 operator + ET (const mat4& a, const mat4& b);	    // m1 + m2
	friend mat4 operator - ET (const mat4& a, const mat4& b);	    // m1 - m2
	friend mat4 operator * ET (const mat4& a, const mat4& b);		    // m1 * m2
	friend mat4 operator * ET (const mat4& a, const T& d);	    // m1 * 4.0
	friend mat4 operator * ET (const T& d, const mat4& a);	    // 4.0 * m1
	friend mat4 operator / ET (const mat4& a, const T& d);	    // m1 / 3.0
	friend bool operator == ET (const mat4& a, const mat4& b);	    // m1 == m2 ?
	friend bool operator != ET (const mat4& a, const mat4& b);	    // m1 != m2 ?
	friend void swap ET (mat4& a, mat4& b);			    // swap m1 & m2
	
        // necessary friend declarations
	
	friend vec4<T> operator * ET (const mat4& a, const vec4<T>& v);	    // linear transform
	friend vec3<T> operator * ET (const mat4& a, const vec3<T>& v);	    // linear transform
};

// mat4 friends

template<class T>
mat4<T> operator - (const mat4<T>& a) { 
	return mat4<T>(-a.v[0], -a.v[1], -a.v[2], -a.v[3]); 
}

template<class T>
mat4<T> operator + (const mat4<T>& a, const mat4<T>& b) { 
	return mat4<T>(a.v[0] + b.v[0], a.v[1] + b.v[1], 
		       a.v[2] + b.v[2],  a.v[3] + b.v[3]);
}

template<class T>
mat4<T> operator - (const mat4<T>& a, const mat4<T>& b) { 
	return mat4<T>(a.v[0] - b.v[0], a.v[1] - b.v[1], 
		       a.v[2] - b.v[2], a.v[3] - b.v[3]); 
}

template<class T>
mat4<T> operator * (const mat4<T>& ca, const mat4<T>& cb) {
	mat4<T>& a = const_cast<mat4<T>&>(ca);
	mat4<T>& b = const_cast<mat4<T>&>(cb);
    #define ROWCOL(i, j) a.v[i].n[0]*b.v[0].n[j] + a.v[i].n[1]*b.v[1].n[j] + \
    a.v[i].n[2]*b.v[2].n[j] + a.v[i].n[3]*b.v[3].n[j]
    return mat4<T>(
    vec4<T>(ROWCOL(0,0), ROWCOL(0,1), ROWCOL(0,2), ROWCOL(0,3)),
    vec4<T>(ROWCOL(1,0), ROWCOL(1,1), ROWCOL(1,2), ROWCOL(1,3)),
    vec4<T>(ROWCOL(2,0), ROWCOL(2,1), ROWCOL(2,2), ROWCOL(2,3)),
    vec4<T>(ROWCOL(3,0), ROWCOL(3,1), ROWCOL(3,2), ROWCOL(3,3))
    );
    #undef ROWCOL
}

template<class T>
mat4<T> operator * (const mat4<T>& a, const T& d) { 
	return mat4<T>(a.v[0] * d, a.v[1] * d, a.v[2] * d, a.v[3] * d); 
}

template<class T>
mat4<T> operator * (const T& d, const mat4<T>& a) { 
	return a*d; 
}

template<class T>
mat4<T> operator / (const mat4<T>& a, const T& d) { 
	return mat4<T>(a.v[0] / d, a.v[1] / d, a.v[2] / d, a.v[3] / d); 
}

template<class T>
bool operator == (const mat4<T>& a, const mat4<T>& b) { 
	return ((a.v[0] == b.v[0]) && (a.v[1] == b.v[1]) && 
		(a.v[2] == b.v[2]) && (a.v[3] == b.v[3])); 
}

template<class T>
bool operator != (const mat4<T>& a, const mat4<T>& b) { 
	return !(a == b); 
}

template<class T>
void swap(mat4<T>& a, mat4<T>& b) { 
	mat4<T> tmp(a); a = b; b = tmp; 
}

/****************************************************************
*								*
*	       2D functions and 3D functions			*
*								*
****************************************************************/

template<class T>
mat3<T> identity2D();					    

template<class T>
mat3<T> translation2D(vec2<T>& v);				
template<class T>
mat3<T> rotation2D(vec2<T>& Center, const T& angleDeg);

template<class T>
mat3<T> scaling2D(vec2<T>& scaleVector);			

template<class T>
mat4<T> identity3D(T size = 1.0, T zero=0.0)
{
	return mat4<T>(
		vec4<T>(size,zero,zero,zero),
		vec4<T>(zero,size,zero,zero),
		vec4<T>(zero,zero,size,zero),
		vec4<T>(zero,zero,zero,size));
}

template<class T>
mat4<T> translation3D(vec3<T>& v);
template<class T>
mat4<T> rotation3D(vec3<T>& Axis, const T& angleDeg);
template<class T>
mat4<T> scaling3D(vec3<T>& scaleVector);
template<class T>
mat4<T> perspective3D(const T& d);


// rotations about a plane in 4D; used for Mandelbrot weirdness
template<class T>
mat4<T> rotXY(const T& theta, T one=1.0, T zero=0.0)
{
    T c = cos((T)theta), s = sin((T)theta);
    return mat4<T>(
        vec4<T>(   c,  -s,zero,zero),
        vec4<T>(   s,   c,zero,zero),
        vec4<T>(zero,zero, one,zero),
        vec4<T>(zero,zero,zero, one));
}

template<class T>
mat4<T> rotXZ(const T& theta, T one=1.0, T zero=0.0)
{
    T c = cos(theta), s = sin(theta);
    return mat4<T>(
        vec4<T>(   c,zero,   s,zero),
        vec4<T>(zero, one,zero,zero),
        vec4<T>(  -s,zero,   c,zero),
        vec4<T>(zero,zero,zero, one));
}

template<class T>
mat4<T> rotXW(const T& theta, T one=1.0, T zero=0.0)
{
    T c = cos(theta), s = sin(theta);
    return mat4<T>(
        vec4<T>(   c,zero,zero,   s),
        vec4<T>(zero, one,zero,zero),
        vec4<T>(zero,zero, one,zero),
        vec4<T>(  -s,zero,zero,   c));
}

template<class T>
mat4<T> rotYZ(const T& theta, T one=1.0, T zero=0.0)
{
    T c = cos(theta), s = sin(theta);
    return mat4<T>(
        vec4<T>( one,zero,zero,zero),
        vec4<T>(zero,   c,  -s,zero),
        vec4<T>(zero,   s,   c,zero),
        vec4<T>(zero,zero,zero, one));
}

template<class T>
mat4<T> rotYW(const T& theta, T one=1.0, T zero=0.0)
{
    T c = cos(theta), s = sin(theta);
    return mat4<T>(
        vec4<T>( one,zero,zero,zero),
        vec4<T>(zero,   c,zero,   s),
        vec4<T>(zero,zero, one,zero),
        vec4<T>(zero,  -s,zero,   c));
}

template<class T>
mat4<T> rotZW(const T& theta, T one=1.0, T zero=0.0)
{
    T c = cos(theta), s = sin(theta);
    return mat4<T>(
        vec4<T>( one,zero,zero,zero),
        vec4<T>(zero, one,zero,zero),
        vec4<T>(zero,zero,   c,  -s),
        vec4<T>(zero,zero,   s,   c));
}

#endif 
