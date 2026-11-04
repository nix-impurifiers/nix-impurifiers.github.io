# r-impurifier

Distribute an already-installed R package as a native binary package archive.
Original code is MIT; R and payloads retain their own licenses.

```nix
backend.makePackage {
  packageDir = "${builtPackage}/library/example";
}
```

`backend` is `import (inputs.r-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
`packageDir` is the installed package directory, not an R source tree. The native
DESCRIPTION must include Package and Built fields, and Meta/package.rds must
exist. Metadata, namespace/lazy-load data and prepared compiled libraries are
preserved. The output contains a deterministic Package.tar.gz in R's installed
binary-package format, compatible with `R CMD INSTALL --library=...`.

Build the package with a suitable Nix R toolchain first, or supply another
prepared installed tree. This step does not rebuild it, change its dependency
policy or make arbitrary native libraries ABI-compatible. Consumers need the
appropriate R version, architecture and external libraries. No target Nix client,
database, daemon or relocation is added. CRAN publication and repository indexes
are separate concerns. This is not a Windows/macOS archive-format implementation.

`nix flake check -L` builds a real R extension, installs its binary archive with
native R in QEMU, executes compiled code, replaces it with a second revision,
executes the new code and removes the package. Removal makes loading fail and
removes the installed package tree. The fixture tests the pinned Linux R ABI;
further R versions, platforms and dependencies require explicit coverage.
