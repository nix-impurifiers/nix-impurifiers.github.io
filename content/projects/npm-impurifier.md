# npm-impurifier

Pack prepared JavaScript trees and native Node addons using actual `npm pack`.
Original code is MIT; Node/npm and payloads keep their own licenses.

```nix
backend.makePackage { name = "my-package"; version = "1.0.0"; payload = tree; }
```

`main`, `bin`, `dependencies`, `os`, `cpu` and `license` supply native package
metadata. The generated package.json replaces any payload package.json.
Lifecycle scripts are not added or executed while packing. Consumers can install
the resulting tarball with npm or compatible package managers. Supply an already
compatible Node addon or native executable: no automatic relocation, native
compilation at install, Nix runtime or registry publication is implied.

The QEMU test installs an actual compiled N-API addon with real offline npm,
loads it with Node, upgrades, checks the dependency tree and uninstalls. Node/npm
are NixOS fixture tools; the package itself contains no Nix launcher or runtime.
Further Node versions, native ABIs and operating systems need explicit validation.
