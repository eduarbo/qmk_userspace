# Eduardo's split-keyboard layout

Shared 36-key layout for the Piantor and the 3x5 Corne (CRKBD). The layer and
chord behavior intentionally tracks the
[Karabiner-Elements version](https://github.com/eduarbo/dotfiles/tree/main/macos/karabiner)
used on the MacBook keyboard.

## Supported targets

- `beekeeb/piantor:eduarbo`
- `crkbd/rev1:eduarbo`

Both targets use the same userspace code and are listed in `qmk.json`.
`qmk userspace-compile` checks both locally; the included GitHub Actions workflow
does the same on pushes after workflows have been enabled for this fork.

The AVR-based CRKBD keeps its OLED and custom animations. RGB Matrix is
explicitly disabled in its keymap to fit the firmware size limit. The verified
build uses about 97% of available flash, so every userspace change must compile
both targets before it is accepted.

## How to build and flash

### Prerequisites on macOS

```sh
brew install qmk/qmk/qmk
brew install arm-none-eabi-gcc arm-none-eabi-binutils
qmk setup -H ~/dev/eduarbo/qmk_firmware
qmk config user.overlay_dir="$(realpath .)"
```

Run the overlay command from the root of this userspace checkout.

Without a global `qmk` install, run the CLI through `uv` with the QMK toolchains
checkout on the `PATH`, from the root of this userspace checkout:

```sh
export PATH="$HOME/dev/eduarbo/qmk_toolchains/bin:$PATH" QMK_HOME=~/dev/eduarbo/qmk_firmware
uvx --from qmk==1.2.0 qmk userspace-compile
```

Prefix any `qmk` command below with `uvx --from qmk==1.2.0` the same way.

### Build every configured target

```sh
qmk userspace-compile
```

### Piantor split UF2 images

Run the command for each half, then put that half in bootloader mode; the CLI
waits for the `RPI-RP2` drive and copies the image with its handedness:

```sh
qmk flash -kb beekeeb/piantor -km eduarbo -bl uf2-split-left
qmk flash -kb beekeeb/piantor -km eduarbo -bl uf2-split-right
```

### Corne (CRKBD rev1)

```sh
qmk compile -kb crkbd/rev1 -km eduarbo
```

Both boards use `EE_HANDS`, so each half stores its side in EEPROM. Flash each
Corne half with its handedness target:

```sh
qmk flash -kb crkbd/rev1 -km eduarbo -bl avrdude-split-left
qmk flash -kb crkbd/rev1 -km eduarbo -bl avrdude-split-right
```

## Behavior contract

The following chords are shared with the Karabiner layout unless a difference
is called out explicitly:

| Chord | Tap/result | Hold/release behavior |
| --- | --- | --- |
| `Symbols+A` | macOS: `Option+E`; Winux: `Right Alt+E` | `A` is Shift while held, without leaving Symbols |
| `Symbols+;` | macOS: `Option+N`; Winux: `Right Alt+N` | `;` is Shift while held, without leaving Symbols |
| `Symbols+Space` | `Left Shift+Space` | Space remains Left Shift while held |
| `Right Command+Space` (macOS) | `Shift+Return` | Holding a Return thumb and tapping Space gives the same result as the opposite order, without leaving Right Command latched. Karabiner maps Space hold + Left Command tap the same way |
| `Symbols+Return` | macOS: `Left Command+Return`; Winux: `Left Control+Return` | Return remains Right Command or Right Control while held |
| `Symbols+Shift+Return` | macOS: `Left Command+Return`; Winux: `Left Control+Return` | Same tap result as `Symbols+Return`; Shift is removed only for the emitted chord and then restored |
| `Symbols+Super` or `Super+Symbols` | Hyper (`Right Shift+Command+Option+Control`, as in Karabiner) | Momentary in both press orders; releasing either key restores only the key still held |
| `Super+Space` | `F16` | With Super pressed first, holding Space enters F-Keys; either release order restores Super or the right Fn modifier correctly |

`Symbols+Z` uses QMK's native Caps Word, while Karabiner emits Caps Lock there
because it has no native Caps Word state machine. The userspace narrows the gap:
letters are shifted, while digits, `-`, `'`, `;`, `` ` ``, Backspace and Delete
continue Caps Word unshifted, as they would with Caps Lock.

Caps Word is the only deliberate QMK/Karabiner difference. Both sides use a
250 ms tap window (`TAPPING_TERM` here, `to_if_alone_timeout` in Karabiner). Running
`npm test` in `dotfiles/macos/karabiner` compares the base, Symbols and F-Keys layers
in `wrappers.h` with Karabiner, so run it after changing either side.

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

The keyboard always boots into the macOS base. `TG_BASE` on Adjust switches
between macOS and Winux for the current session only; unplugging and
reconnecting the keyboard restores macOS. QMK OS detection stays disabled because
USB hubs made it report macOS as Windows.

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
╭───┬───┬───┬───┬───╮       ╭───┬───┬───┬───┬───╮
│⇧⌘3│MIC│⌥⌘I│⇧⌘C│⌘\ │       │SND│1PW│GPT│CLP│   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│⇧⌘4│⇧⌃⇥│⌘[ │⌘] │⌃⇥ │       │W←½│WNS│WTM│W→½│WGR│
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│⇧⌘5│⌃↓ │⌘` │⌘⇥ │⌃↑ │       │   │EMJ│SNP│UAC│   │
╰───┴───┴───┴───┴───╯       ╰───┴───┴───┴───┴───╯
```

QMK emits `E`, `R`, `T`, `S`, `D`, `F` and `G` itself; the developer and
navigation shortcuts use their Control equivalents on the Winux base. `Q`, `A`,
`Z`, `X`, `C`, `V` and `B` are remapped by Karabiner's SUPER layer, which applies
to external keyboards on purpose. `MIC` and the right-hand bindings are app
hotkeys on `Super+key`. Without Karabiner (for example on a Winux host), those
keys reach the host as plain `Super+key`.

## F-Keys

```text
╭───┬───┬───┬───┬───╮       ╭────┬────┬────┬────┬───╮
│F12│F7 │F8 │F9 │PRT│       │ V+ │ RW │PLAY│ FF │PRT│
├───┼───┼───┼───┼───┤       ├────┼────┼────┼────┼───┤
│F11│F4 │F5 │F6 │LCK│       │ V- │ V- │MUTE│ V+ │LCK│
├───┼───┼───┼───┼───┤       ├────┼────┼────┼────┼───┤
│F10│F1 │F2 │F3 │PAU│       │MUTE│ B- │ B+ │MCTL│PAU│
╰───┴───┴───┴───┴───╯       ╰────┴────┴────┴────┴───╯
```

F-Keys matches the Karabiner FN layer key for key. Reach it by holding Super and
then Space, or Super and the right Fn thumb.

## Adjust and Gamepad

Hold Super and a Return thumb, in either order, to reach Adjust. In Gamepad, hold
Left Alt and the right Return thumb instead.

```text
╭───┬───┬───┬───┬───╮       ╭───┬────┬────┬───┬───╮
│   │DBG│RBT│EEC│BOT│       │   │    │    │   │   │
├───┼───┼───┼───┼───┤       ├───┼────┼────┼───┼───┤
│   │   │   │   │   │       │   │GAME│BASE│   │   │
├───┼───┼───┼───┼───┤       ├───┼────┼────┼───┼───┤
│   │   │   │   │   │       │   │    │    │   │   │
╰───┴───┴───┴───┴───╯       ╰───┴────┴────┴───┴───╯
```

`DBG` toggles debug, `RBT` reboots, `EEC` clears EEPROM and `BOT` enters the
bootloader. Lighting controls fill the empty left keys only on builds with RGB
Matrix or RGB Light enabled; neither current target enables them. `BASE` is the
session-only macOS/Winux toggle described above, and `GAME` toggles Gamepad, a
right-shifted QWERTY layer for FPS controls. Both toggles live on Adjust instead
of F-Keys so that volume and brightness keys cannot change the layout.

## Physical verification checklist

After flashing, test on both the macOS and Winux bases:

1. Tap and hold both accent keys; confirm the tap emits the expected dead key
   and the hold shifts a following Symbols-layer key.
2. Test tap and hold for `Symbols+Space` and `Symbols+Return` on both bases, plus
   `Right Command+Space` on macOS and `Symbols+Shift+Return`. Release Symbols
   and each thumb in both orders; verify the exact tap result, rollover behavior,
   restored one-shot modifiers, and that no modifier remains latched.
3. Enter Hyper in both press orders, then release Symbols first and Super first;
   the remaining key must keep only its own behavior.
4. With Super pressed first, tap and hold Space. Release Space first once and
   Super first once; no modifier or layer may remain latched.
5. Toggle Caps Word with `Symbols+Z`, type letters, digits, `-`, underscore,
   and a terminating key; `-` must stay a hyphen.
6. On F-Keys, confirm `J`/`K`/`L` send Volume Down, Mute and Volume Up.
7. Toggle `BASE` on Adjust, confirm the Winux base is active, then unplug and
   reconnect the keyboard: the macOS base must be active again.
