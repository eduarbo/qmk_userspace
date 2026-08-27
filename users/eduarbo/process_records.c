// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "eduarbo.h"
#include "version.h"

typedef enum {
    SUPER_FN_NONE,
    SUPER_FN_SPACE,
    SUPER_FN_THUMB,
} super_fn_source_t;

enum fkeys_owner {
    FKEYS_OWNER_SUPER_FN    = 1 << 0,
    FKEYS_OWNER_GAMEPAD_FN  = 1 << 1,
    FKEYS_OWNER_ESCAPE      = 1 << 2,
    FKEYS_OWNER_GAMEPAD_ALT = 1 << 3,
};

static bool     super_key_held;
static bool     symbols_key_held;
static bool     space_key_held;
static bool     right_fn_key_held;
static uint16_t right_fn_held_keycode;

/* Once a chord takes ownership, its releases must not reach the original
 * Mod-Tap/Layer-Tap actions. This prevents a survivor from becoming sticky. */
static bool super_event_owned;
static bool symbols_event_owned;
static bool space_event_owned;
static bool right_fn_event_owned;
static bool gamepad_fkeys_active;
static bool escape_fkeys_active;
static bool gamepad_alt_fkeys_active;

static uint8_t fkeys_owners;
static bool    fkeys_was_preexisting;
static uint8_t gamepad_alt_fkeys_restore_mod;

static struct {
    bool    active;
    uint8_t weak_mods_added;
} hyper_state;

static struct {
    bool              active;
    bool              right_mod_registered;
    super_fn_source_t source;
    uint16_t          source_keycode;
    uint8_t           right_mod;
} super_fn_state;

static void acquire_fkeys(uint8_t owner) {
    if (fkeys_owners & owner) {
        return;
    }
    if (!fkeys_owners) {
        fkeys_was_preexisting = IS_LAYER_ON(_FKEYS);
        if (!fkeys_was_preexisting) {
            layer_on(_FKEYS);
        }
    }
    fkeys_owners |= owner;
}

static void release_fkeys(uint8_t owner) {
    if (!(fkeys_owners & owner)) {
        return;
    }
    fkeys_owners &= ~owner;
    if (!fkeys_owners) {
        if (!fkeys_was_preexisting) {
            layer_off(_FKEYS);
        }
        fkeys_was_preexisting = false;
    }
}

static bool is_mac_base(void) {
    return get_highest_layer(default_layer_state) == _BASE_MAC;
}

static uint8_t right_fn_mod_for_base(void) {
    return is_mac_base() ? MOD_BIT(KC_RCTL) : MOD_BIT(KC_RGUI);
}

static uint8_t right_mod_for_keycode(uint16_t keycode) {
    return keycode == F16_RCTL ? MOD_BIT(KC_RCTL) : MOD_BIT(KC_RGUI);
}

static void tap_code_with_exact_mods(uint16_t keycode, uint8_t mods) {
    const uint8_t saved_mods         = get_mods();
    const uint8_t saved_weak_mods    = get_weak_mods();
    const uint8_t saved_oneshot_mods = get_oneshot_mods();

    set_mods(mods);
    set_weak_mods(0);
    set_oneshot_mods(0);
    send_keyboard_report();
    tap_code(keycode);
    set_mods(saved_mods);
    set_weak_mods(saved_weak_mods);
    set_oneshot_mods(saved_oneshot_mods);
    send_keyboard_report();
}

static void enter_hyper(void) {
    const uint8_t weak_mods = get_weak_mods();

    super_event_owned   = true;
    symbols_event_owned = true;

    unregister_mods(SUPER_MOD);
    layer_off(_SYMBOLS);

    hyper_state.weak_mods_added = HYPER_MOD & ~weak_mods;
    add_weak_mods(hyper_state.weak_mods_added);
    send_keyboard_report();
    hyper_state.active = true;
}

static void leave_hyper(void) {
    del_weak_mods(hyper_state.weak_mods_added);
    send_keyboard_report();
    hyper_state.weak_mods_added = 0;
    hyper_state.active          = false;

    if (super_key_held) {
        register_mods(SUPER_MOD);
    }
    if (symbols_key_held) {
        layer_on(_SYMBOLS);
    }
}

static void enter_super_fn(super_fn_source_t source, uint16_t source_keycode) {
    super_fn_state.active         = true;
    super_fn_state.source         = source;
    super_fn_state.source_keycode = source_keycode;
    super_fn_state.right_mod      = source == SUPER_FN_SPACE ? right_fn_mod_for_base() : right_mod_for_keycode(source_keycode);

    super_event_owned = true;
    if (source == SUPER_FN_SPACE) {
        space_event_owned = true;
    } else {
        right_fn_event_owned = true;
        unregister_mods(super_fn_state.right_mod);
    }

    unregister_mods(SUPER_MOD);
    acquire_fkeys(FKEYS_OWNER_SUPER_FN);
}

static void release_super_from_fn(void) {
    unregister_mods(SUPER_MOD);
    if ((super_fn_state.source == SUPER_FN_SPACE && space_key_held) || (super_fn_state.source == SUPER_FN_THUMB && right_fn_key_held)) {
        register_mods(super_fn_state.right_mod);
        super_fn_state.right_mod_registered = true;
    }
}

static void release_source_from_fn(void) {
    if (super_fn_state.right_mod_registered) {
        unregister_mods(super_fn_state.right_mod);
        super_fn_state.right_mod_registered = false;
    }
    release_fkeys(FKEYS_OWNER_SUPER_FN);
    if (super_key_held) {
        register_mods(SUPER_MOD);
    }
    super_fn_state.active = false;
    super_fn_state.source = SUPER_FN_NONE;
}

/**
 * @brief Main user keycode handler
 *
 * This handles all of the keycodes for the user, including calling feature handlers.
 *
 * @param keycode Keycode from matrix
 * @param record keyrecord_t data structure
 * @return true Continue processing keycode and send to host
 * @return false Stop process keycode and do not send to host
 */
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    const uint8_t mods             = get_mods();
    const uint8_t os_mods          = get_oneshot_mods();
    const bool    super_mod_active = !hyper_state.active && !super_fn_state.active && (mods & SUPER_MOD) == SUPER_MOD && !(mods & MOD_MASK_SHIFT);

    switch (keycode) {
        case TG_BASE:
            if (record->event.pressed) {
                if (get_highest_layer(default_layer_state) == _BASE_MAC) {
                    set_single_persistent_default_layer(_BASE);
                } else {
                    set_single_persistent_default_layer(_BASE_MAC);
                }
                return false;
            }
            break;

        case ACUTE_LSFT:
        case TILDE_LSFT:
            if (record->tap.count) {
                if (record->event.pressed) {
                    const uint8_t  accent_mod = is_mac_base() ? MOD_BIT(KC_LALT) : MOD_BIT(KC_RALT);
                    const uint16_t accent_key = keycode == ACUTE_LSFT ? KC_E : KC_N;
                    tap_code_with_exact_mods(accent_key, accent_mod);
                }
                return false;
            }
            break;

        case KC_PGUP:
            if (record->event.pressed) {
                if ((mods & MOD_BIT(KC_LSFT)) == MOD_BIT(KC_LSFT)) {
                    unregister_code(KC_LSFT);
                    tap_code(KC_HOME);
                    register_code(KC_LSFT);
                    return false;
                }
            }
            break;

        case KC_PGDN:
            if (record->event.pressed) {
                if ((mods & MOD_BIT(KC_LSFT)) == MOD_BIT(KC_LSFT)) {
                    unregister_code(KC_LSFT);
                    tap_code(KC_END);
                    register_code(KC_LSFT);
                    return false;
                }
            }
            break;

        case VRSN: // Prints firmware version
            if (record->event.pressed) {
                send_string_with_delay_P(PSTR(QMK_KEYBOARD "/" QMK_KEYMAP " @ " QMK_VERSION ", Built on: " QMK_BUILDDATE), TAP_CODE_DELAY);
            }
            break;

        case SPC_LSFT:
            if (record->tap.count) {
                if (record->event.pressed) {
                    if (super_mod_active) {
                        tap_code_with_exact_mods(KC_F16, 0);
                    } else if (IS_LAYER_ON(_SYMBOLS)) {
                        tap_code_with_exact_mods(KC_SPC, MOD_BIT(KC_LSFT));
                    } else if (is_mac_base() && (mods & MOD_BIT(KC_RGUI))) {
                        // Match Left Command+Space without leaking Right Command into the tap.
                        tap_code_with_exact_mods(KC_ENT, MOD_BIT(KC_LSFT));
                    } else {
                        return true;
                    }
                }
                if (super_mod_active || IS_LAYER_ON(_SYMBOLS) ||
                    (is_mac_base() && (mods & MOD_BIT(KC_RGUI)))) {
                    return false;
                }
            } else if (record->event.pressed) {
                space_key_held = true;
                if (super_mod_active) {
                    enter_super_fn(SUPER_FN_SPACE, keycode);
                    return false;
                }
            } else {
                space_key_held = false;
                if (super_fn_state.active && super_fn_state.source == SUPER_FN_SPACE) {
                    release_source_from_fn();
                    space_event_owned = false;
                    return false;
                }
                if (space_event_owned) {
                    unregister_mods(right_fn_mod_for_base());
                    space_event_owned = false;
                    return false;
                }
            }
            break;

        case ESC_SUPR: {
            if (record->tap.count && record->event.pressed) {
                // on tap
                if (IS_LAYER_ON(_SYMBOLS)) {
                    tap_code16(S(KC_ESC));
                    return false;
                } else if (os_mods && !has_oneshot_mods_timed_out()) {
                    // Clear one shot mods when pressing ESC
                    clear_oneshot_mods();
                    unregister_mods(os_mods);
                }
            } else if (record->event.pressed) {
                // on hold keydown
                super_key_held = true;
                if (symbols_key_held) {
                    enter_hyper();
                    return false;
                } else if (right_fn_key_held) {
                    enter_super_fn(SUPER_FN_THUMB, right_fn_held_keycode);
                    return false;
                } else if ((mods & MOD_BIT(KC_RCTL)) == MOD_BIT(KC_RCTL)) {
                    unregister_code(KC_RCTL);
                    if (is_mac_base()) {
                        acquire_fkeys(FKEYS_OWNER_ESCAPE);
                        escape_fkeys_active = true;
                    } else {
                        layer_on(_ADJUST);
                    }
                    return false;
                } else if ((mods & MOD_BIT(KC_RGUI)) == MOD_BIT(KC_RGUI)) {
                    unregister_code(KC_RGUI);
                    layer_on(_ADJUST);
                    return false;
                } else if ((mods & MOD_BIT(KC_RALT)) == MOD_BIT(KC_RALT)) {
                    unregister_code(KC_RALT);
                    layer_on(_ADJUST);
                    return false;
                }
            } else {
                // on hold keyup
                super_key_held = false;
                if (hyper_state.active) {
                    leave_hyper();
                    super_event_owned = false;
                    return false;
                } else if (super_fn_state.active) {
                    release_super_from_fn();
                    super_event_owned = false;
                    return false;
                } else if (super_event_owned) {
                    unregister_mods(SUPER_MOD);
                    super_event_owned = false;
                    return false;
                } else if (escape_fkeys_active) {
                    release_fkeys(FKEYS_OWNER_ESCAPE);
                    register_code(KC_RCTL);
                    escape_fkeys_active = false;
                    return false;
                } else if (IS_LAYER_ON(_ADJUST)) {
                    layer_off(_ADJUST);
                    if (is_mac_base()) {
                        register_code(KC_RGUI);
                    } else {
                        register_code(KC_RCTL);
                    }
                    return false;
                }
            }
            break;
        }

        case TAB_SYMB: {
            if (record->tap.count) {
                if (record->event.pressed && super_mod_active) {
                    set_oneshot_mods(os_mods | MOD_BIT(KC_RALT));
                }
                if (super_mod_active) {
                    return false;
                }
            } else if (record->event.pressed) {
                // on hold keydown
                symbols_key_held = true;
                if (super_key_held && !super_fn_state.active) {
                    enter_hyper();
                    return false;
                }
            } else {
                // on hold keyup
                symbols_key_held = false;
                if (hyper_state.active) {
                    leave_hyper();
                    symbols_event_owned = false;
                    return false;
                }
                if (symbols_event_owned) {
                    layer_off(_SYMBOLS);
                    symbols_event_owned = false;
                    return false;
                }
            }
            break;
        }

        case ENT_RCTL:
        case ENT_RGUI: {
#ifdef OLED_ENABLE
            is_calm = (record->event.pressed) ? true : false;
#endif

            if (record->tap.count) {
                if (record->event.pressed) {
                    // on tap
                    if (super_mod_active) {
                        if (keycode == ENT_RCTL) {
                            set_oneshot_mods(os_mods | MOD_BIT(KC_RCTL));
                        } else if (keycode == ENT_RGUI) {
                            set_oneshot_mods(os_mods | MOD_BIT(KC_RGUI));
                        }
                    } else if (IS_LAYER_ON(_SYMBOLS)) {
                        tap_code_with_exact_mods(KC_ENT, is_mac_base() ? MOD_BIT(KC_LGUI) : MOD_BIT(KC_LCTL));
                    } else {
                        return true;
                    }
                }
                if (super_mod_active || IS_LAYER_ON(_SYMBOLS)) {
                    return false;
                }
            } else if (record->event.pressed) {
                // on hold keydown
                if (super_mod_active) {
                    unregister_mods(SUPER_MOD);
                    layer_on(_ADJUST);
                    return false;
                } else if (IS_LAYER_ON(_GAMEPAD) && ((mods & MOD_BIT(KC_LALT)) == MOD_BIT(KC_LALT))) {
                    unregister_code(KC_LALT);
                    layer_on(_ADJUST);
                    return false;
                }
            } else {
                // on hold keyup
                if (IS_LAYER_ON(_ADJUST)) {
                    layer_off(_ADJUST);
                    if (IS_LAYER_ON(_GAMEPAD)) {
                        register_code(KC_LALT);
                    }
                    return false;
                }
            }
            break;
        }

        case F16_RGUI:
        case F16_RCTL: {
            if (record->tap.count) {
                if (record->event.pressed) {
                    // on tap
                    if (super_mod_active) {
                        if (keycode == F16_RGUI) {
                            set_oneshot_mods(os_mods | MOD_BIT(KC_RGUI));
                        } else if (keycode == F16_RCTL) {
                            set_oneshot_mods(os_mods | MOD_BIT(KC_RCTL));
                        }
                    } else {
                        tap_code16(KC_F16);
                    }
                }
                return false;
            } else if (record->event.pressed) {
                // on hold keydown
                right_fn_key_held     = true;
                right_fn_held_keycode = keycode;
                if (super_mod_active) {
                    enter_super_fn(SUPER_FN_THUMB, keycode);
                    return false;
                } else if (IS_LAYER_ON(_GAMEPAD) && ((mods & MOD_BIT(KC_LALT)) == MOD_BIT(KC_LALT))) {
                    unregister_code(KC_LALT);
                    gamepad_fkeys_active = true;
                    acquire_fkeys(FKEYS_OWNER_GAMEPAD_FN);
                    return false;
                }
            } else {
                // on hold keyup
                right_fn_key_held = false;
                if (super_fn_state.active && super_fn_state.source == SUPER_FN_THUMB && super_fn_state.source_keycode == keycode) {
                    release_source_from_fn();
                    if (gamepad_fkeys_active) {
                        release_fkeys(FKEYS_OWNER_GAMEPAD_FN);
                        gamepad_fkeys_active = false;
                    }
                    right_fn_event_owned = false;
                    return false;
                }
                if (right_fn_event_owned) {
                    unregister_mods(right_mod_for_keycode(keycode));
                    right_fn_event_owned = false;
                    return false;
                }
                if (gamepad_fkeys_active) {
                    release_fkeys(FKEYS_OWNER_GAMEPAD_FN);
                    gamepad_fkeys_active = false;
                    return false;
                }
            }
            break;
        }

        case KC_LALT: {
            //   Do nothing if is not in the GAMEPAD Layer
            if (!IS_LAYER_ON(_GAMEPAD)) {
                return true;
            }

            if (record->tap.count && record->event.pressed) {
                // on tap
            } else if (record->event.pressed) {
                // on hold keydown
                if ((mods & MOD_BIT(KC_RCTL)) == MOD_BIT(KC_RCTL)) {
                    unregister_code(KC_LALT);
                    if (is_mac_base()) {
                        acquire_fkeys(FKEYS_OWNER_GAMEPAD_ALT);
                        gamepad_alt_fkeys_active      = true;
                        gamepad_alt_fkeys_restore_mod = MOD_BIT(KC_RCTL);
                    } else {
                        layer_on(_ADJUST);
                    }
                    return false;
                } else if ((mods & MOD_BIT(KC_RGUI)) == MOD_BIT(KC_RGUI)) {
                    unregister_code(KC_LALT);
                    if (is_mac_base()) {
                        layer_on(_ADJUST);
                    } else {
                        acquire_fkeys(FKEYS_OWNER_GAMEPAD_ALT);
                        gamepad_alt_fkeys_active      = true;
                        gamepad_alt_fkeys_restore_mod = MOD_BIT(KC_RGUI);
                    }
                    return false;
                }
            } else {
                // on hold keyup
                if (gamepad_alt_fkeys_active) {
                    release_fkeys(FKEYS_OWNER_GAMEPAD_ALT);
                    register_mods(gamepad_alt_fkeys_restore_mod);
                    gamepad_alt_fkeys_active      = false;
                    gamepad_alt_fkeys_restore_mod = 0;
                    return false;
                } else if (IS_LAYER_ON(_ADJUST)) {
                    layer_off(_ADJUST);
                    if (is_mac_base()) {
                        register_code(KC_RGUI);
                    } else {
                        register_code(KC_RCTL);
                    }
                    return false;
                }
            }
            break;
        }

        case KC_E:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    if (get_highest_layer(default_layer_state) == _BASE_MAC) {
                        tap_code16(MAC_DEVTOOLS);
                    } else {
                        tap_code16(DEVTOOLS);
                    }
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;

        case KC_R:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    if (get_highest_layer(default_layer_state) == _BASE_MAC) {
                        tap_code16(MAC_INSP_ELE);
                    } else {
                        tap_code16(INSP_ELE);
                    }
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;

        case KC_T:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    if (get_highest_layer(default_layer_state) == _BASE_MAC) {
                        tap_code16(MAC_TGL_EXEC);
                    } else {
                        tap_code16(TGL_EXEC);
                    }
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;

        case KC_S:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    tap_code16(PREV_TAB);
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;

        case KC_G:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    tap_code16(NEXT_TAB);
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;

        case KC_D:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    if (get_highest_layer(default_layer_state) == _BASE_MAC) {
                        tap_code16(MAC_GO_BACK);
                    } else {
                        tap_code16(GO_BACK);
                    }
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;

        case KC_F:
            if (super_mod_active) {
                if (record->event.pressed) {
                    unregister_mods(SUPER_MOD);
                    if (get_highest_layer(default_layer_state) == _BASE_MAC) {
                        tap_code16(MAC_GO_FWD);
                    } else {
                        tap_code16(GO_FWD);
                    }
                    register_mods(SUPER_MOD);
                }
                return false;
            }
            break;
    }
    return true;
}
