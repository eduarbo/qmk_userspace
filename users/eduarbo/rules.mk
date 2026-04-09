SRC += process_records.c

CAPS_WORD_ENABLE ?= yes
RGBLIGHT_ENABLE ?= no
RGB_MATRIX_ENABLE ?= no

OLED_ENABLE ?= no
ifeq ($(strip $(OLED_ENABLE)), yes)
	WPM_ENABLE = yes        # required by bongocat

	SRC += oled_setup.c
	SRC += bongocat.c
	SRC += ocean_dream.c
	SRC += oled_eduarbo.c
endif
