#ifndef _POINTFUNC_PUBLIC_H_
#define _POINTFUNC_PUBLIC_H_

/* an enumeration of the available bailout functions */
// update table in interface.cpp:create_bailout_menu if this changes
typedef enum 
{
    BAILOUT_MAG = 0,
    BAILOUT_MANH,
    BAILOUT_MANH2,
    BAILOUT_OR,
    BAILOUT_AND,
} e_bailFunc;

#endif
