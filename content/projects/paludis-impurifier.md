# paludis-impurifier

Emit PMS EAPI 6 overlays that transport Nix applications through actual Paludis
`cave` transactions. Paludis owns native files; the shared
[impurifier engine](https://github.com/nix-impurifiers/impurifier) realizes and
roots closures, then atomically publishes `/opt/nix/profile`. Original code is
MIT. Application licenses and GPL-covered native tooling remain independent.

```nix
let
  impurifier = inputs.paludis-impurifier.lib.paludis-impurifier {inherit pkgs;};
in impurifier.makeOverlay {
  packages = [
    impurifier.runtimeOverlay
    (impurifier.makeOfflineEbuild {pkg=pkgs.hello;})
  ];
}
```

Register the overlay in a persistent Portage-compatible configuration (`PORTDIR`
or `PORTDIR_OVERLAY`). The adapter uses Paludis's supported `portage` environment;
it does not invoke emerge. Run `paludis-impurifier resolve --execute
--preserve-world sys-apps/paludis-impurifier app-misc/hello-offline`. The flake's
`adapter` output bootstraps the same command before the runtime is installed.
Native Nix and Python must already be available. `makeRuntimeOverlay` accepts
`nixDependency` and `pythonDependency`; a Nix provider/installer is deferred.

The pinned native client supports EAPI 6, so the emitter uses `DEPEND` and EAPI 6
phase rules. This is PMS overlay integration, not an exheres compiler. Paludis
warns that its Portage configuration compatibility mode has limitations; it does
not implement every modern emerge configuration feature. Use a compatible
profile. The VM uses an explicit minimal profile with ARCH, USERLAND, KERNEL,
CHOST and CONFIG_PROTECT, rather than assuming current Gentoo profile directories
are accepted by this client.

`makeNetEbuild`, `makeOfflineEbuild` and `makePackage` accept the shared payload
arguments. `makePackage` returns `net` and `offline` overlays. Flavors have distinct
names and native blockers. This native resolver rejects a conflicting installed
flavor: explicitly remove it with `paludis-impurifier resolve --execute
--preserve-world !app-misc/hello-net` before installing `hello-offline`. Those are
two transactions with an availability gap. Edited configurations survive native
removal and subsequent install. Ordinary updates use CONFIG_PROTECT.

Native `hostDependencies`, `category`, `license` and `licenseFiles` are configurable.
Application license metadata defaults to SPDX identifiers; custom native license
names need matching files. Incompatible upstream versions need a PMS `version`
override. `buildEbuild` emits lower-level payloads and defaults to no activation;
`makeOverlay` merges versions and manifests while rejecting collisions.

The adapter waits for native cave, reconciles after executed transactions even
when the native command failed, and preserves either failure status. Without
`--execute` it remains read-only. Phase hooks defer only while a live adapter is
an ancestor; direct cave commands activate per package. Foreign environment/root
selection is rejected by the wrapper; phases independently reject foreign EROOT.
There is no assumption that Paludis runs Portage's post_emerge hook. Use the
adapter or explicitly reconcile after unrelated native driver changes.

OpenRC and shadow tools are the default service/account protocol. Explicit
systemd and runit declarations select those protocols. Users, directories,
lifecycle retries, service admin intent and declared host-library snapshots use
the shared engine. Failed realization retains the old profile. Lifecycle hooks
must be idempotent; retry `nix-profile-engine reconcile` after repairing failures.

`nix flake check -L` uses QEMU, the real pinned cave client, and real Gentoo OpenRC
userspace. Tests cover native solving/blockers, configuration ownership,
transaction batching, lifecycle retries, accounts/directories, service intent,
direct phase activation, foreign-root guards, native driver dependencies and GC.
The fixture disables the optional Paludis sandbox via its documented environment
switch. The outer kernel is NixOS and Nix is preinstalled. This is not an Exherbo
boot, binary-Paludis-package or Nix-installer claim. Upstream marks its optional
PBINS implementation nonfunctional; this fixture leaves that feature disabled.

## Native payloads and bundled clients

`makeNativeEbuild { name; version; payload; license; dependencies?; ... }` emits
a native EAPI 6 overlay from a producer-prepared tree. It disables engine
activation and adds no Nix requirement. The producer supplies a working target
layout; this does not relocate binaries. The native cave VM installs, executes,
upgrades and removes a static payload in an independent root without `/nix`.
That root retains the ordinary native package database, world file and `/etc`
foundation used by Paludis's post-merge tools.

`makeRuntimeOverlay` optionally accepts `bundledNixStore` and
`bundledNixNotices`. Supply a static ELF client with upstream notices. Bundling
omits the default Nix dependency; Python remains required. Compatible external
clients take precedence, explicit `IMPURIFIER_NIX_STORE` disables fallback, and
failed mutations are never retried through another client. A separate bundled
VM repeats the original cave lifecycle suite with an incompatible external
candidate. Nix provisioning remains deferred.
