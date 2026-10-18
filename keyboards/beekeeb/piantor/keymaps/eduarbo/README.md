Overview
========

This is my personal Piantor configuration, and my daily driver.

Most of the code resides in my userspace, rather than here, as I have other keyboards.


## How to flash

1. Push and hold the BOOTSEL button on the Pico, then connect to your computer using a micro USB cable. Release BOOTSEL once the drive RPI-RP2 appears on your computer.

2. Flash the right split:

       qmk compile -kb beekeeb/piantor -km eduarbo -t uf2-split-right

3. Flash the left split:

       qmk compile -kb beekeeb/piantor -km eduarbo -t uf2-split-left

See the [userspace README](../../../../../users/eduarbo/README.md) for prerequisites and setup instructions.

## Layers

* BASE_MAC: Default at every boot. QWERTY with Backspace on the slash key and mod-tap thumbs
* BASE (Winux): Same layout with Control and GUI swapped on the thumbs; toggled for the current session from Adjust
* SYMBOLS: Numpad on the left, symbols and arrows on the right
* FKEYS: Function keys on the left, media and brightness on the right
* ADJUST: Firmware controls plus the BASE and GAMEPAD toggles
* GAMEPAD: QWERTY shifted to the right for FPS games

Diagrams and the full behavior contract are in the [userspace README](../../../../../users/eduarbo/README.md).
