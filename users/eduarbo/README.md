# Eduarbo's Split Keyboard Userspace

This userspace is tailored for my split keyboards, optimizing them particularly for coding. It's designed for keyboards such as the 36-key Piantor and the 42-key CRKBD equipped with an OLED display. By prioritizing simplicity and functionality, I've aimed to provide a consistent keymapping experience across all my keyboards. This ensures a seamless transition between different keyboards and keeps all essential coding keys within easy reach.

I've incorporated a lot of OLED display code from various contributors to the QMK community.

## How to flash

Before flashing, ensure your keyboard is in bootloader mode.

### Piantor

To flash the right split, use the command:

    make beekeeb/piantor:eduarbo:uf2-split-right

For the left split, use:

    make beekeeb/piantor:eduarbo:uf2-split-left

### Corne Keyboard (CRKBD):

    make crkbd:eduarbo

## Features

- Dynamic Base Layer: Adapts the base layer based on the detected OS at boot
- Auto Hand Detection: Determines handiness by the USB-connected half
- OLED Animations: Features captivating [Ocean Dream](../snowe/readme_ocean_dream.md) and Bongocat displays
- RGB Underglow: Dynamic RGB lighting underglow effects
- Caps Word: Prevent unintentional CAPS LOCK activations for uninterrupted typing

## Keymaps

- [Crkdb/eduarbo](../../keyboards/crkbd/keymaps/eduarbo/keymap.c)
- [Piantor/eduarbo](../../keyboards/beekeeb/piantor/keymaps/eduarbo/keymap.c)

## Macbook Internal Keyboard Support

Because I occasionally have to use the Macbook's built-in keyboard, I've ported most of the features from this userspace using Karabiner Elements. This ensures a consistent keymapping experience, whether I'm using an external keyboard or the Macbook's internal one.

## TODO
- [ ] Reimplement [Bongocat](../../keyboards/adpenrose/akemipad/keymaps/oled_bongocat/readme.md)

## Layouts

### Adjust

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│TGL│DBG│RBT│EEC│BOT│       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│   │HUI│SAI│VAI│SPI│       │   │WIN│GAM│   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│MOD│HUD│SAD│VAD│SPD│       │   │   │   │   │   │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │▐█▌│   │   │ │▐█▌│   │   │
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

### Winux

Swaps Ctrl and Gui keys for non-Mac systems.

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│   │   │   │   │   │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│   │   │   │   │   │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│   │   │   │   │   │       │   │   │   │   │   │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │   │   │ ⏎ │ │ ⏎ │   │F13│ ← on tap
           │   │   │ ⌃ │ │ ⌃ │   │ ⌥ │ ← on hold
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

### Gaming

Right-shifted QWERTY for FPS games using ESDF as arrow keys

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│ESC│ W │ ↑ │ R │ T │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ a │ ← │ ↓ │ → │ G │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ z │ X │ C │ V │ B │       │   │   │   │   │   │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │ ⌥ │ ␣ │ ⌃ │ │   │   │   │
           ╰───┴───┴───╯ ╰───┴───┴───╯
```
