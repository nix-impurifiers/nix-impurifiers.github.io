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

Native Flatpak tests export an independent static runtime and exercise install, execution, update and uninstall without a Nix client, daemon socket, database or engine launcher in the app sandbox. Native TCE tests boot initial, upgraded and removed extension sets in Tiny Core userspace. BitBake builds native and Nix-backed layers with actual OpenEmbedded tooling before consumer VM transactions.

The Android fixture derives a lean boot ISO from pinned Android-x86 9.0-r2 by removing Chrome and Google Play services. The Android framework, package manager, certificate checks and actual app startup remain in use. This avoids unrelated browser and cloud-service startup work competing with software-emulated application tests. The fixture selects Android P’s upstream HWUI GL pipeline before UI initialization and verifies its renderer log; the default Skia GL path could block the system UI on slow emulated runners. The watchdog remains enabled.

Native Guix payloads are built by Guix's actual trivial builder and installed into real profiles, with version changes, rollback and manifest replacement. Snap uses upstream snapd and its socket activation, native revisions and retained-image policy. Swupd signs real third-party repositories and exercises native bundle updates. Bedrock imports and replaces actual strata. These manager fixtures retain their documented host tools; separate isolated-root executions establish that their prepared static payloads do not need Nix.

Native bootc layers and transactional-update trees are booted through real image deployments or Btrfs snapshots, with native upgrade or rollback and removal checks. Nix-backed variants repeat their lifecycle with private static clients and incompatible external candidates. None of these tests claims to install a bootloader or provision Nix itself.

[initramfs-tools](/initramfs-tools-impurifier/) builds images inside a producer VM and boots two revisions with upstream init. [Booster](/booster-impurifier/) uses its native generator and rescue shell to execute embedded tools. Both boot without a root disk or shared host store. [ukify](/ukify-impurifier/) boots signed UKIs under OVMF Secure Boot, reads the guest's SecureBoot variable and requires firmware rejection of a modified kernel section. Signing uses disposable test keys; production keys remain outside Nix builds.

## Further native consumers

[OCI](/oci-impurifier/) tests Skopeo, Podman and umoci with prepared native roots and embedded closures. [Apptainer](/apptainer-impurifier/) tests ordinary-user SIF execution, replacement and removal. Neither image requires a target Nix database or daemon.

[pip](/pip-impurifier/), [npm](/npm-impurifier/) and [RubyGems](/rubygems-impurifier/) perform offline native transactions and execute compiled shared libraries or interpreter extensions. Their prepared payloads must match the consumer ABI. These are interpreter/tool VMs, not claims that arbitrary nixpkgs outputs work on every operating system.

[pkg](/pkg-impurifier/) uses the actual portable FreeBSD/DragonFly package manager for target-root transactions and static execution in a Linux VM. This proves its native archive/manager lifecycle; FreeBSD kernel and executable-ABI coverage remains additional work.

[NuGet](/nuget-impurifier/) restores managed assemblies and runtime-specific native libraries, then verifies an ordinary incremental upgrade runs the new library. Its producer normalizes wrapper metadata and gives assets deterministic content-derived timestamps to prevent stale same-size native files. Reference removal makes consumer compilation fail.

[Maven](/maven-impurifier/) publishes native repository coordinates and POMs; actual Gradle resolves a transitive dependency offline, compiles and runs both versions, and rejects missing artifacts after cache removal. [Composer](/composer-impurifier/) installs local distribution ZIPs with Packagist/network access disabled, executes the native autoloader, updates, checks platform requirements and removes the package. [LuaRocks](/luarocks-impurifier/) installs binary rocks with native dependency checks, executes a compiled Lua extension, upgrades and removes it.

These prepared-artifact tests use their pinned interpreter/SDK ABIs. Further .NET runtime identifiers, Maven plugins, PHP extensions and Lua versions require explicit native coverage.
