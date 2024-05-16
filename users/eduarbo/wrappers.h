// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include "eduarbo.h"

/*
Blocks for each of the four major keyboard layouts
Organized so we can quickly adapt and modify all of them
at once, rather than for each keyboard, one at a time.
And this allows for much cleaner blocks in the keymaps.
For instance Tap/Hold for Control on all of the layouts

NOTE: These are all the same length.  If you do a search/replace
  then you need to add/remove underscores to keep the
  lengths consistent.
*/

#define _____BASE_MAC_MODS_L_____                       ESC_SUPR,     SPC_LSFT,     ENT_RGUI
#define _____BASE_MAC_MODS_R_____                       ENT_RGUI,     TAB_SYMB,     F13_RCTL

#define _______BASE_MODS_L_______                       ESC_SUPR,     SPC_LSFT,     ENT_RCTL
#define _______BASE_MODS_R_______                       ENT_RCTL,     TAB_SYMB,     F13_RGUI

#define ______SYMBOLS_MODS_L_____                       _______,      _______,      _______
#define ______SYMBOLS_MODS_R_____                       _______,      _______,      _______

#define ______F_KEYS_MODS_L______                       _______,      KC_LSFT,      _______
#define ______F_KEYS_MODS_R______                       _______,      KC_RSFT,      _______

#define ______ADJUST_MODS_L______                       _______,      _______,      _______
#define ______ADJUST_MODS_R______                       _______,      _______,      _______

#define ______GAMEPAD_MODS_L_____                       KC_LALT,      KC_SPC,       KC_LCTL
#define ______GAMEPAD_MODS_R_____                       _______,      _______,      _______

#define ___________________________________________     _______, _______, _______, _______, _______
#define XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX

#define _________________QWERTY_L1_________________     KC_Q,    KC_W,    KC_E,    KC_R,    KC_T
#define _________________QWERTY_L2_________________     KC_A,    KC_S,    KC_D,    KC_F,    KC_G
#define _________________QWERTY_L3_________________     KC_Z,    KC_X,    KC_C,    KC_V,    KC_B

#define _________________QWERTY_R1_________________     KC_Y,    KC_U,    KC_I,    KC_O,    KC_P
#define _________________QWERTY_R2_________________     KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN
#define _________________QWERTY_R3_________________     KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_BSPC

#define _________________SYMBOLS_L1________________     KC_HOME, KC_7,    KC_8,    KC_9,    KC_0
#define _________________SYMBOLS_L2________________     KC_END,  KC_4,    KC_5,    KC_6,    KC_EQL
#define _________________SYMBOLS_L3________________     ACCENT,  KC_1,    KC_2,    KC_3,    KC_MINS

#define _________________SYMBOLS_R1________________     KC_BSLS, KC_LBRC, KC_RBRC, KC_SLSH, KC_PGUP
#define _________________SYMBOLS_R2________________     KC_LEFT, KC_DOWN, KC_UP,   KC_RIGHT,KC_PGDN
#define _________________SYMBOLS_R3________________     KC_GRV,  KC_QUOT, _______, _______, _______

#define _________________F_KEYS_L1_________________     KC_F12,  KC_F7,   KC_F8,   KC_F9,   KC_PSCR
#define _________________F_KEYS_L2_________________     KC_F11,  KC_F4,   KC_F5,   KC_F6,   KC_SCRL
#define _________________F_KEYS_L3_________________     KC_F10,  KC_F1,   KC_F2,   KC_F3,   KC_PAUS

#define _________________F_KEYS_R1_________________     KC_VOLU, KC_MRWD, KC_MPLY, KC_MFFD, KC_PSCR
#define _________________F_KEYS_R2_________________     KC_VOLD, TG_GAME, TG_BASE, KC_LPAD, KC_SCRL
#define _________________F_KEYS_R3_________________     KC_MUTE, KC_BRID, KC_BRIU, KC_MCTL, KC_PAUS

#define _________________ADJUST_L1_________________     RGB_TOG, DB_TOGG, QK_RBT,  EE_CLR,  QK_BOOT
#define _________________ADJUST_L2_________________     RGB_RMOD,RGB_HUI, RGB_SAI, RGB_VAI, RGB_SPI
#define _________________ADJUST_L3_________________     RGB_MOD, RGB_HUD, RGB_SAD, RGB_VAD, RGB_SPD

#define _________________ADJUST_R1_________________     XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#define _________________ADJUST_R2_________________     XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#define _________________ADJUST_R3_________________     XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

#define _________________GAMEPAD_L1________________     KC_ESC,  KC_W,    KC_UP,   KC_R,    KC_T
#define _________________GAMEPAD_L2________________     KC_A,    KC_LEFT, KC_DOWN, KC_RIGHT,KC_G
#define _________________GAMEPAD_L3________________     KC_Z,    KC_X,    KC_C,    KC_V,    KC_B

#define _________________GAMEPAD_R1________________     ___________________________________________
#define _________________GAMEPAD_R2________________     ___________________________________________
#define _________________GAMEPAD_R3________________     ___________________________________________
