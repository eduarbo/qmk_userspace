# Piantor keymap

The keymap lives in the [shared userspace](../../../../../users/eduarbo/README.md). This
folder only sets Piantor hardware options: either half can be the main one (`EE_HANDS`),
and USB is detected on the Pico's VBUS pin.

Flash each half with its side, then follow the guide's bootloader steps:

```sh
qmk flash -kb beekeeb/piantor -km eduarbo -bl uf2-split-left
qmk flash -kb beekeeb/piantor -km eduarbo -bl uf2-split-right
```
