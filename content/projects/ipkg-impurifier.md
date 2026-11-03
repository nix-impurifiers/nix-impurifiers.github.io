# ipkg-impurifier

Emit native IPK packages that project Nix application closures into a shared,
GC-rooted `/opt/nix/profile`. IPK/ipkg is a separate contract from Alpine APK.
Original emitter/runtime code is MIT licensed. The archived native client is
GPL-2.0-or-later; see `THIRD_PARTY.md`. This is a historical compatibility target.

```nix
let impurifier = inputs.ipkg-impurifier.lib.ipkg-impurifier { inherit pkgs; };
in impurifier.makePackage { pkg = pkgs.hello; }
```

`makePackage` returns `net` and `offline`. Individual constructors are `makeIpk`,
`makeNetIpk`, and `makeOfflineIpk`. Both flavors have the same native package
identity and version. Select transport explicitly when installing local files:

```sh
sudo ipkg --force-defaults --force-reinstall install ./hello-offline.ipk
sudo ipkg --force-defaults --force-reinstall install ./hello-net.ipk
sudo ipkg remove hello
```

Export the two Nix artifacts under distinct local filenames. A repository needs
separate flavor channels or distinct releases; two artifacts cannot occupy one
native repository filename. Net packages use administrator-configured Nix
caches. Offline packages carry the full closure cache, select only that cache,
and disable remote builders during import. Neither changes global cache trust.

`makeRuntimeIpk { nixDependency = "nix"; pythonDependency = "python3"; }` makes
native runtime requirements consumer policy. The runtime requires working Nix
and Python; the impure Nix provider/installer remains deferred, not excluded.
The runtime archive contains the engine's MIT license notice.

`configFiles`, `files`, `users`, `directories`, `systemd`, `openrc`, `lifecycle`,
and `hardware` use the shared core API. Configurations belong to native ipkg
conffile handling on upgrades. Native `remove` purges configuration, including
edited files. Back up configurations before removal. Use ordinary `ipkg install`
for version upgrades; reserve `--force-reinstall` for same-version transport
switches, because the historical client bypasses normal upgrade bookkeeping
with that flag. Service host dependencies default to `[ "systemd" ]`; consumers
using OpenRC select its native dependencies. This does not claim OpenWrt procd
or every embedded image's supervisor has been implemented.

## Native transaction behavior

Application post-install scripts enqueue one callback in `IPKG_INTERCEPT_DIR`
when ipkg is configuring a transaction. Without that context the helper runs
reconciliation immediately. Removal reconciles per package; ipkg does not expose
the same transaction-wide removal/file-trigger contract as dpkg or RPM.

The historical ipkg client discards deferred intercept-script exit statuses. A native command
can succeed while profile activation failed. The engine prints diagnostics and
preserves the old profile on fetch/composition failure. After correcting cache
availability or installing an offline artifact, run:

```sh
sudo /usr/sbin/nix-profile-engine reconcile
sudo /usr/sbin/nix-profile-engine status
sudo /usr/sbin/nix-profile-engine prune --keep 2
```

Service/lifecycle failure may occur after publication and retains retry state.
Hooks must be idempotent. Native offline-root installations skip maintainer scripts. The helper also
rejects IPKG_OFFLINE_ROOT and non-root PKG_ROOT contexts. Image-time activation belongs
to the separate image adapter.

There is no claim of automatic library-directory triggers in ipkg. Native driver
packages can call `/usr/sbin/ipkg-impurifier-activate` after changing selected
libraries; it uses the same configuration batching. Otherwise explicitly
reconcile after an upstream driver upgrade. Snapshots retain old user-space
libraries but cannot establish GPU ABI or kernel-module compatibility.

## Verification

`nix flake check -L` runs engine contracts, native archive/dependency metadata and
reference-free closure checks, and a QEMU VM using actual ipkg/Nix/systemd. The
network-disabled VM checks fetch failure, offline reinstall, edited conffiles,
upgrades, native install batching, lifecycle hooks, account/directory ownership,
administrator service intent, removal, cooperating driver upgrades and GC.
It uses NixOS with mutable native-style unit directories, not an OpenWrt or
complete OpenEmbedded boot. This independently tests ipkg 0.99.163, not its maintained opkg successor.
The native client uses `/var/lib/ipkg` in this fixture (configure-time policy).

The exported `runtimeVersion` follows the pinned core source timestamp. Application dependencies require that runtime version or newer, rather than accepting every engine as `0.1.0`. This supports ordinary native engine upgrades without project release tags. Consumer-provided Nix dependency expressions remain independent of the engine's own native version.

## Native payloads and optional bundled clients

`makeNativeIpk { name; version; payload; architecture?; dependencies?; ... }`
packages a producer-prepared filesystem tree directly. It adds no engine hooks,
Nix dependency, daemon or database. The producer must prepare a working target
layout; this does not relocate binaries. The native target-root VM installs,
executes, upgrades and removes a static payload with no `/nix` directory.

`makeRuntimeIpk` also accepts `bundledNixStore` and `bundledNixNotices`. Supply
a static ELF client and its upstream notices. Bundling omits the default native
Nix dependency; Python remains required. A compatible external client takes
precedence, otherwise the bundled client is selected before mutation. Explicit
`IMPURIFIER_NIX_STORE` disables fallback; failed mutations are never retried with
another client. The bundled-client check repeats the full existing native VM
suite with an incompatible external candidate. This is not a Nix installer.
