# Eduardo's split-keyboard layout

Shared 36-key layout for the Piantor and the 3x5 Corne (CRKBD). The layer and
chord behavior intentionally tracks the
[Karabiner-Elements version](https://github.com/eduarbo/dotfiles/tree/main/macos/karabiner)
used on the MacBook keyboard.

## Supported targets

- `beekeeb/piantor:eduarbo`
- `crkbd/rev1:eduarbo`

Both targets use the same userspace code and are listed in `qmk.json`, so the
GitHub Actions build checks both on every push.

## How to build and flash

### Prerequisites on macOS

```sh
brew install qmk/qmk/qmk
brew install arm-none-eabi-gcc arm-none-eabi-binutils
qmk setup -H ~/dev/eduarbo/qmk_firmware
qmk config user.overlay_dir="$(realpath .)"
```

Run the overlay command from the root of this userspace checkout.

### Build every configured target

```sh
qmk userspace-compile
```

### Piantor split UF2 images

Put the appropriate half in bootloader mode, then build the matching image:

```sh
qmk compile -kb beekeeb/piantor -km eduarbo -t uf2-split-right
qmk compile -kb beekeeb/piantor -km eduarbo -t uf2-split-left
```

### Corne (CRKBD rev1)

```sh
qmk compile -kb crkbd/rev1 -km eduarbo
```

## Behavior contract

The following chords are shared with the Karabiner layout unless a difference
is called out explicitly:

| Chord | Tap/result | Hold/release behavior |
| --- | --- | --- |
| `Symbols+A` | macOS: `Option+E`; Winux: `Right Alt+E` | `A` is Shift while held, without leaving Symbols |
| `Symbols+;` | macOS: `Option+N`; Winux: `Right Alt+N` | `;` is Shift while held, without leaving Symbols |
| `Symbols+Return` | `Shift+Return` | Existing Symbols behavior is preserved |
| `Symbols+Shift+Return` | macOS: `Command+Return`; Winux: `Control+Return` | Shift is removed only for the emitted chord and then restored |
| `Symbols+Super` or `Super+Symbols` | Hyper (`Shift+Command+Option+Control`) | Momentary in both press orders; releasing either key restores only the key still held |
| `Super+Space` | `F16` | With Super pressed first, holding Space enters F-Keys; either release order restores Super or the right Fn modifier correctly |

`Symbols+Z` uses QMK's native Caps Word. This is the one deliberate runtime
difference: Karabiner emits Caps Lock there because it has no native Caps Word
state machine.

Super plus a right thumb key can still emit the corresponding one-shot modifier
on tap. That QMK convenience is separate from Hyper: the Hyper chord itself is
strictly momentary and never leaves Symbols or Shift latched.

## Symbols

The accent keys are Shift mod-taps: tap for the dead key, hold for Shift.

```text
╭─────┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬─────╮
│  ▲  │ 7 │ 8 │ 9 │ 0 │       │ \ │ [ │ ] │ / │  ▼  │
├─────┼───┼───┼───┼───┤       ├───┼───┼───┼───┼─────┤
│ ´/⇧ │ 4 │ 5 │ 6 │ = │       │ ← │ ↓ │ ↑ │ → │ ~/⇧ │
├─────┼───┼───┼───┼───┤       ├───┼───┼───┼───┼─────┤
│ CW  │ 1 │ 2 │ 3 │ - │       │ ` │ ' │   │   │     │
╰─────┴───┴───┴───┴───╯       ╰───┴───┴───┴───┴─────╯
```

`▲`/`▼` are Page Up/Page Down; holding Shift changes them to Home/End.

## Base layers

The base is selected persistently with `TG_BASE` on Adjust. It is not detected
from the operating system at boot.

### macOS base

```text
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│ Q │ W │ E │ R │ T │       │ Y │ U │ I │ O │ P │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ A │ S │ D │ F │ G │       │ H │ J │ K │ L │ ; │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│ Z │ X │ C │ V │ B │       │ N │ M │ , │ . │ ⌫ │
╰───┴───┴──┬┴──┬┴──┬┴──╮ ╭──┴┬──┴┬──┴┬──┴───┴───╯
           │ ⎋ │ ␣ │ ⏎ │ │ ⏎ │ ⇥ │F16│ ← tap
           │ ≡ │ ⇧ │ ⌘ │ │ ⌘ │ ⇪ │ ⌃ │ ← hold
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

### Winux base

Winux uses Control where the macOS base uses Command. Its right Fn thumb is
`F16` on tap and Right GUI on hold; the Return thumbs hold Right Control.

```text
           ╭───┬───┬───╮ ╭───┬───┬───╮
           │ ⎋ │ ␣ │ ⏎ │ │ ⏎ │ ⇥ │F16│ ← tap
           │ ≡ │ ⇧ │ ⌃ │ │ ⌃ │ ⇪ │ ⌘ │ ← hold
           ╰───┴───┴───╯ ╰───┴───┴───╯
```

## Super

Super is `Command+Option+Control` and provides one-handed browser/developer
shortcuts. Holding it with Symbols produces Hyper in either press order.

```text
╭───┬───┬───┬───┬───╮
│   │   │⌥⌘I│⇧⌘C│⌘\ │
├───┼───┼───┼───┼───┤
│   │⇧⌃⇥│⌘[ │⌘] │⌃⇥ │
├───┼───┼───┼───┼───┤
│   │   │   │   │   │
╰───┴───┴───┴───┴───╯
```

The developer and navigation shortcuts use their Control equivalents on the
Winux base.

## F-Keys

```text
╭───┬───┬───┬───┬───╮       ╭────┬────┬────┬────┬───╮
│F12│F7 │F8 │F9 │PRT│       │ V+ │ RW │PLAY│ FF │PRT│
├───┼───┼───┼───┼───┤       ├────┼────┼────┼────┼───┤
│F11│F4 │F5 │F6 │LCK│       │ V- │GAME│BASE│LPAD│LCK│
├───┼───┼───┼───┼───┤       ├────┼────┼────┼────┼───┤
│F10│F1 │F2 │F3 │PAU│       │MUTE│ B- │ B+ │MCTL│PAU│
╰───┴───┴───┴───┴───╯       ╰────┴────┴────┴────┴───╯
```

## Adjust and Gamepad

Adjust contains firmware controls (debug, reboot, EEPROM clear, bootloader) and
lighting controls when enabled. The F-Keys layer contains the persistent base
toggle and the Gamepad toggle. Gamepad is a right-shifted QWERTY layer for FPS
controls.

## Physical verification checklist

After flashing, test on both the macOS and Winux bases:

1. Tap and hold both accent keys; confirm the tap emits the expected dead key
   and the hold shifts a following Symbols-layer key.
2. Test `Symbols+Return` and `Symbols+Shift+Return`.
3. Enter Hyper in both press orders, then release Symbols first and Super first;
   the remaining key must keep only its own behavior.
4. With Super pressed first, tap and hold Space. Release Space first once and
   Super first once; no modifier or layer may remain latched.
5. Toggle Caps Word with `Symbols+Z`, type letters, digits, underscore, and a
   terminating key.
