// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "eduarbo.h"

bool oled_horizontal = false; // OLED rotation  (true = horizontal,  false = vertical)

// Set OLED rotation
oled_rotation_t oled_init_user(oled_rotation_t rotation) {
    bool is_master = is_keyboard_master();
    bool is_left = is_keyboard_left();

    if (is_master && !is_left) {
        if (oled_horizontal) {
            return OLED_ROTATION_90;
        } else {
            return OLED_ROTATION_180;
        }
    } else if (!is_master) {
        if (oled_horizontal) {
            return OLED_ROTATION_180;
        } else {
            return OLED_ROTATION_270;
        }
    }
    return rotation;
}

// Writes the current layer state on the screen wherever the cursor is
void render_layer_state(void) {
    if (oled_horizontal) {
        oled_set_cursor(0, 0);
    } else {
        oled_set_cursor(0, 128);
    }

    // NOTE Layer names:
    // Should be exactly 5 characters in length if vertical display
    switch (get_highest_layer(layer_state)) {
        case _GAMEPAD:
            oled_write_P(PSTR("GAMIN"), false);
            break;
        case _SYMBOLS:
            oled_write_P(PSTR("SYMBL"), false);
            break;
        case _ADJUST:
            oled_write_P(PSTR("ADJST"), false);
            break;
        case _FKEYS:
            oled_write_P(PSTR("F-KEY"), false);
            break;
        case _BASE:
            oled_write_P(PSTR("BASE"), false);
            break;
        case _BASE_MAC:
            oled_write_P(PSTR("MACOS"), false);
            break;
        default:
            oled_write_P(PSTR("?????"), false);
    }
}

bool oled_task_user(void) {
    if (is_keyboard_master()) {
        // Write active layer name to display
        render_bongo_cat();
        render_eduarbo();
    } else {
        render_stars();
        render_layer_state();
    }

    return false;
}
