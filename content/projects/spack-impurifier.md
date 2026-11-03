# spack-impurifier

Emit native Spack repositories whose installed applications run from Nix. Original
code is MIT licensed. Spack owns installation prefixes and its native database;
Nix owns the application closure. This backend targets per-user Linux installs.

```nix
let
  backend = inputs.spack-impurifier.lib.spack-impurifier { inherit pkgs; };
in backend.makePackage { pkg = pkgs.ripgrep; }
```

`makePackage` returns `net` and `offline` repositories. Use
`makeCollection [ repository1 repository2 ]` to combine different applications or
versions into one native repository. Choose one transport per application version;
conflicting archives are rejected. Add the selected output's
`spack_repo/impurifiers` directory with `spack repo add`, then install the package
normally. The command defaults to `pkg.meta.mainProgram`, falling back to
`pkg.pname`; `name` and `program` may be supplied explicitly. `archiveURL` permits
publishing the source archive at an HTTP URL. Keep local repository outputs
available until Spack has fetched their source archives.

Recipes declare native runtime dependencies `nix@2:` and `python@3.8:`.
`nixDependency` and `pythonDependency` customize these constraints. Configure real
host installations as Spack externals or supply compatible packages. Native Nix
provisioning is deferred; this backend does not install or configure a Nix daemon.

The launcher realizes the application and registers the prefix-owned `nix-root`
symlink as an indirect Nix GC root. Native removal deletes that link, allowing
collection. Native manifest verification continues to cover the installed files.
Network packages require the selected application to be available through the
host's configured Nix providers.

Offline packages carry a file binary cache. An unprivileged user cannot bypass a
Nix daemon's signature policy. With the trusted helper installed, explicitly run:

```
sudo spack-impurifier prepare /path/to/spack/prefix/share/spack-impurifier
```

Preparation verifies native installed-file metadata before importing the closure,
then registers the lasting root as the prefix owner. It executes no application
code as root. Launch failures can be retried without rebuilding the native package.

Optional `hardware` uses the shared impurifier library-capture contract. Each
launch captures and roots a fresh immutable host-library snapshot. Run
`spack-impurifier prune` as the application user after removing native prefixes to
release snapshots belonging to missing installations.

This backend does not activate a global profile, system services, or host accounts.
See [development notes](docs/development/index.md) for verification and limits.
