#include <stdint.h>

uint32_t pack_markers(uint16_t s1, uint16_t s2) {
    return ((uint32_t)s1 << 14) | (s2 & 0x3FFF);
}
