# Eduardo's QMK userspace

Shared QMK configuration for Eduardo's Piantor and Corne keyboards. The keymaps
use the same layer definitions and chord behavior so the two boards stay in
sync with the internal-keyboard mapping in
[Karabiner-Elements](https://github.com/eduarbo/dotfiles/tree/main/macos/karabiner).

The complete layout, behavior contract, setup, and flashing instructions live
in [the userspace documentation](users/eduarbo/README.md).

## CI build targets

- `beekeeb/piantor:eduarbo`
- `crkbd/rev1:eduarbo`

`qmk.json` is the authoritative build matrix, and `qmk userspace-compile`
compiles both targets. The included GitHub Actions workflow uses the same matrix
on pushes after workflows have been enabled for this fork. A successful build
verifies that the shared userspace compiles for both boards; flashing and a
physical key test are still required before treating a behavior change as
hardware-verified.
The AVR-based Corne keeps its OLED animations but disables RGB Matrix to stay
within its firmware size limit; its build has little spare flash and must remain
in the build matrix for every change.

## Local build

After installing QMK and configuring this checkout as the userspace overlay:

```sh
qmk config user.overlay_dir="$(realpath .)"
qmk userspace-compile
```

The userspace guide also covers building without a global `qmk` install.

Piantor split UF2 images can be built explicitly with the commands documented
in [the userspace guide](users/eduarbo/README.md#how-to-build-and-flash).
