// Copyright 2021 Jonathan Law, Jay Greco
// Copyright 2023 Eduardo Ruiz Macias (@eduarbo) <eduarbo@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include "quantum.h"

void render_bongo_cat(void);
void animation_phase(void);
#ifdef USE_OLED_COMPRESSION
void oled_write_compressed_P(const char* input_block_map, const char* input_block_list);
#endif // USE_OLED_COMPRESSION
