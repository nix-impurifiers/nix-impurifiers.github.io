# Autopackage impurifier

Native Autopackage 1.4.2 installers whose commands run Nix application closures.
Original adapter code is MIT. Upstream applications, the LGPL installer code
and bundled native tools retain their own licenses and notices.

```nix
let adapter = autopackageImpurifier.lib.autopackage-impurifier { inherit pkgs; };
in adapter.makePackage { pkg = myApplication; }
```

`makePackage` returns `net` and `offline`, each containing `application.package`.
`makeNetPackage` and `makeOfflinePackage` return one artifact. `makeArtifact`
also accepts `name`, `program`, `offline`, `hardware` and `revision`.
Names/programs must be safe command identifiers and versions must start with a
digit. The pinned native SDK currently supports x86_64 Linux.

`pkg` supplies `pname`, `version` and `bin/<program>`; `program` defaults to
`meta.mainProgram` or `pname`. Optional `hardware` accepts the shared impurifier
hardware manifest and captures selected real host libraries at launch.
The stable native interface name is `@nix-impurifiers.org/<name>:0`.
Software versions follow the application. Native package revisions default to
the newer backend/core source timestamp, with an offline transport increment;
set `revision` explicitly when managing release numbers yourself. This permits
backend updates without changing the application's own version.

Nix and its daemon must already be installed. Native Nix provisioning remains
deferred installer work. The optional flake output `native-client` supplies
the archived compiler and native `package` client; the default output supplies
`autopackage-impurifier` for preparation/pruning. Existing native Autopackage
installations may also consume emitted artifacts.

```sh
package install --ttyfe --user --prefix="$HOME/.local" ./application.package
sudo autopackage-impurifier prepare --owner "$USER" "$HOME/.local" my-application
"$HOME/.local/bin/my-application"
package files --user @nix-impurifiers.org/my-application:0
package verify --user @nix-impurifiers.org/my-application:0
```

The native installer owns the launcher, application description and optional
closure caches under `<prefix>/share/autopackage-impurifier/apps/<name>`.
Preparation uses the host's trusted Nix executable to import data, then drops
privileges before creating the owner's roots. It does not execute package code
as root or change Nix daemon trust. Ordinary unsigned-cache imports into a
restricted daemon fail. A network artifact instead needs an available trusted
source for its Nix closure.

Install a newer generated artifact through the same native command to upgrade.
After upgrades, each participating user runs `autopackage-impurifier prune` to
release roots for replaced descriptions. After native uninstall:

```sh
package remove --user @nix-impurifiers.org/my-application:0
autopackage-impurifier prune
```

Old applications and library snapshots remain protected until pruning. State
and GC roots live outside native-owned payloads, under the user's state directory.
Preparation and launch leave the installed payload unchanged.

The SDK pins the upstream Google Code archive's `autopackage-1.4.2-x86_64.tar.bz2`
and `autopackage-devel-1.4.2.tar.bz2`; their full original archives accompany the
tools. It relocates the ELF interpreter/RPATH of the selected native CLI helpers
and the hard-coded `/bin/ls` call to the real Nix GNU ls. The original call
silently produces empty sizes/checksums in a Nix build sandbox; no checksum or
architecture checks are disabled. Configuration disables anonymous reporting
and uses native `autopackage_no_autosu=true` for user installs. Root transactions
still run when explicitly invoked as root; automatic password escalation and
GUI helpers are not covered. The `__no_fd_close=1` native manager flag can keep
headless diagnostics visible; VM checks use real PTYs and the native tty frontend.

`nix flake check -L` runs a real native VM suite: corrupted archive rejection,
file ownership and native verify, net failure, unsigned-cache rejection and
trusted offline recovery, transport replacement, application upgrade, unchanged
payload checksums, real library replacement, uninstall, pruning and Nix GC.
Coverage is per-user prefixes. Root installations, services/accounts, protected
configuration policy, remote feeds/updates, GUI frontends, automatic bootstrap,
other architectures and concurrent install/launch/prune remain separate work.
The historical compiler embeds build timestamps; byte-identical rebuilds are
not currently claimed. Native MD5 checks detect corruption, not publisher identity;
obtain artifacts through a trusted distribution channel.
