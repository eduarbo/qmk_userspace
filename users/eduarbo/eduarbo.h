// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include QMK_KEYBOARD_H

#include "wrappers.h"
#include "callbacks.h"
#include "process_records.h"

#ifdef OS_DETECTION_ENABLE
#    include "os_detection.h"
#endif

#ifdef OLED_ENABLE
#    include "oled_setup.h"
#endif

/* Define layer names */
enum userspace_layers {
    _BASE_MAC = 0,
    _BASE,
    _FKEYS,
    _ADJUST,
    _SYMBOLS,
    _GAMEPAD,
};
