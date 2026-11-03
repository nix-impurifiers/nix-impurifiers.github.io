# pkg-impurifier

Produce native packages with the upstream FreeBSD/DragonFly `pkg` tool. This
manager and archive format are distinct from pkgsrc's pkg_* tools. Original
code is MIT; upstream pkg and payloads retain their licenses.

`makePackage { name; version; payload; abi; }` takes a prepared prefix tree and
an explicit consumer ABI such as `FreeBSD:15:amd64`. `prefix` defaults to
`/usr/local`; `origin`, `description` and native `dependencies` are configurable.
Dependencies map names to pkg's `{ origin; version; }` records. Upstream pkg
creates the manifest, archive and checksums from the staged files. No Nix
runtime, database, daemon, activation or relocation is added.

The current VM runs unmodified portable pkg on Linux and tests target-root
installation, compiled static execution without `/nix`, checksum verification,
version replacement and removal. It does not claim a FreeBSD kernel boot or
validation of FreeBSD-native executable payloads. Producers must supply the
right native ABI and dependency metadata; those platform cases remain explicit
additional coverage.
