// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "oled_bongocat.h"

void render_bongo_cat(void) {
    // assumes 1 frame prep stagen
    if (get_current_wpm() != 000) {
        oled_on(); // not essential but turns on animation OLED with any alpha keypress
        if (timer_elapsed32(anim_timer) > ANIM_FRAME_DURATION) {
            anim_timer = timer_read32();
            animation_phase();
        }
        anim_sleep = timer_read32();
    } else {
        if (timer_elapsed32(anim_sleep) > OLED_TIMEOUT) {
            oled_off();
        } else {
            if (timer_elapsed32(anim_timer) > ANIM_FRAME_DURATION) {
                anim_timer = timer_read32();
                animation_phase();
            }
        }
    }
}

void animation_phase(void) {
    if (get_current_wpm() <= IDLE_SPEED) {
        current_idle_frame = (current_idle_frame + 1) % IDLE_FRAMES;
        uint8_t idx        = abs((IDLE_FRAMES - 1) - current_idle_frame);
#ifdef USE_OLED_COMPRESSION
        oled_write_compressed_P(idle_maps[idx], idle_lists[idx]);
#else
        oled_write_raw_P(idle[idx], ANIM_SIZE);
#endif // USE_OLED_COMPRESSION
    }
    if (get_current_wpm() > IDLE_SPEED && get_current_wpm() < TAP_SPEED) {
#ifdef USE_OLED_COMPRESSION
        oled_write_compressed_P(prep_map, prep_list);
#else
        oled_write_raw_P(prep[0], ANIM_SIZE); // remove if IDLE_FRAMES >1
                                              // oled_write_raw_P(prep[abs((PREP_FRAMES-1)-current_prep_frame)], ANIM_SIZE);
#endif // USE_OLED_COMPRESSION
    }
    if (get_current_wpm() >= TAP_SPEED) {
        current_tap_frame = (current_tap_frame + 1) % TAP_FRAMES;
        uint8_t idx       = abs((TAP_FRAMES - 1) - current_tap_frame);
#ifdef USE_OLED_COMPRESSION
        oled_write_compressed_P(tap_maps[idx], tap_lists[idx]);
#else
        oled_write_raw_P(tap[idx], ANIM_SIZE);
#endif
    }
}

#ifdef USE_OLED_COMPRESSION
void oled_write_compressed_P(const char* input_block_map, const char* input_block_list) {
    uint16_t block_index = 0;
    for (uint16_t i = 0; i < NUM_OLED_BYTES; i++) {
        uint8_t bit          = i % 8;
        uint8_t map_index    = i / 8;
        uint8_t _block_map   = (uint8_t)pgm_read_byte_near(input_block_map + map_index);
        uint8_t nonzero_byte = (_block_map & (1 << bit));
        if (nonzero_byte) {
            const char data = (const char)pgm_read_byte_near(input_block_list + block_index++);
            oled_write_raw_byte(data, i);
        } else {
            const char data = (const char)0x00;
            oled_write_raw_byte(data, i);
        }
    }
}
#endif // USE_OLED_COMPRESSION
