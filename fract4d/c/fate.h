#ifndef FATE_H_
#define FATE_H_

#include <limits>

/* the 'fate' of a point. This can be either
   Unknown (255) - not yet calculated
   0 - passed bailout test and escaped
   1 - 127 - trapped in an attractor with this index
*/

typedef unsigned char fate_t;

#define FATE_UNKNOWN std::numeric_limits<fate_t>::max()
#define FATE_SOLID 0x80


#endif /* COLOR_H_ */
