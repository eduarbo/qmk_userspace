// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#include "eduarbo.h"

#ifdef OS_DETECTION_ENABLE
os_variant_t os_type;

uint32_t startup_exec(uint32_t trigger_time, void *cb_arg) {
    if (is_keyboard_master()) {
        os_type = detected_host_os();
        switch (os_type) {
            case OS_IOS:
            case OS_MACOS:
                set_single_persistent_default_layer(_BASE_MAC);
                break;
            default:
                set_single_persistent_default_layer(_BASE);
                break;
        }
    }

    return os_type ? 0 : 500;
}

void keyboard_post_init_user(void) {
    defer_exec(100, startup_exec, NULL);
}
#endif
