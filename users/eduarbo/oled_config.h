// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#define OLED_FONT_H "keyboards/crkbd/lib/glcdfont.c"
#define USE_OLED_COMPRESSION
#define OLED_TIMEOUT 300000 // 5 * 60 * 1000 = 5 mins

// WPM-responsive animation stuff here
#define IDLE_FRAMES 5
#define IDLE_SPEED 20  // below this wpm value your animation will idle
#define TAP_FRAMES 2
#define TAP_SPEED 40             // above this wpm value typing animation to trigger
#define ANIM_FRAME_DURATION 200  // how long each frame lasts in ms
/* #define ANIM_SIZE 636            // number of bytes in array, minimize for adequate firmware size, max is 1024 */
#define NUM_OLED_BYTES 512
