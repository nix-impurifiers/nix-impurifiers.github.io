# Tested through native transactions

An archive that builds successfully is only the beginning. Impurifier checks run native package managers and supporting tools inside QEMU VMs, with actual native tools and package databases. Nix-backed modes use real Nix stores; native payload modes also test operation without target-side Nix.

Each project's README describes the contract its tests exercise and the parts that still need coverage. A passing VM does not imply every distribution, architecture, init system or hardware combination is supported.

## What the tests look for

- **Native ownership and dependency policy.** Packages must enter the actual package database, with meaningful provider requirements and native metadata.
- **Failure and recovery.** Tests remove network access or substitution paths, inspect failed activation, and recover using a genuinely carried offline closure.
- **Updates and removal.** Native tools perform version changes, transport replacements and removals. Tests inspect the resulting profile and protected configuration where supported.
- **GC retention and release.** Installed applications must remain usable after Nix garbage collection. Removal and pruning must release closures when no retained generation needs them.
- **Trust boundaries.** Signed repository suites exercise native verification and reject unsigned or modified inputs. An unsigned local-artifact test is documented as such.
- **Host integration.** Adapters that expose services or accounts test their lifecycle and administrator intent with the actual supporting tools.

## Package-manager families

The [dpkg suite](/dpkg-impurifier/) includes APT, apt-get, Aptitude, Nala, GDebi and Synaptic. Its native userspace tests cover signed indexes, updates, configuration and removal.

The [RPM suite](/rpm-impurifier/) covers RPM, DNF 4 and 5, modern and historical yum, Zypper, microdnf, tdnf, ALT APT-RPM, urpmi and Poldek. Older frontends require documented format and dependency choices.

The [ALPM suite](/pacman-impurifier/) exercises pacman, makepkg and its tested helper frontends, including genuine recipe builds. The [Slackware suite](/pkgtools-impurifier/) exercises pkgtools, slackpkg, slapt-get, sbopkg and Netpkg.

[APK](/apk-impurifier/) tests both APK 2 and APK 3 against signed repositories. [opkg](/opkg-impurifier/) tests upstream opkg and the native OpenWrt fork. [XBPS](/xbps-impurifier/) tests native package transactions and real xbps-src template builds.

## Images and source builders

Image and functional managers have different activation models. [rpm-ostree](/rpm-ostree-impurifier/), [bootc](/bootc-impurifier/) and [transactional-update](/transactional-update-impurifier/) include native deployment or snapshot operations and reboot/rollback checks.

[BitBake](/bitbake-impurifier/) tests emitted layers and recipes with actual OpenEmbedded classes, including first-boot postinstall deferral. It is a BitBake/OpenEmbedded target; Yocto is the surrounding project ecosystem.

Other adapters document their own native build, profile, feed, bundle or activation tests. Browse the [complete directory](/#impurifiers) for their details.

## Run a project's checks

For example:

```sh
nix flake check github:nix-impurifiers/dpkg-impurifier -L
```

VM checks can be substantial builds. Their fixtures may boot NixOS while running a pinned native userspace and package manager inside it. That is disclosed in the project documentation; it is not a claim to test a complete distribution boot.

## Remaining work

Native Nix provisioning through an impure package is explicitly deferred. So are the additional platform and integration cases called out by individual adapters: for example, full OpenWrt/procd boot, router hardware, complete desktop stacks and further architectures.

The implemented adapters remain useful within their documented contracts. Read those contracts before choosing one for a deployment.

## Native payloads and early userspace

DEB, RPM, ALPM and APK target-root VMs install native-owned closure objects, upgrade applications, retain shared dependencies, detect altered files and clean up through native tools without a target Nix client, daemon or database. Native prefix tests for Conda, Spack, Homebrew and MacPorts run the installed payload inside chroots without `/nix`. Separate bundled-client suites exercise real static Nix fallback while preserving the native ownership and trust boundaries.

[dracut](/dracut-impurifier/) and [mkinitcpio](/mkinitcpio-impurifier/) each generate and boot initial and regenerated initramfs images under QEMU. Distinct proofs execute under the upstream init implementation before a real root is available. The guest has no root disk, mounted host store or Nix database. These tests establish the early-userspace contract rather than complete distribution boots.

## Android applications and Termux

[Android](/android-impurifier/) builds actual DEX/JNI applications, signs them with ephemeral test keys, and exercises the native Android package manager. Its software-QEMU fixture covers execution, upgrades with retained app data, rejected signer changes, rejected tampering and uninstall. Resource linking exposes generated Java resource IDs before DEX compilation; private production signing keys stay outside Nix builds.

[Termux](/termux-impurifier/) is a distinct target. Its VM installs the actual Android app and embedded bootstrap, then runs the real Termux package manager as the app UID. A compiled Android-native executable consumes a required native package. Tests cover rootless unpacking, checksums, upgrades, dependency retention, preserved private-directory modes and cleanup. Initial coverage is Android-x86 API 28, not a claim of modern stock Android or ARM coverage.
