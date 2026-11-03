# appimage-impurifier

Build native type-2 AppImages that launch Nix applications. Original code is MIT
licensed. Images use the unmodified upstream AppImage runtime and a SquashFS
payload; both FUSE mounting and native extract-and-run are supported.

```nix
let backend = inputs.appimage-impurifier.lib.appimage-impurifier { inherit pkgs; };
in backend.makePackage { pkg = pkgs.ripgrep; }
```

`makePackage` returns `net` and `offline` image files. Copy the selected file to a
user-owned location, make it executable, and launch it normally. The host must
provide working `python3` and `nix-store` commands. Native Nix provisioning is
explicitly deferred; this project does not install or configure the Nix daemon.

`makeImage`, `makeNetImage`, and `makeOfflineImage` accept `pkg`, optional
`program` (defaulting to `meta.mainProgram` or `pname`), `terminal` (default true),
and optional `hardware` using the shared host-library capture contract. Desktop
metadata and an icon are included for AppImageLauncher integration. `buildImage`
is the lower-level emitter for an existing AppDir payload.

Network images use the host's configured Nix providers. Offline images carry a
file binary cache. A normal user cannot override a daemon's signature policy.
With the trusted helper installed, explicitly prepare an offline image:

```
sudo appimage-impurifier prepare /home/user/Applications/example.AppImage
```

The helper reads the native image with trusted runtime/SquashFS tools, imports its
closure, and registers a lasting root as the image owner. It never executes the
supplied AppImage or application code as root. A failed launch may be retried.
Preparation uses the owner's default state directory; custom `XDG_STATE_HOME`
locations require the application to establish its own root on its first launch.

Application and captured-library roots live under
`$XDG_STATE_HOME/appimage-impurifier` (default `~/.local/state`). They are associated
with the image's absolute path and full SHA-256 content digest. The launcher hashes
the image each time; large images therefore incur an extra sequential read.
Launching after moving or replacing an image establishes roots for the new file.
After deleting, moving, or replacing images, run this as the application user:

```
appimage-impurifier prune
```

Pruning releases roots whose image is missing or has different content. AppImage
has no native uninstall hooks, so deletion alone does not release these roots.
The image stays unchanged through preparation and launch. Host-library snapshots
refresh at each launch and remain rooted until their owning image is pruned.

This backend does not activate a global profile, services, or host accounts.
See [development notes](docs/development/index.md) for native verification.
