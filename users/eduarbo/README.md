# Eduarbo's Split Keyboard Userspace

This userspace is tailored for my split keyboards, optimizing them particularly for coding. It's designed for keyboards such as the 36-key Piantor and the 42-key CRKBD equipped with an OLED display. By prioritizing simplicity and functionality, I've aimed to provide a consistent keymapping experience across all my keyboards. This ensures a seamless transition between different keyboards and keeps all essential coding keys within easy reach.

<!-- I've incorporated a lot of OLED display code from various contributors to the QMK community. -->

## Prerequisites (macOS)

1. Install QMK and its dependencies:

       brew install qmk/qmk/qmk

2. Install the ARM toolchain (required for RP2040-based boards like the Piantor):

       brew install arm-none-eabi-gcc arm-none-eabi-binutils

3. Run QMK setup and point to your firmware checkout:

       qmk setup -H ~/dev/eduarbo/qmk_firmware

4. Set the userspace overlay:

       qmk config user.overlay_dir="$(realpath .)"

## How to flash

Before flashing, ensure your keyboard is in bootloader mode and that you have properly set up QMK and this userspace.

### Piantor

To flash the right split, use the command:

    qmk compile -kb beekeeb/piantor -km eduarbo -t uf2-split-right

For the left split, use:

    qmk compile -kb beekeeb/piantor -km eduarbo -t uf2-split-left

<!-- ### Corne Keyboard (CRKBD) -->

## Features

- Dynamic Base Layer: Adapts the base layer based on the detected OS at boot
- Auto Hand Detection: Determines handiness by the USB-connected half
- Caps Word: Prevent unintentional CAPS LOCK activations for uninterrupted typing
<!-- - OLED Animations (CRKBD): Features captivating [Ocean Dream](../snowe/readme_ocean_dream.md) and Bongocat displays -->
<!-- - RGB Underglow (CRKBD): Dynamic RGB lighting underglow effects -->

## Keymaps

<!-- - [Crkdb/eduarbo](../../keyboards/crkbd/keymaps/eduarbo/keymap.c) -->
- [Piantor/eduarbo](../../keyboards/beekeeb/piantor/keymaps/eduarbo/keymap.c)

## My layout

This layout is built for my main keyboard, a 36-key Piantor, but since I sometimes need to use the MacBook's built-in keyboard, I’ve [replicated the layout with Karabiner Elements](https://github.com/eduarbo/dotfiles/blob/main/macos/karabiner/README.md#super). This way, I maintain a consistent keymapping experience whether I’m using the external keyboard or the MacBook’s internal one, as I don’t always have my mechanical keyboard with me 😞.

### Why this layout distribuition?

- Super Mod: Frequently used shortcuts. Placed on the left hand for ease of use with the mouse in the right hand.
- Shift: Positioned on the left to be used with modifiers on the opposite side and with the mouse.
- Symbols Layer: For all symbols that didn’t fit on the base layer. Positioned on the right to use the arrow keys (hjkl) with one hand.
- Command: Placed on both sides since, like the Shift key, it is often used with other modifiers. This placement maintains consistency with the integrated keyboard, where the spacebar can be used with any modifier on either side.
- Alt/Option: This modifier is less used in macOS, so I prioritized the Super key in the thumbs cluster.
- Space: Placed in the most accessible positions, such as the Shift or Symbols keys, which are the most used modifiers when typing.
- Enter: Positioned on both the left and right sides to facilitate copying, pasting, and pressing Enter while using the mouse. Keeping Enter on the left side prevents the need to move the right hand from the mouse to the keyboard.
- Sticky mods (CMD, CTRL, ALT): Available when holding the Super key for the rare occasions when I need to combine mods.
- Avoid placing Enter on the Shift or Symbols keys to prevent accidental presses while typing.

### Symbols chart

#### Modifiers

| Symbol | description | Symbol | description   | Symbol | description    |
|--------|-------------|--------|---------------|--------|----------------|
| `⌘`    | command     | `⌃`    | control       | `⇧`    | shift          |
| `⌥`    | option      | `≡`    | super (`⌘⌥⌃`) | `≢`    | hyper (`⇧⌘⌥⌃`) |

#### Layers

| Symbol | description | Symbol | description | Symbol | description  |
|--------|-------------|--------|-------------|--------|--------------|
| `⇪`    | symbols     | `ƒ`    | f-keys      | `⊕`    | adjust (QMK) |

#### Other Keys

| Symbol | Description | Symbol | Description | Symbol | Description |
|--------|-------------|--------|-------------|--------|-------------|
| `␣`    | Space       | `⌫`    | Backspace   | `⇧▲`   | Home        |
| `⇥`    | Tab         | `⌦`    | Delete      | `⇧▼`   | End         |
| `⏎`    | Enter       | `▼`    | Page Down   | `CW`   | Caps Word   |
| `⎋`    | Escape      | `▲`    | Page Up     |        |             |

### Base

Standard QWERTY layout, with the delete key replacing the slash key. Modifiers are set as mod-tap (acting as a modifier when held and a regular keycode when tapped). Central modifiers are treated as one, allowing the layout to be replicated on a MacBook keyboard by using the space key in place of the central modifiers.

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│ Q │ W │ E │ R │ T │       │ Y │ U │ I │ O │ P │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ A │ S │ D │ F │ G │       │ H │ J │ K │ L │ ; │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ Z │ X │ C │ V │ B │       │ N │ M │ , │ . │ ⌫ │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │ ⎋ │ ␣ │ ⏎ │ │ ⏎ │ ⇥ │F16│ ← on tap
           │ ≡ │ ⇧ │ ⌘ │ │ ⌘ │ ⇪ │ ⌃ │ ← on hold
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

### Symbols

Left-side numpad, right-side symbols and arrows, with `,`, `.`, and `⌫` retained for easy number typing.

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│ ▲ │ 7 │ 8 │ 9 │ 0 │       │ \ │ [ │ ] │ / │ ▼ │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ ´ │ 4 │ 5 │ 6 │ = │       │ ← │ ↓ │ ↑ │ → │ ~ │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│CW │ 1 │ 2 │ 3 │ - │       │ ` │ ' │   │   │   │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │⇧+⎋│⇧+␣│⇧+⏎│ │   │▐█▌│   │ ← on tap
           │ ≢ │   │   │ │   │▐█▌│   │ ← on hold
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

| Symbol | Description | Symbol      | Description | Symbol      | Description |
|--------|-------------|-------------|-------------|-------------|-------------|
| `F16`  | Raycast     | `⌘␣`        | Spotlight   | `⇧` + `F16` | Emojis      |

### Super

Left-hand shortcuts for one-handed use, perfect for when you're navigating with the mouse/trackpad or snacking on Cheetos.

Only a few keys are mapped, as the rest are handled by OS-level bindings using Karabiner-Elements. You can view the [complete list here](https://github.com/eduarbo/dotfiles/blob/main/macos/karabiner/README.md#super).

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│   │   │⌥⌘I│⇧⌘C│⌘\ │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│   │⇧⌃⇥│⌘[ │⌘] │⌃⇥ │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│   │   │   │   │   │       │   │   │   │   │   │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │▐█▌│   │   │ │ ⌘ │ ⌥ │ ⌃ │ ← on tap (sticky)
           │▐█▌│   │   │ │ ⊕ │ ≢ │ ƒ │ ← on hold
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

#### Left side

**Debugger**
- `⌥⌘I`: Toggle DevTools
- `⇧⌘C`: Inspect element
- `⌘\`: Pause/Resume script

**Browser navigation**
- `⇧⌃⇥` : Previous tab
- `⌘[` : Back
- `⌘]` : Forward
- `⌃⇥`: Next tab

### F-Keys

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│F12│F7 │F8 │F9 │PRT│       │F12│F7 │F8 │F9 │PRT│
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│F11│F4 │F5 │F6 │LCK│       │F11│F4 │F5 │F6 │LCK│
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│F10│F1 │F2 │F3 │PAU│       │F10│F1 │F2 │F3 │PAU│
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │▐█▌│ ⇧ │   │ │   │ ⇧ │▐█▌│
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

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
│ A │ ← │ ↓ │ → │ G │       │   │   │   │   │   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ Z │ X │ C │ V │ B │       │   │   │   │   │   │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │ ⇥ │ ␣ │ ⏎ │ │   │   │   │
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

## TODO
- [ ] Migrate config for my corne keyboard
<!-- - [ ] Reimplement [Bongocat](../../keyboards/adpenrose/akemipad/keymaps/oled_bongocat/readme.md) -->
