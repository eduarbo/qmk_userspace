// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "quantum.h"

// To make your own pixel art:
// save a png/jpeg of an 128x32 image (resource: https://www.pixilart.com/draw )
// follow this guide up to and including "CONVERT YOUR IMAGE" https://docs.splitkb.com/hc/en-us/articles/360013811280-How-do-I-convert-an-image-for-use-on-an-OLED-display-
// replace numbers in brackets with your own
void render_eduarbo(void) {
    static const char PROGMEM eduarbo_logo_l_1[] = {0xdc, 0x44, 0x44, 0x4c, 0x44, 0x44, 0xdc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    static const char PROGMEM eduarbo_logo_l_2[] = {0x5d, 0x55, 0x55, 0xd5, 0x55, 0x55, 0xd4, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x10, 0x12, 0x1e, 0xfc};
    static const char PROGMEM eduarbo_logo_l_3[] = {0xa5, 0xa5, 0xa5, 0xbd, 0x95, 0x95, 0x8d, 0x00, 0x00, 0x00, 0x00, 0x38, 0x45, 0x47, 0x47, 0x7f};
    static const char PROGMEM eduarbo_logo_l_4[] = {0x77, 0x54, 0x54, 0x53, 0x52, 0x52, 0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

    static const char PROGMEM eduarbo_logo_r_1[] = {0x8e, 0x4a, 0x4a, 0xca, 0x2a, 0x2a, 0xee, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    static const char PROGMEM eduarbo_logo_r_2[] = {0xb1, 0xa9, 0xa9, 0xbd, 0xa5, 0xa5, 0xa5, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xe2, 0xe2, 0xa2, 0x1c};
    static const char PROGMEM eduarbo_logo_r_3[] = {0x2b, 0xaa, 0xaa, 0xab, 0xaa, 0xaa, 0xba, 0x00, 0x00, 0x00, 0x00, 0x3f, 0x78, 0x48, 0x08, 0x07};
    static const char PROGMEM eduarbo_logo_r_4[] = {0x3b, 0x22, 0x22, 0x32, 0x22, 0x22, 0x3b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

    if (is_keyboard_left()) {
        oled_set_cursor(1, 0);
        oled_write_raw_P(eduarbo_logo_l_1, sizeof(eduarbo_logo_l_1));
        oled_set_cursor(1, 1);
        oled_write_raw_P(eduarbo_logo_l_2, sizeof(eduarbo_logo_l_2));
        oled_set_cursor(1, 2);
        oled_write_raw_P(eduarbo_logo_l_3, sizeof(eduarbo_logo_l_3));
        oled_set_cursor(1, 3);
        oled_write_raw_P(eduarbo_logo_l_4, sizeof(eduarbo_logo_l_4));
    } else {
        oled_set_cursor(1, 0);
        oled_write_raw_P(eduarbo_logo_r_1, sizeof(eduarbo_logo_r_1));
        oled_set_cursor(1, 1);
        oled_write_raw_P(eduarbo_logo_r_2, sizeof(eduarbo_logo_r_2));
        oled_set_cursor(1, 2);
        oled_write_raw_P(eduarbo_logo_r_3, sizeof(eduarbo_logo_r_3));
        oled_set_cursor(1, 3);
        oled_write_raw_P(eduarbo_logo_r_4, sizeof(eduarbo_logo_r_4));
    }
}
