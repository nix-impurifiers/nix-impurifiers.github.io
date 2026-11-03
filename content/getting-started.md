# Getting started

Choose the impurifier for your **package manager**. A distribution matters when choosing native dependencies and host integration, but it does not need its own impurifier.

The quick example below produces a native DEB containing a Nix-built `hello`. Other backends have their own constructors and installation semantics; start with the [directory](/#impurifiers) to find yours.

## Before you begin

You need a working Nix installation and the native runtime dependencies described by your adapter. For dpkg, the runtime also requires Python 3. Native Nix provisioning is a future installer project; the impurifiers do not currently install Nix for you.

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
