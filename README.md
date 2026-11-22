# Eduardo's QMK userspace

Firmware for my Piantor and Corne, two 36-key splits that share one keymap. The MacBook
keyboard mirrors it with
[Karabiner-Elements](https://github.com/eduarbo/dotfiles/tree/main/macos/karabiner).

**[Find a key or shortcut](users/eduarbo/README.md#find-a-key)** · [Split and MacBook thumbs](users/eduarbo/README.md#base-and-thumbs) · [All layer maps](users/eduarbo/README.md#layers) · [Build and flash](users/eduarbo/README.md#build-and-flash)

<picture>
  <source media="(max-width: 600px)" srcset="docs/cover/layout-mobile.webp">
  <img src="docs/cover/layout.webp" alt="The 36-key split above its MacBook equivalents. The six split thumbs correspond to left Option, left Command, the space bar, right Command and right Option. Both inner Return thumbs share the space bar.">
</picture>

| Target | Hardware |
| --- | --- |
| `beekeeb/piantor:eduarbo` | Raspberry Pi Pico (RP2040), one UF2 per half |
| `crkbd/rev1:eduarbo` | Pro Micro (AVR), OLED on, RGB Matrix off |

[`qmk.json`](qmk.json) lists both targets for `qmk userspace-compile`. Running the
**Build QMK firmware** workflow in GitHub Actions builds them and replaces the `latest`
release only when both compile.
