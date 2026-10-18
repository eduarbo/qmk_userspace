// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

enum userspace_custom_keycodes {
    TG_BASE = SAFE_RANGE,
};

#define SUPER_MOD (MOD_BIT(KC_LGUI) | MOD_BIT(KC_LALT) | MOD_BIT(KC_LCTL))
#define HYPER_MOD (MOD_BIT(KC_LGUI) | MOD_BIT(KC_LALT) | MOD_BIT(KC_LCTL) | MOD_BIT(KC_LSFT))

#define ACUTE_LSFT MT(MOD_LSFT, KC_E)
#define TILDE_LSFT MT(MOD_LSFT, KC_N)

#define SPC_LSFT MT(MOD_LSFT, KC_SPC)
#define TAB_SYMB LT(_SYMBOLS, KC_TAB)

#define ESC_SUPR MT(SUPER_MOD, KC_ESC)

#define ENT_RCTL MT(MOD_RCTL, KC_ENT)
#define ENT_RGUI MT(MOD_RGUI, KC_ENT)

#define DEVTOOLS C(S(KC_I))
#define INSP_ELE C(S(KC_C))
#define TGL_EXEC C(KC_BSLS)

#define MAC_DEVTOOLS G(A(KC_I))
#define MAC_INSP_ELE G(A(KC_C))
#define MAC_TGL_EXEC G(KC_BSLS)

#define PREV_TAB C(S(KC_TAB))
#define NEXT_TAB C(KC_TAB)

#define GO_BACK  A(KC_LEFT)
#define GO_FWD   A(KC_RIGHT)
#define MAC_GO_BACK G(KC_LBRC)
#define MAC_GO_FWD  G(KC_RBRC)

// Right Fn thumb: F16 on tap, right modifier on hold. process_record_user()
// handles the tap so Super can turn it into a one-shot modifier instead.
#define F16_RCTL MT(MOD_RCTL, KC_F16)
#define F16_RGUI MT(MOD_RGUI, KC_F16)

#define TG_GAME TG(_GAMEPAD)

