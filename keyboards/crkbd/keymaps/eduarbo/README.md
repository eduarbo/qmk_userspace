# Corne keymap

The keymap lives in the [shared userspace](../../../../users/eduarbo/README.md). This
folder only sets Corne hardware options: either half can be the main one (`EE_HANDS`),
the OLEDs show animations and the active layer, and RGB Matrix is off to fit the AVR flash.

Flash each half with its side, then follow the guide's bootloader steps:

```sh
qmk flash -kb crkbd/rev1 -km eduarbo -bl avrdude-split-left
qmk flash -kb crkbd/rev1 -km eduarbo -bl avrdude-split-right
```
