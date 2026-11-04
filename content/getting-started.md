# Getting started

Choose the impurifier for your **native consumer**: a package manager, language ecosystem, image runtime or boot tool. A distribution matters when choosing dependencies and host integration, but it does not need its own impurifier.

Each project has an overview, a full guide and a documentation matrix. Use the [comparison](/compare/) to distinguish mode-dependent Nix integration from artifacts that add no target Nix runtime. Prepared payloads still need the right native libraries and ABI.

The quick example below produces a native DEB containing a Nix-built `hello`. Other backends have their own constructors and installation semantics; start with the [directory](/#impurifiers) to find yours.

## Before you begin

The build machine needs Nix. Target requirements depend on the payload mode: native-owned payloads can run without Nix, while Nix-backed packages need a usable client and store. Selected adapters can bundle a supplied static client and prefer a compatible external one. The Nix-backed dpkg runtime also requires Python 3. Complete Nix provisioning through an impure package remains deferred installer work.

An external Nix installation must be represented accurately in the native package database when another package depends on it. The adapter lets you select that dependency; it does not invent a provider.

## Declare an application

This example targets `x86_64-linux`. Save it as `flake.nix` in a project directory:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    dpkg-impurifier.url = "github:nix-impurifiers/dpkg-impurifier";
  };

  outputs = { nixpkgs, dpkg-impurifier, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      adapter = dpkg-impurifier.lib.dpkg-impurifier {
        inherit pkgs;
      };
    in {
      packages.${system} = {
        hello-offline = adapter.makeOfflineDeb {
          pkg = pkgs.hello;
        };
        runtime = adapter.makeRuntimeDeb {
          nixDependency = "nix-bin | nix-external-runtime";
        };
      };
    };
}
```

Select a Nix provider expression that matches your system. `nix-bin` is one possible native package; `nix-external-runtime` must be a real provider package if you use it.

## Build native packages

```sh
nix build .#runtime --out-link result-runtime
nix build .#hello-offline --out-link result-application
```

Nix builds the application closure and packages it for the native manager. The target does not rebuild the application during installation.

## Install through your package manager

On a compatible dpkg/APT system with the prerequisites satisfied:

```sh
sudo apt install \
  "$(readlink -f result-runtime)" \
  "$(readlink -f result-application)"

/opt/nix/profile/bin/hello
```

The native packages own installation intent and host files. The shared engine projects the installed application into a Nix profile and retains the necessary GC roots.

To remove the application:

```sh
sudo apt remove hello-offline
```

See the [dpkg guide](/dpkg-impurifier/) for upgrades, protected configuration, services, trust and generation pruning.

## Choose net or offline

A **net** artifact carries the application descriptor and integration. Installation resolves the closure through the host's configured Nix substituters.

An **offline** artifact carries a local closure cache. The import uses that cache with remote substitution and builders disabled. The native package or repository authenticates that payload; NAR hashes still verify its contents.

Offline artifacts are larger and still require a working Nix runtime. Neither flavor silently changes global Nix cache trust. Read your adapter's documentation for transport replacement rules: native managers differ in how they treat same-version artifacts.

## Know the transaction boundary

A native package transaction and Nix profile activation are separate operations. A failed fetch or profile composition can leave the native package installed while retaining the previous profile. Fix the reported cause and follow the adapter's recovery procedure.

Support for services, configuration, accounts, drivers, rollback and image deployment varies by adapter. The [VM coverage guide](/testing/) explains how to read those limits.

## Native payloads without target-side Nix

Choose the payload contract that matches the consumer. These modes omit Nix activation and target-side Nix database requirements; their native managers retain their own requirements.

| Payload contract | Adapters |
| --- | --- |
| Complete closures at their original store paths, split into native-owned objects with exact dependencies | dpkg, RPM, ALPM, APK, XBPS, opkg |
| Prepared filesystem trees with native dependency and configuration policies | ipkg, pkgtools, pkgutils, KISS, CPT, eopkg, PiSi, pkgsrc, PETget, Entropy |
| Prepared prefix or output trees | Conda, Spack, Homebrew, MacPorts, Autopackage, Guix |
| Native source-builder recipes carrying prepared files | Portage, pkgcore, Paludis, Sorcery, Lunar, BitBake/OpenEmbedded |
| Native application bundles with their own runtime contracts | AppImage, Flatpak, Snap, Zero Install |
| Native extensions, third-party bundles or strata | TCE, systemd-sysext, swupd, Bedrock |
| Prepared native image layers, RPM layers or snapshot trees | bootc, rpm-ostree, transactional-update |
| Early userspace modules and hooks | dracut, mkinitcpio |

For example, `adapter.makeNativeDebs { pkg = pkgs.hello; }` produces DEBs with exact native dependencies between closure objects. The native manager owns those store files. Keep this ownership separate from a Nix-managed store and its garbage collection.

For prepared trees, the producer supplies files that already work with the target ABI, prefix and runtime. This is not automatic relocation. Flatpak requires an explicit native runtime reference; Guix retains its own store and daemon; image adapters retain native deployment policy. Each project guide names its constructor and tested platforms.

Nix's own impurifier uses native Nix profiles, which necessarily retain a Nix store, database and client. Use the adapter for another native manager when that manager should own Nix-free files.

## Supply a bundled Nix client

Nix-backed adapters can accept a producer-supplied static client through `bundledNixStore` and upstream notices through `bundledNixNotices`. Depending on the adapter, these belong on its runtime package or application constructor. Launch prefers a compatible external client, then the bundle. Explicit `IMPURIFIER_NIX_STORE` disables fallback.

A client is not a Nix installation: the store, daemon or other documented infrastructure must already exist. Trusted preparation helpers use host tools and never execute an application-owned bundled client as root. Read the selected adapter's guide for its preparation and trust boundary.

## Android and Termux are separate ecosystems

[android-impurifier](/android-impurifier/) assembles native APKs from Android-compatible DEX, resources, assets and ABI-specific libraries. Sign the unsigned output outside Nix with your own key, then install through Android’s native tools.

[termux-impurifier](/termux-impurifier/) builds DEBs for Termux’s private prefix and Android ABI. Supply an already-compatible native tree; ordinary Debian/Linux binaries and global-store layouts are separate contracts. Both targets work without a target-side Nix installation.

