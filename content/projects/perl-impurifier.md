# perl-impurifier

Create installable Perl distributions from prepared modules and XS libraries.
Original code is MIT; Perl and payloads retain their own licenses.

```nix
backend.makeDistribution {
  name = "Example::Library";
  version = "1.00";
  payload = preparedTree;
  modules = {
    "Library.pm" = "Example/Library.pm";
    "Library.so" = "auto/Example/Library/Library.so";
  };
  dependencies = { XSLoader = "0"; };
}
```

`backend` is `import (inputs.perl-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
Module maps take relative payload files to relative Perl archlib destinations.
Pure Perl modules can use the same mechanism without shared libraries. `abstract`
and `author` supply metadata. A generated ExtUtils::MakeMaker Makefile.PL installs
these prepared files and records native ownership; it does not compile XS or run
payload build hooks. Native prerequisite versions pass through dependencies.
Archive timestamps and ownership are normalized.

Consumers use cpanm or compatible MakeMaker distribution tooling. The artifact
is a prepared distribution, not a promise that CPAN can rebuild its original
source. Compiled XS must match the consumer Perl ABI and architecture. Declare
external dependencies and supply compatible files; this backend does not relocate
libraries, infer ABI compatibility or add a target Nix runtime. Registry upload,
source provenance and release-signing policy remain producer concerns.

`nix flake check -L` builds an actual XS extension with Nix, then uses native
cpanm/MakeMaker in QEMU to install from a local archive without a consumer compiler
or remote mirror. It executes the extension, upgrades, executes its replacement
and uninstalls through cpanm's native packlist handling. Loading then fails and
the shared object is gone. Coverage is the pinned Perl ABI on Linux.
