// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "eduarbo.h"

#ifdef OS_DETECTION_ENABLE
os_variant_t os_type;

static uint8_t os_detect_retries = 0;
#define OS_DETECT_MAX_RETRIES 20

// Require N consecutive identical detections before switching layers to filter
// out transient misdetections during USB bus resets (sleep/wake, display changes)
#define OS_DETECT_CONSENSUS_THRESHOLD 3
static uint8_t os_consensus_count = 0;
static os_variant_t last_detected_os = OS_UNSURE;

static void apply_detected_os(os_variant_t os) {
    switch (os) {
        case OS_IOS:
        case OS_MACOS:
            default_layer_set(1UL << _BASE_MAC);
            break;
        case OS_WINDOWS:
        case OS_LINUX:
        default:
            default_layer_set(1UL << _BASE);
            break;
    }
}

uint32_t startup_exec(uint32_t trigger_time, void *cb_arg) {
    if (is_keyboard_master()) {
        os_type = detected_host_os();

        if (os_type == OS_UNSURE) {
            os_consensus_count = 0;
            if (++os_detect_retries < OS_DETECT_MAX_RETRIES) {
                return 500;
            }
            default_layer_set(1UL << _BASE_MAC);
            return 0;
        }

        if (os_type == last_detected_os) {
            os_consensus_count++;
        } else {
            os_consensus_count = 1;
            last_detected_os = os_type;
        }

        if (os_consensus_count < OS_DETECT_CONSENSUS_THRESHOLD) {
            if (++os_detect_retries < OS_DETECT_MAX_RETRIES) {
                return 500;
            }
        }

        apply_detected_os(os_type);
    }

    return 0;
}

void keyboard_post_init_user(void) {
    defer_exec(100, startup_exec, NULL);
}
#endif
