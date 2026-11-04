# nuget-impurifier

Pack producer-prepared managed and native assets as NuGet packages. Original
code is MIT; NuGet, .NET and payloads keep their own licenses.

```nix
backend.makePackage {
  name = "Example.Library";
  version = "1.0.0";
  payload = preparedTree;
  licenseExpression = "MIT";
  dependencies."net10.0" = { "Other.Library" = "[1.0.0,2.0.0)"; };
}
```

`backend` is `import (inputs.nuget-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
The payload uses NuGet's native layout: for example `lib/net10.0/Example.dll`
and `runtimes/linux-x64/native/libexample.so`. `authors`, `description`, native
framework dependency groups and optional `licenseExpression` supply metadata.
The default omits a payload license claim. Package versions are immutable
three-component releases with an optional prerelease suffix.

Upstream `nuget pack` creates the package and OPC metadata. Normalization removes
random relationship IDs, host details and wrapper timestamps. Asset timestamps
are deterministic functions of their contents: MSBuild can otherwise retain an
old same-size native library during an ordinary incremental upgrade. Signing
must happen after normalization, outside Nix. Feed publication, credentials and
package trust policy remain consumer operations.

Consumers restore through a local feed with `dotnet restore` or another NuGet
client. The payload must already match its declared target framework and runtime
identifier; this backend does not compile, relocate or install a Nix runtime.
It does not require NixOS or a particular libc.

`nix flake check -L` compares two independent native package builds for
reproducibility, and uses native .NET in QEMU to restore two package versions,
compile a consumer, resolve and execute an actual RID-specific native shared
library, and verify an ordinary rebuild runs the updated library. Removing the
PackageReference makes the consumer fail to compile. This tests Linux x64 and
.NET 10; other runtime identifiers, Windows and signing require separate tests.
NuGet's package cache follows its normal retention policy after reference removal.
