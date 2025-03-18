// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// use either hands as master as long as the flag that determines which half of
// the keyboard it is has been set in the persistent storage (EEPROM)
#define EE_HANDS

// Enabling this option sets startup to listen for USB communication to
// determine master and slave
#define SPLIT_USB_DETECT

// Ensures the current layer state is available on the slave
#define SPLIT_LAYER_STATE_ENABLE
// Ensures the current WPM is available on the slave
#define SPLIT_WPM_ENABLE

// #undef RGBLED_NUM
// #define RGBLED_NUM 12
// #undef RGBLED_SPLIT
// #define RGBLED_SPLIT { 6, 6 }
