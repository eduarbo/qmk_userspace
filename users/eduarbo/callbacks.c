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

static const char *os_variant_name(os_variant_t os) {
    switch (os) {
        case OS_UNSURE: return "UNSURE";
        case OS_LINUX:  return "LINUX";
        case OS_WINDOWS: return "WINDOWS";
        case OS_MACOS:  return "MACOS";
        case OS_IOS:    return "IOS";
        default:        return "UNKNOWN";
    }
}

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

static bool   detection_complete = false;
static uint8_t detection_total_retries = 0;
static bool   detection_reached_consensus = false;

uint32_t print_detection_result(uint32_t trigger_time, void *cb_arg) {
    dprintf("=== OS Detection Result ===\n");
    dprintf("  detected: %s\n", os_variant_name(os_type));
    dprintf("  retries: %u/%u\n", detection_total_retries, OS_DETECT_MAX_RETRIES);
    dprintf("  consensus: %s (%u/%u)\n",
            detection_reached_consensus ? "YES" : "NO",
            os_consensus_count, OS_DETECT_CONSENSUS_THRESHOLD);
    dprintf("  active layer: %s\n",
            get_highest_layer(default_layer_state) == _BASE_MAC ? "MAC" : "BASE");
    dprintf("===========================\n");
    return 0;
}

uint32_t startup_exec(uint32_t trigger_time, void *cb_arg) {
    if (is_keyboard_master()) {
        os_type = detected_host_os();

        if (os_type == OS_UNSURE) {
            os_consensus_count = 0;
            if (++os_detect_retries < OS_DETECT_MAX_RETRIES) {
                return 500;
            }
            detection_complete = true;
            detection_total_retries = os_detect_retries;
            default_layer_set(1UL << _BASE_MAC);
            defer_exec(3000, print_detection_result, NULL);
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
        } else {
            detection_reached_consensus = true;
        }

        detection_complete = true;
        detection_total_retries = os_detect_retries;
        apply_detected_os(os_type);
        defer_exec(3000, print_detection_result, NULL);
    }

    return 0;
}

void keyboard_post_init_user(void) {
    defer_exec(100, startup_exec, NULL);
}
#endif
