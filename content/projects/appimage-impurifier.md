# appimage-impurifier

Build native type-2 AppImages that launch Nix applications. Original code is MIT
licensed. Images use the unmodified upstream AppImage runtime and a SquashFS
payload; both FUSE mounting and native extract-and-run are supported.

```nix
let backend = inputs.appimage-impurifier.lib.appimage-impurifier { inherit pkgs; };
in backend.makePackage { pkg = pkgs.ripgrep; }
```

`makePackage` returns `net` and `offline` image files. Copy the selected file to a
user-owned location, make it executable, and launch it normally. Nix-backed images require host `python3` and a working Nix store. They can use
a compatible external `nix-store` or an explicitly bundled static client. Native Nix provisioning is
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

## Native AppDirs and bundled clients

`makeNativeImage { name; appDir; }` wraps a producer-prepared AppDir with an
executable `AppRun`. It adds no Nix/Python launcher, database or daemon requirement.
Supply desktop metadata and icons in the AppDir if desktop integration is wanted.
The producer prepares a working target layout; this does not relocate binaries.
A separate VM executes both real FUSE and extract-and-run inside a root with
neither `/nix` nor Python, replaces the image and removes it.

Nix-backed `makeImage` and its flavor constructors accept `bundledNixStore` and
`bundledNixNotices`. Supply a static ELF client and its upstream notices. A
compatible external client takes precedence; explicit `IMPURIFIER_NIX_STORE`
disables fallback. Client selection happens before mutation, and failures are
never retried through another client or store. The bundled-client VM runs the
full lifecycle suite with no external Nix on the application user's PATH.

Root preparation continues to use trusted helper tools and never executes a
client from the user-owned image. Bundling a client is not a Nix installer.
