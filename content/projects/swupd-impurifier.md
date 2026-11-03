# swupd impurifier

Build native third-party swupd repositories whose exported commands run Nix
application closures. Original adapter code is MIT; bundled upstream software
retains its own licenses and notices.

```nix
let
  adapter = import (swupdImpurifier + "/nix") {
    inherit pkgs;
    coreSrc = impurifier;
  };
  application = adapter.makeOfflineBundle { pkg = myApplication; };
in adapter.makeRepository {
  version = 10;
  bundles = [ application ];
}
```

`pkg` must provide `pname`, `version`, and `bin/<program>`. Set `program` when
it differs from `pname`. `makeNetBundle` omits closure caches; `makePackage`
returns both `net` and `offline`. Optional `hardware` uses the shared impurifier
hardware manifest to capture host libraries at launch. Nix must already be
installed and its daemon available. Providing Nix through an impure package
remains deferred installer work.

Repository production runs the actual mixer-tools manifest/hash/fullfile
implementation as root inside an isolated QEMU VM, because native hashes
include ownership metadata. This deliberately requires Linux VM support rather
than synthesizing root ownership. Pass the previous repository as `previous`
and increase `version` to preserve native file versions and deletion records.
Format 40 fullfiles are supported; delta packs and format transitions are not
implemented.

Copy the output to a writable publication directory, then sign it outside the
Nix build:

```sh
cp -r result repository
chmod -R u+w repository
swupd-impurifier sign repository --key signing-key.pem --certificate signing-cert.pem
```

Keep the private key outside the Nix store. Signing creates native detached
CMS signatures, manifest archives and the signed latest-version pointer.
Distribute the public certificate through your own trusted channel. With your
actual repository URL and certificate, native installation is:

```sh
swupd 3rd-party add applications https://example.org/repository \
  --versionurl=https://example.org/repository \
  --contenturl=https://example.org/repository --format=40 --certpath=/trusted/cert.pem
swupd 3rd-party bundle-add my-application --repo=applications \
  --versionurl=https://example.org/repository \
  --contenturl=https://example.org/repository --format=40 --certpath=/trusted/cert.pem
sudo swupd-impurifier prepare --owner "$USER" applications my-application
/opt/3rd-party/bin/my-application
```

Use the same URL, format and certificate options for subsequent native commands.
The VM tests use local signed repositories with all native signature and hash
checks enabled. Remote publication itself is not tested. Native `add` may leave a repository
registration after rejecting its manifest; native `swupd 3rd-party remove
--force NAME` removes that incomplete registration (and can report partial
cleanup). Resolve it before later updates, whose wrapper regeneration visits
all registered repositories.

Preparation explicitly imports closure data from an offline bundle, using a
trusted host Nix executable, then drops privileges before creating the owner's
GC roots. It does not execute bundle code as root or change daemon trust.
Ordinary users cannot import an unsigned cache into a restricted daemon.
Network bundles instead require an available, trusted source for their closure.

swupd installs third-party bundles under `/opt/3rd-party/bundles/<repository>`
and exports executables under `/opt/3rd-party/bin`. Its native third-party path
intentionally disables package scripts. This adapter therefore provides
per-user application launch, rather than system service/account hooks.
After updating or removing bundles, each participating user runs:

```sh
swupd-impurifier prune
```

This releases roots belonging to removed/replaced application descriptions.
Old applications and library snapshots remain protected until pruning; this
also avoids tying an executing application to a mutable repository prefix.
Native swupd owns installed payload files; preparation and launch leave them
unchanged. Concurrent native updates and launches are not a tested guarantee.

The SDK pins swupd-client 7.0.0, mixer-tools 6.4.0 and Clear Linux bsdiff 1.0.6.
Two disclosed client fixes retain native checks: the SHA digest formatting loop
uses the remaining buffer length (required by modern fortified libc), and
third-party repository initialization returns failure when setting its prefix
fails. The latter prevents an invalid prefix from falling back to the host
root. Upstream source/license archives accompany the SDK and publisher.

`nix flake check -L` runs real publisher and consumer VMs: native signed
installation, rejected signatures and invalid prefixes, command export,
network failure, unsigned-cache rejection, trusted offline recovery,
versioned updates, host-library replacement, removal, pruning and Nix GC.
Tests run on x86_64 Linux using actual native clients and databases. A complete
Clear Linux boot image and other architectures remain separate coverage.
