# initramfs-tools-impurifier

Embed Nix-built closures using native initramfs-tools build hooks and boot scripts.
Original code is MIT licensed. Upstream initramfs-tools retains its GPL license.

```nix
let
  backend = import (inputs.initramfs-tools-impurifier + "/nix") {
    inherit pkgs;
    coreSrc = inputs.impurifier;
  };
in backend.makeHook {
  pkg = earlyTool;
  name = "early-tool";
  scripts = [{ stage = "init-top"; script = earlyHook; }];
}
```

Install the result's `etc/` and `usr/` trees into a producer host, then run that
host's `update-initramfs` or `mkinitramfs`. The generated build hook copies the
complete closure from its staged payload. Scripts execute at native init-top,
init-premount, local-top, local-premount, local-bottom or init-bottom stages.
Hook names must be unique. Stage ordering and prerequisites remain native
initramfs-tools concerns. Removing the hook package requires regenerating the
initramfs to remove its embedded payload.

Store paths are preserved; the image needs no Nix daemon, database or client.
The payload must be suitable for the target kernel and architecture. This does
not install a kernel, select modules, configure the real root or manage a host.
`package` exposes the pinned upstream builder scripts as a test SDK; it is not
a replacement for the host's distro integration or its optional hook packages.

`nix flake check -L` builds two revisions with upstream mkinitramfs inside a
producer VM, then boots both generated images in QEMU with upstream `/init`,
no root disk and no shared host store. Native init-top scripts execute the
Nix-built payload and verify there is no Nix database or mounted real root.
