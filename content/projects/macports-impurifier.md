# macports-impurifier

Emit native MacPorts recipes backed by Nix applications. Original code is MIT
licensed. The verified target is Linux x86_64 with MacPorts' `/opt/local` prefix.
MacPorts owns source checksums, installed images, active files, dependencies,
revision upgrades, deactivation and removal. Nix owns application closures.

```nix
let backend = inputs.macports-impurifier.lib.macports-impurifier { inherit pkgs; };
in backend.makeRepository [
  (backend.makeRuntimePort {})
  (backend.makeOfflinePort { pkg = pkgs.ripgrep; })
]
```

The output contains `sysutils/<name>/Portfile` and `archives` directories. Copy it
to a writable repository checkout, then run
native `portindex` in the repository, add its URL to `sources.conf`, and install
normally with `port install`. For local use, keep the source output available
until MacPorts has fetched its archives. `archiveURL` selects a published source
archive URL. Index generation and remote hosting remain native MacPorts tasks.

`makePort`, `makeNetPort` and `makeOfflinePort` accept `pkg`, optional `name`,
`version`, `revision`, `program`, `priority`, `users`, `directories`, `lifecycle`, `hardware`,
and `archiveURL`. `program` defaults to `meta.mainProgram` or `pname`. The selected
command is exported under `/opt/local/bin`, pointing into `/opt/nix/profile`.
Additional commands remain available directly from the shared Nix profile.
Native file conflicts still apply to command exports.

`makePackage` returns `net` and `offline` recipe outputs. Select one recipe per
port in a repository. Net uses revision 0 and offline revision 1; native upgrades
can replace a net revision with offline. MacPorts keeps inactive installed images
for explicit reactivation or uninstall. Bump `revision` when changing package
content without changing the application version. When several revisions are installed,
use native version selectors such as `port uninstall name@version_revision`.

The runtime port defaults to native binary dependencies `bin:nix-store:nix` and
`bin:python3:python314`. Existing compatible host commands satisfy these; otherwise
MacPorts resolves their provider ports. Override `makeRuntimePort.dependencies`
with real provider ports, including your own. Users/directories additionally
require native systemd-sysusers/tmpfiles tools. Nix provisioning and daemon
installation are explicitly deferred, not excluded.

Root activation imports an offline closure or realizes through the host's Nix
providers, roots a new profile generation, then runs declared host actions. Runtime compatibility is checked by the recipe and again before profile
publication. Use `macports-impurifier install`, `upgrade`, `activate`, `deactivate`
or `uninstall` when you need a final reconciliation exit status: native MacPorts
can report successful image activation despite a failed callback, and can fall
back to file activation after a stored Portfile hook fails. The adapter prevents
an incompatible runtime from publishing a new profile through those paths. Failed realization preserves
the previous profile. A lifecycle hook can fail after the new profile is published;
the native port remains active with pending work. Correct the cause and run:

```
sudo /opt/local/bin/macports-impurifier reconcile
```

The same command refreshes immutable host-driver snapshots after a driver update.
Native deactivation/removal reconciles active manifests. Upgrade-time deactivation
waits for activation so installation history is preserved. Old generations retain
roots until explicitly pruned:

```
sudo /opt/local/bin/macports-impurifier prune --keep 0
```

Services, config-file policy, macOS, other prefixes/architectures and remote binary
archives are not claimed. See [development notes](docs/development/index.md) for
native SDK compatibility details and VM coverage.

`makeNativePort { payload; name; version; ... }` accepts a producer-prepared
prefix tree. It emits a native port without impurifier activation hooks, Nix
requirements or the Nix-backed adapter's `/opt/local` prefix guard. Defaults are
`platforms = [ "any" ]` and `architectures = [ "noarch" ]`; producers must set
accurate restrictions for compiled payloads. The producer owns ABI and prefix
compatibility; the adapter does not relocate binaries.

`makeRuntimePort` optionally accepts a static `bundledNixStore` and upstream
`bundledNixNotices`. Without explicit dependency overrides, bundling omits the
external Nix dependency and retains Python. A compatible external client takes
precedence; failures after selection do not trigger retries against another
client or store. Bundling is not Nix provisioning.
