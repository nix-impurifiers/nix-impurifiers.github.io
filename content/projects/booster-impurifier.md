# booster-impurifier

Build native Booster initramfs images containing Nix-built closures. MIT licensed.

```nix
let
  backend = import (inputs.booster-impurifier + "/nix") {
    inherit pkgs;
    coreSrc = inputs.impurifier;
  };
in backend.makeImage {
  pkg = earlyTool;
  kernel = pkgs.linuxPackages.kernel;
  extraFiles = [];
  config = { compression = "gzip"; };
}
```

The upstream generator receives every store object in the package's closure
through its `extra_files` configuration. Absolute paths remain unchanged and
need no Nix database, daemon or client at boot. `extraFiles` adds prepared
absolute paths; their own non-Nix dependencies remain the producer's concern.
`kernel` must provide `modules` and `modDirVersion`. Native Booster configuration
passes through `config`, except closure files and stripping are controlled by
the backend. Builds use universal mode, with explicit kernel/module selection;
host-only discovery is unavailable in a pure build.

The SDK builds upstream init statically and leaves its runtime implementation
unchanged. Small generator patches disable host module/modprobe discovery and
skip `/usr/lib` dependency rescanning for complete Nix store closures. No files
are relocated. Booster does not expose dracut-style runtime hooks; inclusion
makes early tools available to Booster's native facilities and rescue shell.
It does not automatically execute arbitrary payloads or manage the real root.

`nix flake check -L` builds two revisions with the native generator and boots
upstream Booster `/init` in QEMU. Its native emergency shell executes each
embedded tool without a root disk, shared store or Nix database. The fixture
adds static BusyBox at Booster's documented rescue path; it does not replace
init. This verifies early tool availability, not every storage/root layout.
