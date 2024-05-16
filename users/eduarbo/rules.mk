SRC += process_records.c
SRC += callbacks.c

# CONSOLE_ENABLE = yes
# OS_DETECTION_DEBUG_ENABLE = yes

CAPS_WORD_ENABLE ?= yes
RGBLIGHT_ENABLE ?= no
RGB_MATRIX_ENABLE ?= no

OS_DETECTION_ENABLE ?= yes
ifeq ($(strip $(OS_DETECTION_ENABLE)), yes)
    DEFERRED_EXEC_ENABLE = yes
endif

OLED_ENABLE ?= no
ifeq ($(strip $(OLED_ENABLE)), yes)
	WPM_ENABLE = yes        # required by bongocat

	SRC += oled_setup.c
	SRC += bongocat.c
	SRC += ocean_dream.c
	SRC += oled_eduarbo.c
endif
