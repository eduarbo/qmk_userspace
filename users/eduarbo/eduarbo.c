// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "eduarbo.h"

// Always boot into the macOS base. TG_BASE only switches the base for the
// current session, so reconnecting the keyboard restores macOS even when an
// older firmware left another default layer in EEPROM.
void keyboard_post_init_user(void) {
    set_single_default_layer(_BASE_MAC);
}

#if defined(CAPS_WORD_ENABLE)
// Define custom Caps Word continuity characters
bool caps_word_press_user(uint16_t keycode) {
    switch (keycode) {
        // Keycodes that continue Caps Word, with shift applied.
        case KC_A ... KC_Z:
        case KC_TILD:
        case KC_UNDS:
        case KC_DQT:
        case KC_COLN:
        case KC_RSFT:
        case KC_LSFT:
            add_weak_mods(MOD_BIT(KC_LSFT)); // Apply shift to next key.
            return true;

        // Keycodes that continue Caps Word, without shifting.
        case KC_1 ... KC_0:
        case KC_GRV:
        case KC_MINS:
        case KC_QUOT:
        case KC_SCLN:
        case KC_BSPC:
        case KC_DEL:
            return true;

        default:
            return false; // Deactivate Caps Word.
    }
}
#endif
