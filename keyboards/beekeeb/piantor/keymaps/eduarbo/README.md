Overview
========

This is my personal Piantor configuration, and my daily driver.

Most of the code resides in my userspace, rather than here, as I have other keyboards.


## How to flash

1. Push and hold the BOOTSEL button on the Pico, then connect to your computer using a micro USB cable. Release BOOTSEL once the drive RPI-RP2 appears on your computer.

2. Flash both sides using the following command:

```
make beekeeb/piantor:eduarbo:flash
```

## Layers (WIP)

* BASE: Basic Qwerty layout but swapping the slash key with the delete key and turning the modifiers to mod-tap
* WINUX: Only Swaps Ctrl and Gui keys
* SYMBOLS: Numpad on the left, symbols and arrows on the right
* GAMEPAD: This is the QWERTY layout shifted to the right for FPS type games
* FKEYS: Function and Media keys
