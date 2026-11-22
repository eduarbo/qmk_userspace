# Eduardo's QMK userspace

Firmware for my Piantor and Corne, two 36-key splits that share one keymap. The MacBook
keyboard mirrors it with
[Karabiner-Elements](https://github.com/eduarbo/dotfiles/tree/main/macos/karabiner).

**[Find a key or shortcut](users/eduarbo/README.md#find-a-key)** · [Why Symbols has two Shifts](users/eduarbo/README.md#macbook-rollover-and-shift) · [All layer maps](users/eduarbo/README.md#layers) · [Build and flash](users/eduarbo/README.md#build-and-flash)

![QWERTY split with tap and hold actions on the six thumbs](docs/layers/macos.svg)

| Target | Hardware |
| --- | --- |
| `beekeeb/piantor:eduarbo` | Raspberry Pi Pico (RP2040), one UF2 per half |
| `crkbd/rev1:eduarbo` | Pro Micro (AVR), OLED on, RGB Matrix off |

[`qmk.json`](qmk.json) lists both targets for `qmk userspace-compile`. Running the
**Build QMK firmware** workflow in GitHub Actions builds them and replaces the `latest`
release only when both compile.
