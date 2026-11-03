# homebrew-impurifier

Emit native Homebrew formulae and taps backed by Nix applications. Original code
is MIT licensed. Homebrew owns its Cellar, opt links, command links, receipts,
upgrades and cleanup; Nix owns the application closures. Linux is the tested target.

```nix
let backend = inputs.homebrew-impurifier.lib.homebrew-impurifier { inherit pkgs; };
in backend.makePackage { pkg = pkgs.ripgrep; }
```

`makePackage` returns `net` and `offline` formula outputs. Each contains `Formula`
and `archives` directories. Combine distinct applications with
`makeTap [ formula1 formula2 ]`, publish the result as an ordinary Git tap, then
use `brew tap` and `brew install` normally. Choose one transport for a formula
version. Use native `brew reinstall` to replace a version's transport.

`makeFormula`, `makeNetFormula` and `makeOfflineFormula` accept `pkg`, optional
`name`, `program` (defaulting to `meta.mainProgram` or `pname`), `archiveURL`,
`nixDependency`, `pythonDependency`, and optional `hardware` using the shared
host-library capture contract. Formula names use lowercase letters, numbers and
hyphens. For remote taps, set `archiveURL` to the published source archive URL.
Default local URLs require keeping the source output available until Homebrew
has downloaded it. The native client checks the archive SHA-256.

By default, native fatal requirements check host `nix-store >= 2.0` and
`python3 >= 3.8`. Set `nixDependency` and `pythonDependency` to actual Homebrew
formula names to declare package dependencies instead, including providers in
your own tap. Homebrew 7 requires explicit trust for provider dependencies from
non-official taps; use its normal `brew trust --formula user/tap/provider` command
for the provider formulae you select. The launcher uses those formulae's opt paths explicitly. Native
Nix provisioning and daemon installation are deferred, not excluded.

Network formulae realize through the host's configured Nix providers. Offline
formulae carry a file binary cache. An unprivileged user cannot bypass the Nix
daemon's signature policy. With the trusted helper installed, explicitly run:

```
sudo homebrew-impurifier prepare "$(brew --prefix your-formula)"
```

Preparation checks the native install receipt and package payload checksums,
imports the offline closure and registers its root as the keg owner. It never
executes formula or application code as root. Homebrew moves the original MIT
license notice to the keg root; it remains preserved there.

Activation occurs on launch or explicit preparation. A failed realization may be
retried. The lasting root lives inside the native keg, so unlinking a command
keeps an installed application's closure, while uninstall or cleanup of that keg
releases it. Native upgrades install a new version and manage the old keg through
Homebrew's own cleanup policy.

Host-library snapshots refresh on each launch and live in per-user state. After
removing or cleaning kegs, run `homebrew-impurifier prune` as the application user
to release snapshots belonging to missing implementations.

This backend does not activate a global profile, services, or accounts. See
[development notes](docs/development/index.md) for native verification and limits.

`makeNativeFormula { payload; name; version; dependencies ? []; archiveURL ? null; }`
accepts a producer-prepared prefix tree and emits an ordinary source formula.
Homebrew owns its files; the installed payload has no impurifier launcher, Nix
client, daemon, database or Python requirement. The producer is responsible for
ABI compatibility and prefix independence. This does not relocate store paths.

Nix-backed formulae optionally accept `bundledNixStore` (a static ELF `nix-store`)
and `bundledNixNotices`. They prefer a compatible external client, falling back
to the private bundled client before any operation. A failed operation is never
retried with another client. Python remains required. Root preparation continues
to use the administrator's trusted client. A bundled client does not install Nix
or grant write access to a store.
