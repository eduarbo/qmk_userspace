/*
This is the c configuration file for the keymap

Copyright 2012 Jun Wako <wakojun@gmail.com>
Copyright 2015 Jack Humbert

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

// Use custom magic number so that when switching branches, EEPROM always gets reset
#define EECONFIG_MAGIC_NUMBER (uint16_t)0x1339

#ifdef OLED_ENABLE
#    include "oled_config.h"
#endif

#ifdef RGBLIGHT_ENABLE
#    include "rgblight_config.h"
#endif // RGBLIGHT_ENABLE

#ifdef RGB_MATRIX_ENABLE
#    include "rgb_matrix_config.h"
#endif // RGB_MATRIX_ENABLE

#if defined(WPM_ENABLE)
// #    define WPM_LAUNCH_CONTROL
// #    define WPM_ALLOW_COUNT_REGRESSOIN
// #    define WPM_UNFILTERED
#    define WPM_SAMPLE_SECONDS 10
#    define WPM_SAMPLE_PERIODS 50
#    define WPM_ESTIMATED_WORD_SIZE 5
#endif

// #define WPM_ESTIMATED_WORD_SIZE 5
#define WPM_ALLOW_COUNT_REGRESSION
// #define WPM_UNFILTERED
// #define WPM_SAMPLE_SECONDS 5
// #define WPM_SAMPLE_PERIODS 50
// #define WPM_LAUNCH_CONTROL


// Mod Tap sane defaults -------------------------------------------------------

// how long before a key press becomes a hold
#define TAPPING_TERM 250
// how many taps before triggering the toggle
#define TAPPING_TOGGLE 3
// remove the auto-repeat ability and activate the hold function instead when tapping twice quickly
#define QUICK_TAP_TERM 0


// Fast typing -----------------------------------------------------------------

// makes tap and hold keys (like Layer Tap) work better for fast typists, or for
// high TAPPING_TERM settings. Compared to the “permissive hold” mode, this mode
// selects the hold action in more cases
#define HOLD_ON_OTHER_KEY_PRESS

// makes it possible to use a dual role key as modifier shortly after having
// been tapped. Breaks any Tap Toggle functionality (TT or the One Shot Tap
// Toggle)
#define QUICK_TAP_TERM 0

#define ONESHOT_TAP_TOGGLE 2
#define ONESHOT_TIMEOUT 3000
